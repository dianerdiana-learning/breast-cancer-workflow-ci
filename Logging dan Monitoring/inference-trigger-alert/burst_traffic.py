import requests
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "http://localhost:8000/predict"


def make_payload():
    return {
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


payloads = [make_payload() for _ in range(300)]


def send_one(p):
    r = requests.post(URL, json=p, timeout=10)
    return r.status_code


with ThreadPoolExecutor(max_workers=25) as ex:
    futures = [ex.submit(send_one, p) for p in payloads]
    ok = 0
    fail = 0
    for f in as_completed(futures):
        try:
            code = f.result()
            if code == 200:
                ok += 1
            else:
                fail += 1
        except Exception:
            fail += 1

print("done", {"ok": ok, "fail": fail})
