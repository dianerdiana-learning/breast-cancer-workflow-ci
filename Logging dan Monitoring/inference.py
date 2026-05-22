import requests
import time

for i in range(30):
    payload = {
        "radius_mean": 14.1,
        "texture_mean": 20.2,
        "perimeter_mean": 91.0,
    }
    requests.post("http://localhost:8000/predict", json=payload, timeout=5)
    time.sleep(1)
