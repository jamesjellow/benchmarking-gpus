import os  
import json  
import pandas as pd  
pd.options.mode.chained_assignment = None

from sklearn.model_selection import train_test_split  
from sklearn.ensemble import RandomForestClassifier  
from sklearn.metrics import accuracy_score, classification_report  

from category_encoders import OneHotEncoder  #we could look into tweaking this

data_dir = '../../../inference_results_v4.1'
model_to_eval = 'resnet50'

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
                            content['system'] = file.split('.')[0]
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

    systems_df = systems_df.drop(columns=['accelerator_frequency', 'accelerator_interconnect_topology', 'accelerator_on-chip_memories', 'boot_firmware_version', 'cooling', 'disk_controllers', 'disk_drives', 'division', 'filesystem', 'host_memory_configuration', 'host_network_card_count', 'host_networking', 'host_networking_topology', 'host_processor_caches', 'host_processor_frequency', 'host_processor_interconnect', 'host_storage_capacity', 'hw_notes', 'management_firmware_version', 'network_speed_mbit', 'nics_enabled_connected', 'nics_enabled_firmware', 'nics_enabled_os', 'number_of_nodes', 'number_of_type_nics_installed', 'other_hardware', 'power_management', 'power_supply_details', 'power_supply_quantity_and_rating_watts', 'status', 'submitter', 'sw_notes', 'system_name', 'system_type_detail', 'host_processor_vcpu_count', 'host_processor_url', 'implementation', 'device', 'run_config', 'system_type'])
    systems_df = systems_df.query("accelerator_model_name != 'N/A'")
    
    systems_df.loc[systems_df.accelerator_host_interconnect == "N/A", "accelerator_host_interconnect"] = ''
    systems_df.loc[systems_df.accelerator_interconnect == "N/A", "accelerator_interconnect"] = ''
    systems_df.loc[systems_df.accelerator_interconnect == "N/a", "accelerator_interconnect"] = ''

    joined_df = systems_df.join(results_df.set_index('system'), on='system')

    joined_df = joined_df.query(f"division == 'Server' & model == 'resnet50'")

    joined_df['latency_ns'] = joined_df['latency_ns'].astype('Int32')

    joined_df = joined_df.drop(columns=['system', 'model', 'division'])

    return joined_df


def run_rf(df):
    print("Running random forest model")
    X = df.drop('latency_ns', axis=1)
    y = df['latency_ns'] 
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

cleaned_df = cleanse_data_set(systems_df, results_df)
importance_df = run_rf(cleaned_df)

systems_df.to_csv('results/inference-sytems-data.csv')
importance_df.to_csv('results/inference-importance.csv')

# print(importance_df)  