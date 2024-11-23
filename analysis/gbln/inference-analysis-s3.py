import boto3
import json  
import io
import pandas as pd  
import numpy as np

from sklearn.model_selection import train_test_split  
from sklearn.ensemble import RandomForestClassifier  
from sklearn.tree import DecisionTreeRegressor  
from sklearn.tree import export_graphviz
from sklearn.metrics import accuracy_score, mean_squared_error, confusion_matrix

from category_encoders import TargetEncoder

s3_client = boto3.client('s3', 
    aws_access_key_id='***********************', 
    aws_secret_access_key='****************************', 
    region_name='us-east-2'
    )

bucket_name = 'benchmarking-gpus'

guid_idx = 3
run_idx = 5
analysis_type = 'performance'

def get_hardware_info(key):
    json_file  = read_s3_file(bucket_name, key)
    hardware = json.loads(json_file)
    hardware['host_memory_capacity'] =  float(hardware['host_memory_capacity'].replace('G', ''))
    return hardware

def get_metrics_info(key):
    metrics = {}
    json_file  = read_s3_file(bucket_name, key)
    metrics_json = json.loads(json_file)
    metrics['avg_cpu_usage'] = metrics_json['cpu'][analysis_type]['cpu_all usage (%)']['mean']
    metrics['avg_gpu_usage'] = metrics_json['gpu'][analysis_type]['GPU usage (%)']['mean']
    metrics['avg_gpu_mem_usage'] = metrics_json['gpu'][analysis_type]['GPU memory usage (%)']['mean']
    metrics['avg_free_mem'] = float(metrics_json['memory'][analysis_type]['free, RAM available (KB)']['mean']) / 1024 / 1024
    return metrics


def get_results_info(key):
    results_file = read_s3_file(bucket_name, key)
    buf = io.StringIO(results_file)
    results = {}
    for line in buf:
        if 'Samples per second' in line:
            results['samples_ps'] = int(float(line.split(':')[1].strip()))

        if 'Mean latency (ns)' in line:
            results['latency_m'] = float(line.split(':')[1].strip()) / 1e+11
            break
    return results

def read_s3_file(bucket_name, file_key):
    obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    return obj.get('Body').read().decode('utf-8')

def run_dtr(df):
    print("Running decision tree regressor model")

    X = df.drop('samples_ps', axis=1)
    y = df['samples_ps'] 

    encoder = TargetEncoder(X.columns)
    X_encoded = encoder.fit_transform(X, y) 

    X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)  
  
    model = DecisionTreeRegressor(random_state = 0)  
    model.fit(X_train, y_train)  

    y_pred = model.predict(X_test)

    # RMSE (Root Mean Square Error)
    rmse = float(format(np.sqrt(mean_squared_error(y_test, y_pred)), '.3f'))
    print("\nRMSE: ", rmse)
    
    importances = model.feature_importances_  
    feature_names = X_encoded.columns  
    
    feature_importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})  
    feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)  
    return feature_importance_df

def run_rf(df):
    print("Running random forest model")

    X = df.drop('samples_ps', axis=1)
    y = df['samples_ps'] 

    encoder = TargetEncoder(X.columns)
    X_encoded = encoder.fit_transform(X, y) 

    X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.4, random_state=42)  
  
    model = RandomForestClassifier(n_estimators=100, random_state=42)  
    model.fit(X_train, y_train)  

    individual_tree = model.estimators_[0]

    y_pred = model.predict(X_test)

    # RMSE (Root Mean Square Error)
    rmse = float(format(np.sqrt(mean_squared_error(y_test, y_pred)), '.3f'))
    print("\nRMSE: ", rmse)
    
    print(accuracy_score(y_test, y_pred))

    print(confusion_matrix(y_test, y_pred))

    # export_graphviz(individual_tree, out_file='individual_tree.dot',
    #             feature_names=X_encoded.columns,
    #             class_names=y.astype('str'),
    #             rounded=True, filled=True)

    #print(classification_report(y_test, y_pred))

    importances = model.feature_importances_  
    feature_names = X_encoded.columns  
    
    feature_importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})  
    feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)  
    return feature_importance_df


hardware_data = []
metrics_data = []
results_data = []

paginator = s3_client.get_paginator('list_objects_v2')
pages = paginator.paginate(Bucket=bucket_name)

print("Loading Data")
for page in pages:
    for obj in page['Contents']:
        path = obj['Key'].split('/')
        row_key = f'{path[guid_idx]}_{path[run_idx]}'

        if 'reference-gpu-onnxruntime' in obj['Key'] and 'systems' in obj['Key']:
            hardware_info = get_hardware_info(obj['Key'])
            hardware_info['row_key'] = row_key
            hardware_data.append(hardware_info)

        if 'mlperf_log_summary.txt' in obj['Key'] and analysis_type in obj['Key']:
            result_info = get_results_info(obj['Key'])
            result_info['row_key'] = row_key
            results_data.append(result_info)

        if 'metrics_summary.json' in obj['Key']:
            metrics_info = get_metrics_info(obj['Key'])
            metrics_info['row_key'] = row_key
            metrics_data.append(metrics_info)


hardware_df = pd.DataFrame(hardware_data)
metrics_df = pd.DataFrame(metrics_data)
results_df = pd.DataFrame(results_data)

metrics_df.to_csv('results/profile-metrics.csv')
results_df.to_csv('results/inference-results.csv')
hardware_df.to_csv('results/hardware-data.csv')

gpu_df = pd.read_csv('gpu-data.csv')  
gpu_df = gpu_df.drop(columns=['accelerator_model_name'])

#hardware_df = hardware_df.join(gpu_df.set_index('system_name'), on='system_name')
hardware_df = hardware_df.drop(columns=['host_processors_per_node', 'host_storage_type', 'submitter', 'division', 'submitter', 'division', 'status', 'number_of_nodes', 'host_processor_frequency', 'host_processor_caches', 'host_processor_interconnect', 'host_storage_capacity', 'host_networking', 'host_networking_topology', 'host_memory_configuration', 'accelerator_host_interconnect', 'accelerator_frequency', 'accelerator_on-chip_memories', 'accelerator_interconnect_topology', 'cooling', 'hw_notes', 'other_software_stack', 'sw_notes', 'host_network_card_count', 'accelerator_interconnect', 'accelerator_memory_configuration', 'accelerators_per_node', 'framework', 'system_name', 'system_type', 'system_type_detail'])

analysis_df = metrics_df.join(hardware_df.set_index('row_key'), on='row_key')
analysis_df = analysis_df.join(results_df.set_index('row_key'), on='row_key')

analysis_df['avg_mem_usage'] = 1 - (analysis_df['avg_free_mem'] / analysis_df['host_memory_capacity'])

analysis_df = analysis_df.drop(columns=['row_key', 'avg_free_mem'])

#filtering out potential erroneos result
analysis_df = analysis_df.query("samples_ps < 200")


importance_df = run_rf(analysis_df)
importance_df.to_csv('results/training-importance.csv')

sps = analysis_df['samples_ps']
print(sps.describe())

analysis_df.to_csv('results/training-set.csv')