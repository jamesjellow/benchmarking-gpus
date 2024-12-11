import sys
import boto3
import json  
import io
import pandas as pd  
import numpy as np

from sklearn.model_selection import train_test_split  
from sklearn.ensemble import RandomForestClassifier  
from sklearn.metrics import accuracy_score, mean_squared_error, confusion_matrix

from category_encoders import TargetEncoder

from botocore.exceptions import ClientError


# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb', 
    aws_access_key_id='*****', 
    aws_secret_access_key='*****', 
    region_name='us-east-1'
    )

def get_dataframe_from_table(tableName):
    data_table = dynamodb.Table(tableName)
    all_records = []

    response = data_table.scan()
    all_records.extend(response['Items'])

    while 'LastEvaluatedKey' in response:
        response = data_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        all_records.extend(response['Items'])

    return(pd.DataFrame(all_records))

def get_gpu_data():
    gpu_df = get_dataframe_from_table('gpu-data')
    gpu_df = gpu_df.drop(columns=['system_name'])
    return(gpu_df)

def get_inference_run_data():
    run_df = get_dataframe_from_table('inference_perf_run')
    return(run_df)

def run_rf(df):
    print("Running random forest model")

    X = df.drop('samples_ps', axis=1)
    y = df['samples_ps'] 

    print(X)

    encoder = TargetEncoder(X.columns)
    X_encoded = encoder.fit_transform(X, y) 
    # encoder = MeanEncoder(variables=list(X.columns), missing_values='ignore')
    # X_encoded = encoder.fit(X, y) 
    #X_encoded = pd.get_dummies(X)

    X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.4, random_state=42)  
  
    model = RandomForestClassifier(n_estimators=100, random_state=42)  
    model.fit(X_train, y_train)  

    y_pred = model.predict(X_test)

    # RMSE (Root Mean Square Error)
    rmse = float(format(np.sqrt(mean_squared_error(y_test, y_pred)), '.3f'))
    accuracy = accuracy_score(y_test, y_pred)

    importances = model.feature_importances_  
    feature_names = X_encoded.columns  
    
    feature_importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})  
    feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)  
    return rmse, accuracy, feature_importance_df


        
gpu_df = get_gpu_data()
run_df = get_inference_run_data()
run_df = run_df.join(gpu_df.set_index('accelerator_model_name'), on='accelerator_model_name')

run_df = run_df.drop(columns=['latency_m'])

#filtering out potential erroneos result
run_df['samples_ps'] = run_df['samples_ps'].astype('Int32')
run_df = run_df.query("samples_ps < 200")

rmse, accuracy, feature_importance_df = run_rf(run_df)

feature_importance_df = feature_importance_df.query("Importance > 0")

print(feature_importance_df)
    
