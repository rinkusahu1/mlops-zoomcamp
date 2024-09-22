import pickle

from flask import Flask, request, jsonify
import mlflow
from mlflow.tracking import MlflowClient


MLFLOW_TRACKING_URI = 'http://127.0.0.1:5000'
RUN_ID = '708d7da218014fbf8e8e5a6c35010253'

#mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
# mlflow.set_experiment("green-taxi-duration")
# client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)

# path = client.download_artifacts(run_id=RUN_ID, path='preprocessor/dict_vectorizer.bin')
# print(f"Download dict vectorizer to {path}")

# with open(path, 'rb') as f_in:
#     dv = pickle.load(f_in) 

logged_model = f's3://ml-flow-artifacts-remote445/1/{RUN_ID}/artifacts/model'

# Load model as a PyFuncModel.
model = mlflow.pyfunc.load_model(logged_model)

def prepare_feature(ride):
    features = {}
    features['PU_DO']  = '%s_%s' %(ride['PULocationID'],ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features


def predict(features):
    #X =dv.transform(features)
    predics = model.predict(features)
    return float(predics[0])


app = Flask('duration-prediction')


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    ride = request.get_json()

    features = prepare_feature(ride)
    pred = predict(features)

    result = {
        'duration': pred,
        'model_version':RUN_ID
    }

    return jsonify(result)

# Flask use here, is only use for development use cases, neeed proper wsji server for production env
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)