import os  
import json  
import pandas as pd  

from sklearn.model_selection import train_test_split  
from sklearn.ensemble import RandomForestClassifier  
from sklearn.metrics import accuracy_score, classification_report  

from category_encoders import OneHotEncoder  #we could look into tweaking this

data_dir = '../../../inference_results_v4.1'
model_to_eval = 'unet3d'

def traverse_systems(root_dir):  
    print("Gathering systems data")
    data = []  
  
    for dirpath, dirnames, filenames in os.walk(root_dir):  
        if os.path.basename(dirpath) == 'systems':  
            for file in filenames:  
                if file.endswith('.json'):  
                    file_path = os.path.join(dirpath, file)  
                    try:  
                        with open(file_path, 'r') as json_file:  
                            content = json.load(json_file)
                            content['system_name'] = file.split('.')[0]
                            data.append(content)  
                    except Exception as e:  
                        print(f"Error reading {file_path}: {e}")  
  
    df = pd.DataFrame(data)  
    return df  

def traverse_results(root_dir):  
    print("Gathering results data")
    data = []  

    for dirpath, dirnames, filenames in os.walk(root_dir):  
        if '\\performance\\' in dirpath:
            for file in filenames:  
                if file == 'mlperf_log_summary.txt':  
                    result_file = {}
                    file_path = os.path.join(dirpath, file)
                    latency_ns = parse_results(file_path)
                    dir_path = dirpath.split('\\')
                    result_file['system'] = dir_path[4]
                    result_file['model'] = dir_path[5]
                    result_file['division'] = dir_path[6]
                    result_file['latency_ns'] = latency_ns
                    data.append(result_file)
    
    df = pd.DataFrame(data)  
    return df  

def parse_results(file_path):
    latency_ns = 0

    try:  
        with open(file_path, 'r', errors="ignore") as log_file:  
            for line in log_file:
                if 'Mean latency (ns)' in line:
                    latency_ns = line.split(':')[1].strip()
                    break
                    
    except Exception as e:  
        print(f"Error reading {file_path}: {e}")  

    return latency_ns

def cleanse_data_set(systems_df, results_df):
    print("Cleaning and combining data")
    systems_df['number_of_nodes'] = systems_df['number_of_nodes'].astype('Int32')
    systems_df = systems_df.query('number_of_nodes == 1')
    systems_df = systems_df.drop(columns=['submitter', 'division', 'submitter', 'division', 'status', 'number_of_nodes', 'host_processor_vcpu_count', 'host_processor_frequency', 'host_processor_caches', 'host_processor_interconnect', 'host_storage_capacity', 'host_networking', 'host_networking_topology', 'host_memory_configuration', 'accelerator_host_interconnect', 'accelerator_frequency', 'accelerator_on-chip_memories', 'accelerator_interconnect_topology', 'cooling', 'hw_notes', 'other_software_stack', 'sw_notes', 'hardware', 'host_network_card_count', 'framework_name'])
    
    joined_df = systems_df.join(results_df.set_index('system'), on='system_name')
    joined_df = joined_df.query(f"training_ms > 1 & model == '{model_to_eval}' ")

    joined_df = joined_df.drop(columns=['system_name', 'model', 'accuracy'])

    return joined_df


def run_rf(df):
    print("Running random forest model")
    X = df.drop('training_ms', axis=1)
    y = df['training_ms'] 
    encoder = OneHotEncoder(drop_invariant=True) 
    #X_encoded = encoder.fit_transform(X) 
    X_encoded = pd.get_dummies(X, drop_first=True)  

    X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)  
  
    model = RandomForestClassifier(n_estimators=100, random_state=42)  
    model.fit(X_train, y_train)  
    
    importances = model.feature_importances_  
    feature_names = X_encoded.columns  
    
    feature_importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})  
    feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)  
    return feature_importance_df

systems_df = traverse_systems(data_dir)  
results_df = traverse_results(data_dir)  

# df = cleanse_data_set(systems_df, results_df)
# importance_df = run_rf(df)

systems_df.to_csv('results/inference-sytems-data.csv')
results_df.to_csv('inference-importance.csv')

# print(importance_df)  