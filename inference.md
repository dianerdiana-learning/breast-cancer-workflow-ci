# Inference Playbook (Siap Pakai)

Dokumen ini berisi script inference yang bisa langsung dipakai untuk:

- memunculkan metric di Prometheus/Grafana,
- mengisi metrik akurasi (model_accuracy),
- trigger alert sesuai rule di dashboard.

Catatan konteks saat ini:

- Exporter berjalan di http://localhost:8000
- Endpoint inference exporter: POST /predict
- Endpoint metrics exporter: GET /metrics
- Model server default yang dipanggil exporter: http://127.0.0.1:5000/invocations
- Payload request harus memakai nama fitur yang sama persis dengan kolom model.
- Untuk contoh model ini, ada 30 fitur input; `target` hanya dipakai sebagai label evaluasi dan tidak dikirim ke model.

## 1) Checklist Run Service

Jalankan 3 proses ini dulu (terminal terpisah):

```bash
# Terminal 1: model serving
mlflow models serve -m MLProject/outputs/model --port 5000 --env-manager local

# Terminal 2: exporter
python Logging dan Monitoring/prometheus_exporter.py

# Terminal 3: prometheus
prometheus.exe --config.file="Logging dan Monitoring/prometheus.yml"
```

Cek cepat:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/metrics
```

## 2) Mapping Payload Sesuai Fitur Model

Model dilatih dengan 30 fitur berikut. Saat request ke exporter, payload harus mengikuti nama kolom ini persis; `target` boleh ditambahkan hanya untuk hitung `model_accuracy`.

```python
# feature_payload.py
import random


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
```

## 3) Inference Normal (Biar Panel Muncul)

Script ini menghasilkan traffic stabil ke exporter agar panel metric bergerak.

```python
# normal_traffic.py
import random
import time
import requests

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


for i in range(120):
    payload = make_payload()

    try:
        r = requests.post(URL, json=payload, timeout=10)
        print(i, r.status_code)
    except Exception as e:
        print(i, "ERR", e)

    time.sleep(0.5)
```

Jalankan:

```bash
python normal_traffic.py
```

## 4) Inference Dengan Label (Agar model_accuracy Terisi)

model_accuracy pada exporter hanya diupdate jika payload menyertakan salah satu field:

- target, atau
- y_true, atau
- label_true.

Script berikut mengirim target supaya metric model_accuracy bisa naik/turun.

```python
# labeled_traffic.py
import random
import time
import requests

URL = "http://localhost:8000/predict"


def make_payload():
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
        "target": random.choice([0, 1]),
    }

    return payload


for i in range(100):
    payload = make_payload()

    try:
        r = requests.post(URL, json=payload, timeout=10)
        print(i, r.status_code, r.json().get("predicted_label"))
    except Exception as e:
        print(i, "ERR", e)

    time.sleep(0.6)
```

Jalankan:

```bash
python labeled_traffic.py
```

## 5) Trigger Alert: Failure Request Prediksi

Alert query contoh:

```promql
increase(model_prediction_failure_total[5m]) > 0
```

Cara trigger cepat: kirim body non-JSON agar exporter mengembalikan 400 dan menaikkan model_prediction_failure_total.

```python
# trigger_failure_alert.py
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
```

Jalankan:

```bash
python trigger_failure_alert.py
```

## 6) Trigger Alert: Throughput Rendah

Alert query contoh:

```promql
rate(http_requests_total[5m]) < 0.05
```

Langkah trigger:

1. Jalankan normal_traffic.py dulu 1-2 menit.
2. Hentikan semua script inference (jangan kirim request baru).
3. Tunggu sesuai for duration alert (misalnya 2 menit).
4. Ambil screenshot state alert.

## 7) Trigger Alert: Latency Tinggi

Alert query contoh:

```promql
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m]) > 0.50
```

Karena latency tergantung kecepatan model/server lokal, cara demo paling stabil:

1. Turunkan threshold sementara, misalnya > 0.02 selama 1m.
2. Jalankan normal_traffic.py.
3. Jika belum firing, buat beban lebih tinggi pakai burst script di bawah.

```python
# burst_traffic.py
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
```

Jalankan:

```bash
python burst_traffic.py
```

## 8) Query Cek Cepat di Grafana/Prometheus

```promql
model_predictions_total
```

```promql
rate(http_requests_total[5m])
```

```promql
model_prediction_success_total
```

```promql
model_prediction_failure_total
```

```promql
system_cpu_usage
```

```promql
system_ram_usage
```

```promql
model_accuracy
```

## 9) Troubleshooting Singkat

- Jika semua metric no data:
  - cek /health exporter,
  - cek target Prometheus harus UP,
  - cek traffic benar-benar dikirim ke http://localhost:8000/predict.
- Jika model_prediction_failure_total terus naik:
  - cek model serving di port 5000 masih hidup.
- Jika model_accuracy kosong:
  - pastikan payload kirim field target/y_true/label_true.
- Jika throughput tidak bergerak:
  - jalankan normal_traffic.py lalu refresh panel dengan time range Last 15m atau Last 1h.
