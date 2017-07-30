# TensorFlow Serving Test

**Welcome to TensorFlow Serving Test!**

This repository contains a simple Python-based client to TensorFlow Serving and a script to start a simple TensorFlow Serving server.

## How to Run

1. Download the example model `resnet50-ir-256x256-augmented-iter32-batch12.zip` from the staging account in `ii-ava-dev/classification-tensorflow`. This is an IR model used in production.
2. Place the model in the directory `data/resnet-model-data/1/`; this will place set the model as version 1.
3. Build a Docker container
```
docker build .
```
To get a container with GPU support, run this instead
```
docker build -f Dockerfile.gpu .
```
4. Run the Docker container 
```
docker run --rm -it -v ${PWD}:/app <image-id> /bin/bash
```
If your machine has a GPU, the GPU can be accessed via [NVIDIA Docker](https://github.com/NVIDIA/nvidia-docker), so instead, run
```
nvidia-docker run --rm -it -v ${PWD}:/app <image-id> /bin/bash
```
5. Start the server by running it in the background
```
./scripts/serve.sh &
```
6. Run the following to create a request to the server
```
python src/perf.py
```
7. You should obtain an output similar to this
```
Downloading image
Make prediction request
Predicting...
Computed result in 10.0979089737
outputs {
  key: "classes"
  value {
    dtype: DT_STRING
    tensor_shape {
      dim {
        size: 5
      }
      dim {
        size: 1
      }
    }
    string_val: "person"
    string_val: "person"
    string_val: "person"
    string_val: "person"
    string_val: "person"
  }
}
outputs {
  key: "scores"
  value {
    dtype: DT_FLOAT
    tensor_shape {
      dim {
        size: 5
      }
      dim {
        size: 1
      }
    }
    float_val: 8.46247494337e-05
    float_val: 0.999976158142
    float_val: 1.0
    float_val: 0.504229664803
    float_val: 1.0
  }
}
```


## New Models

For any model, if there is a new version, place them in a folder denoted by an *integer*. For example, if there is a new version of the model `resnet-model-data` above, place the new definition and weights in the path `data/resnet-model-data/2/`.

The manager in TensorFlow Serving will load the model from the folder labeled with the largest integer. Note that the whole model needs to be loaded in its entirely as the manager's polling rate is very high, so it will try to load a partially downloaded file as soon as a new directory appears.

## Server Settings

In `scripts/server.sh`, there is a shell script that specifies the configuration of the TensorFlow Serving server:
```
/serving/bazel-bin/tensorflow_serving/model_servers/tensorflow_model_server --port=9000 --model_name="resnet" --model_base_path=/app/data/resnet-model-data --enable_batching --batching_parameters_file=config/batching_config.txt
```

The following is the full list of flags:

1. `port`: port to listen on.
2. `enable_batching`: enable batching.
3. `batching_parameters_file`: If non-empty, read an ascii BatchingParameters protobuf from the supplied file name and use the contained values instead of the defaults.
4. `model_config_file`: If non-empty, read an ascii ModelServerConfig protobuf from the supplied file name, and serve the models in that file. (If used, `--model_name`, `--model_base_path` and `--model_version_policy` are ignored.)
5. `model_name`: name of model (ignored if `--model_config_file` flag is set).
6. `model_base_path`: path to export (ignored if --model_config_file flag is set, otherwise required).
7. `model_version_policy`: The version policy which determines the number of model versions to be served at the same time. The default value is LATEST_VERSION, which will serve only the latest version. (Ignored if `--model_config_file` flag is set). The list of version policies are:
  * `Latest`: serves the latest model version found on disk,
  * `All`: serves all models found on disk, and
  * `Specific`: serves a specific model version found on disk.
8. `file_system_poll_wait_seconds`: interval in seconds between each poll of the file system for new model version.
9. `use_saved_model`: interval in seconds between each poll of the file system for new model version.
10. `tensorflow_session_parallelism`: number of threads to use for running a Tensorflow session. Auto-configured by default. Note that this option is ignored if `--platform_config_file` is non-empty.
11. `platform_config_file`: if non-empty, read an ascii PlatformConfigMap protobuf from the supplied file name, and use that platform config instead of the Tensorflow platform. (If used, `--enable_batching` and `--use_saved_model`are ignored.)

## Batching Configuration

In `config/batching_config.txt`, we have a configuration file with contents
```
max_batch_size { value: 8 }
batch_timeout_micros { value: 0 }
max_enqueued_batches { value: 1000000 }
num_batch_threads { value: 8 }
```

1. `max_batch_size`: the maximum size of any batch. This parameter governs the throughput/latency tradeoff, and also avoids having batches that are so large they exceed some resource constraint (e.g. GPU memory to hold a batch's data).
2. `batch_timeout_micros`: the maximum amount of time to wait before executing a batch (even if it hasn't reached `max_batch_size`). Used to rein in tail latency. 
3. `num_batch_threads`: the degree of parallelism, *i.e.,* the maximum number of batches processed concurrently.
4. `max_enqueued_batches`: the number of batches worth of tasks that can be enqueued to the scheduler. Used to bound queueing delay, by turning away requests that would take a long time to get to, rather than building up a large backlog.

More details can be found [here](https://github.com/tensorflow/serving/tree/master/tensorflow_serving/batching).

If the number of images in a request exceeds the `max_batch_size`, then the TensorFlow Serving server reports with
```
grpc.framework.interfaces.face.face.AbortionError: AbortionError(code=StatusCode.INVALID_ARGUMENT, details="Task size 5 is larger than maximum batch size 2")
```
when `max_batch_size` is equal to 2.
