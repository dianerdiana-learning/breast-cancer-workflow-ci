import requests
import time

URL = "http://localhost:8000/predict"

for i in range(5):
    r = requests.post(
        URL,
        data="this-is-not-json",
        headers={"Content-Type": "text/plain"},
        timeout=10,
    )
    print(i, r.status_code, r.text)
    time.sleep(1)
