import os  
import json  
import pandas as pd  

from sklearn.model_selection import train_test_split  
from sklearn.ensemble import RandomForestClassifier  
from sklearn.metrics import accuracy_score, classification_report  

from category_encoders import OneHotEncoder  #we could look into tweaking this

data_dir = 'training_results_v4.0'
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
                            data.append(content)  
                    except Exception as e:  
                        print(f"Error reading {file_path}: {e}")  
  
    df = pd.DataFrame(data)  
    return df  

def traverse_results(root_dir):  
    print("Gathering results data")
    data = []  

    for dirpath, dirnames, filenames in os.walk(root_dir):  
        if '\\results\\' in dirpath:
            for file in filenames:  
                if file.endswith('.txt'):  
                    result_file = {}
                    file_path = os.path.join(dirpath, file)
                    accuracy, training_ms = parse_results(file_path)
                    dir_path = dirpath.split('\\')
                    result_file['system'] = dir_path[3]
                    result_file['model'] = dir_path[4]
                    result_file['accuracy'] = accuracy
                    result_file['training_ms'] = training_ms
                    data.append(result_file)
    
    df = pd.DataFrame(data)  
    return df  

def parse_results(file_path):
    accuracy = 0
    training_ms = 0
    initial_ms = 0
    try:  
        with open(file_path, 'r', errors="ignore") as log_file:  
            for line in log_file:
                if ':::MLLOG' in line:
                    json_line =  '{' + line.partition('{')[2]
                    log_entry = json.loads(json_line)  
                    if log_entry['event_type'] == 'INTERVAL_START' and initial_ms == 0:
                        initial_ms = log_entry['time_ms']
                    if log_entry['event_type'] == 'INTERVAL_END' and log_entry['key'] == 'eval_stop':
                        training_ms = log_entry['time_ms'] - initial_ms
                    if log_entry['event_type'] == 'POINT_IN_TIME' and log_entry['key'] == 'eval_accuracy':
                        accuracy = log_entry['value']
    except Exception as e:  
        print(f"Error reading {file_path}: {e}")  

    return accuracy, training_ms

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

df = cleanse_data_set(systems_df, results_df)
importance_df = run_rf(df)

df.to_csv('training_sytems_data.csv')
importance_df.to_csv('training_importance.csv')

print(importance_df)  