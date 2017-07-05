import numpy as np
import cPickle as pickle
import requests

def test_flask_client(x):
    URL = "http://localhost:8915/model_prediction"

    s = pickle.dumps({"x":x}, protocol=0)

    DATA = {"model_name": "default",
            "input": requests.utils.quote(s)}

    r = requests.get(URL, data=DATA)
    return r.json()

if __name__ == '__main__':
  test_flask_client(1)