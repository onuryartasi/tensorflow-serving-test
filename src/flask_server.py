#!/usr/bin/env python

import urllib

import flask
from waitress import serve

from grpc.beta import implementations
import tensorflow as tf

import predict_pb2
import prediction_service_pb2

from google.protobuf.json_format import MessageToJson

app = flask.Flask(__name__)


@app.route('/model_prediction', methods=["GET", "POST"])
def model_prediction():
    host = "localhost" 
    port = 9000        
    model_name = "resnet"
    json = flask.request.get_json()
    url_input = json['input']

    image = urllib.urlopen(url_input).read()

    channel = implementations.insecure_channel(host, int(port))
    stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)

    request = predict_pb2.PredictRequest()
    request.model_spec.name = 'resnet'
    request.model_spec.signature_name = 'predict_images'
    request.inputs['images'].CopyFrom(
        tf.contrib.util.make_tensor_proto(image, shape=[1]))
    result = stub.Predict(request, 10.0)  # 10 secs timeout
    print(result)

    return result


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8080)
