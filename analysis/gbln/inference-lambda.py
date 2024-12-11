import boto3
import json  
import uuid
import pandas as pd  
import numpy as np

from sklearn.model_selection import train_test_split  
from sklearn.ensemble import RandomForestClassifier  
from sklearn.tree import DecisionTreeRegressor  
from sklearn.tree import export_graphviz
from sklearn.metrics import accuracy_score, mean_squared_error, confusion_matrix

from category_encoders import TargetEncoder

from botocore.exceptions import ClientError


# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')

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
    run_rf = run_rf.drop(columns=['id'])
    return(run_df)

def run_rf(df):
    print("Running random forest model")

    X = df.drop('samples_ps', axis=1)
    y = df['samples_ps'] 

    encoder = TargetEncoder(X.columns)
    X_encoded = encoder.fit_transform(X, y) 

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

def handler(event, context):
    try:
        
        gpu_df = get_gpu_data()
        run_df = get_inference_run_data()
        run_df = run_df.join(gpu_df.set_index('accelerator_model_name'), on='accelerator_model_name')

        run_df['samples_ps'] = run_df['samples_ps'].astype('Int32')
        run_df = run_df.query("samples_ps < 200")

        rmse, accuracy, feature_importance_df = run_rf(run_df)

        feature_importance_df = feature_importance_df.query("Importance > 0")

        inference_analysis_id = str(uuid.uuid4())
        feature_importance_df['inference_analysis_id'] = inference_analysis_id

        analysis_table = dynamodb.Table('inference_analysis')
        analysis_table.put_item(
                Item={
                    'id': inference_analysis_id,
                    'rmse': str(rmse),
                     'accuracy': str(accuracy) })

        feature_table = dynamodb.Table('inference_analysis_features')
        for index, row in feature_importance_df.iterrows():
            item = row.to_dict()
            item['Importance'] = str(item['Importance'])
            item['id'] = str(uuid.uuid4())
            feature_table.put_item(Item=item)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Data retrieved successfully',
                'data': str(rmse)
            })
        }
    
    except ClientError as e:
        # Return error response if there is an issue accessing DynamoDB
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error accessing DynamoDB',
                'error': str(e)
            })
        }