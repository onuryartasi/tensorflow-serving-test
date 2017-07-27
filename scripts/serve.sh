#!/bin/bash

set -eu

/serving/bazel-bin/tensorflow_serving/model_servers/tensorflow_model_server --port=9000 --model_name="resnet" --model_base_path=/app/data/resnet-model-data --enable_batching --batching_parameters_file=config/batching_config.txt
#/serving/bazel-bin/tensorflow_serving/model_servers/tensorflow_model_server --port=9000 --model_name="inception" --model_base_path=/app/data/inception-model-data
