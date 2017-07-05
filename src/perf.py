#!/usr/bin/env python

import time
import urllib
from grpc.beta import implementations
import tensorflow as tf

import predict_pb2
import prediction_service_pb2

from google.protobuf.json_format import MessageToJson

def create_request():
  image = urllib.urlopen("http://i.imgur.com/hYhFcVf.jpg").read()
  
  image_data = []
  for i in range(20):
    image_data.append(image)

  request = predict_pb2.PredictRequest()
  request.model_spec.name = 'inception'
  request.model_spec.signature_name = 'predict_images'

  request.inputs['images'].CopyFrom(
    tf.contrib.util.make_tensor_proto(image_data, shape=[len(image_data)])
  )

  return request

def main(host, port):
  channel = implementations.insecure_channel(host, int(port))
  stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)

  while True:
    start = time.time()
    request = create_request()
    result = stub.Predict(request, 10.0)  # 10 secs timeout
    duration = time.time() - start
    print("Computed result in %s" %duration)

if __name__ == '__main__':
  main("localhost", 9000)