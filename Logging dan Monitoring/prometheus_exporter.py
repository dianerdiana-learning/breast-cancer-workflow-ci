from flask import Flask, request, jsonify
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
import time
import random
import psutil

app = Flask(__name__)

PREDICTION_TOTAL = Counter("model_predictions_total", "Total jumlah prediksi")
PREDICTION_LATENCY = Histogram("model_prediction_latency_seconds", "Waktu prediksi")
MODEL_ACCURACY = Gauge("model_accuracy", "Akurasi model")
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Requests")
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP Request Latency")
THROUGHPUT = Counter("http_requests_throughput", "Total requests per DETIK")

CPU_USAGE = Gauge("system_cpu_usage", "CPU Usage Percentage")  # Penggunaan CPU
RAM_USAGE = Gauge("system_ram_usage", "RAM Usage Percentage")  # Penggunaan RAM


@app.get("/metrics")
def metrics():
    CPU_USAGE.set(psutil.cpu_percent(interval=1))
    RAM_USAGE.set(psutil.virtual_memory().percent)
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@app.post("/predict")
def predict():
    start = time.time()

    data = request.json
    result = {"prediction": 1, "input": data}

    PREDICTION_TOTAL.inc()
    PREDICTION_LATENCY.observe(time.time() - start)
    MODEL_ACCURACY.set(round(random.uniform(0.85, 0.99), 4))

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
