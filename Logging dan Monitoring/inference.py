import random
import time
import requests

# normal traffic
URL = "http://localhost:8000/predict"


def make_payload(include_target: bool = False):
    payload = {
        "mean radius": round(random.uniform(-3.0, 3.0), 4),
        "mean texture": round(random.uniform(-3.0, 3.0), 4),
        "mean perimeter": round(random.uniform(-3.0, 3.0), 4),
        "mean area": round(random.uniform(-3.0, 3.0), 4),
        "mean smoothness": round(random.uniform(-3.0, 3.0), 4),
        "mean compactness": round(random.uniform(-3.0, 3.0), 4),
        "mean concavity": round(random.uniform(-3.0, 3.0), 4),
        "mean concave points": round(random.uniform(-3.0, 3.0), 4),
        "mean symmetry": round(random.uniform(-3.0, 3.0), 4),
        "mean fractal dimension": round(random.uniform(-3.0, 3.0), 4),
        "radius error": round(random.uniform(-3.0, 3.0), 4),
        "texture error": round(random.uniform(-3.0, 3.0), 4),
        "perimeter error": round(random.uniform(-3.0, 3.0), 4),
        "area error": round(random.uniform(-3.0, 3.0), 4),
        "smoothness error": round(random.uniform(-3.0, 3.0), 4),
        "compactness error": round(random.uniform(-3.0, 3.0), 4),
        "concavity error": round(random.uniform(-3.0, 3.0), 4),
        "concave points error": round(random.uniform(-3.0, 3.0), 4),
        "symmetry error": round(random.uniform(-3.0, 3.0), 4),
        "fractal dimension error": round(random.uniform(-3.0, 3.0), 4),
        "worst radius": round(random.uniform(-3.0, 3.0), 4),
        "worst texture": round(random.uniform(-3.0, 3.0), 4),
        "worst perimeter": round(random.uniform(-3.0, 3.0), 4),
        "worst area": round(random.uniform(-3.0, 3.0), 4),
        "worst smoothness": round(random.uniform(-3.0, 3.0), 4),
        "worst compactness": round(random.uniform(-3.0, 3.0), 4),
        "worst concavity": round(random.uniform(-3.0, 3.0), 4),
        "worst concave points": round(random.uniform(-3.0, 3.0), 4),
        "worst symmetry": round(random.uniform(-3.0, 3.0), 4),
        "worst fractal dimension": round(random.uniform(-3.0, 3.0), 4),
    }

    if include_target:
        payload["target"] = random.choice([0, 1])

    return payload


for i in range(120):
    payload = make_payload()

    try:
        r = requests.post(URL, json=payload, timeout=10)
        print(i, r.status_code)
    except Exception as e:
        print(i, "ERR", e)

    time.sleep(0.5)

# labeled traffic
for i in range(100):
    payload = make_payload()
    payload["target"] = random.choice([0, 1])

    try:
        r = requests.post(URL, json=payload, timeout=10)
        print(i, r.status_code, r.json().get("predicted_label"))
    except Exception as e:
        print(i, "ERR", e)

    time.sleep(0.6)
