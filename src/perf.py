#!/usr/bin/env python

import time
import urllib
from grpc.beta import implementations
import tensorflow as tf

import predict_pb2
import prediction_service_pb2


def create_request():
    print('Downloading image')
    image_data = []
    image_data.append(urllib.urlopen("https://cammyeu.blob.core.windows.net/2017-07-13/3e961e944d7c9631f64648f3f639e06924c191edG.jpg").read())
    image_data.append(urllib.urlopen("https://cammyau.blob.core.windows.net/2017-07-13/24df8d25d4e1282bc45590c919586882dae2c24fE.jpg").read())
    image_data.append(urllib.urlopen("https://cammyeu.blob.core.windows.net/2017-07-13/323245bab1d12e47f616f48b39548c8ec20295bbG.jpg").read())
    image_data.append(urllib.urlopen("https://cammyus.blob.core.windows.net/2017-07-27/6bd2d1e93c4d81f247b11d3b97e73774f8c3ae7dF.jpg").read())
    image_data.append(urllib.urlopen("https://cammyus.blob.core.windows.net/2017-07-27/72107e8b981151bf806cdf7b35837403bbb592e1F.jpg").read())

    print('Make prediction request')
    request = predict_pb2.PredictRequest()
    request.model_spec.name = 'resnet'
    request.model_spec.signature_name = 'predict_images'

    request.inputs['images'].CopyFrom(
        tf.contrib.util.make_tensor_proto(image_data, shape=[len(image_data)])
    )

    return request


def main(host, port):
    channel = implementations.insecure_channel(host, int(port))
    stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)

    start = time.time()
    request = create_request()
    print('Predicting...')
    result = stub.Predict(request, 10.0)  # 10 secs timeout
    duration = time.time() - start
    print("Computed result in %s" % duration)
    print(result)


if __name__ == '__main__':
    main("localhost", 9000)
