import json
import base64
import boto3
import os
from flask import Flask, request, jsonify
import mlflow
from mlflow.tracking import MlflowClient

kinesis_client = boto3.client('kinesis')

PREDICTIONS_STREAM_NAME = os.getenv('PREDICTIONS_STREAM_NAME', 'ride_predictions')

RUN_ID = '708d7da218014fbf8e8e5a6c35010253'

logged_model = f's3://ml-flow-artifacts-remote445/1/{RUN_ID}/artifacts/model'

# Load model as a PyFuncModel.
model = mlflow.pyfunc.load_model(logged_model)

TEST_RUN = os.getenv('TEST_RUN', 'False') == 'True'

def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features


def predict(features):
    pred =  model.predict(features)
    return float(pred[0])


def lambda_handler(event, context):
 
    predictions = []
    for record in event['Records']:
        encoded_data = record['kinesis']['data']
        decoded_data = base64.b64decode(encoded_data).decode('utf-8')
        ride_event = json.loads(decoded_data)
        ride = ride_event['ride']
        ride_id = ride_event['ride_id']
        
        features = prepare_features(ride)
        prediction = predict(features)
        
        prediction_event = {
            'model':'ride_duration_prediction_model',
            'version':'123',
            'prediction':{
                'ride_duration': prediction,
                'ride_id': ride_id    
            }
            
        }
        
        if not TEST_RUN:
            kinesis_client.put_record(
                    StreamName=PREDICTIONS_STREAM_NAME,
                    Data=json.dumps(prediction_event),
                    PartitionKey=str(ride_id)
                )
            
        predictions.append(prediction_event)
    return {
        'predictions':predictions
    }
