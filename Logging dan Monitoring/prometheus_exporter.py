import os
import threading
import time
from typing import Any

import requests
from flask import Flask, jsonify, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

import psutil

app = Flask(__name__)

# Endpoint model MLflow default: http://127.0.0.1:5000/invocations
MODEL_URL = os.getenv("MODEL_URL", "http://127.0.0.1:5000/invocations")
MODEL_TIMEOUT_SECONDS = float(os.getenv("MODEL_TIMEOUT_SECONDS", "10"))
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

PREDICTION_TOTAL = Counter("model_predictions_total", "Total jumlah prediksi")
PREDICTION_LATENCY = Histogram(
    "model_prediction_latency_seconds", "Waktu prediksi model"
)
MODEL_ACCURACY = Gauge(
    "model_accuracy", "Akurasi model dari request yang punya label target"
)

REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests ke endpoint predict"
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency untuk endpoint predict"
)
THROUGHPUT = Counter(
    "http_requests_throughput", "Counter request (throughput hitung via rate())"
)

PREDICTION_SUCCESS_TOTAL = Counter(
    "model_prediction_success_total", "Total request prediksi yang berhasil"
)
PREDICTION_FAILURE_TOTAL = Counter(
    "model_prediction_failure_total", "Total request prediksi yang gagal"
)

CPU_USAGE = Gauge("system_cpu_usage", "CPU usage percentage")
RAM_USAGE = Gauge("system_ram_usage", "RAM usage percentage")

_eval_lock = threading.Lock()
_eval_total = 0
_eval_correct = 0


def _update_system_metrics() -> None:
    if psutil is None:
        CPU_USAGE.set(0.0)
        RAM_USAGE.set(0.0)
        return

    CPU_USAGE.set(psutil.cpu_percent(interval=None))
    RAM_USAGE.set(psutil.virtual_memory().percent)


def _normalize_payload(data: Any) -> dict[str, Any]:
    # Support payload yang sudah format MLflow atau payload sederhana dict fitur.
    if isinstance(data, dict):
        if (
            "dataframe_split" in data
            or "dataframe_records" in data
            or "instances" in data
        ):
            return data
        return {"dataframe_records": [data]}

    if isinstance(data, list):
        if not data:
            raise ValueError("Payload list tidak boleh kosong.")
        if all(isinstance(item, dict) for item in data):
            return {"dataframe_records": data}
        return {"instances": data}

    raise ValueError("Payload harus berupa object JSON atau list.")


def _extract_true_label(data: Any) -> tuple[Any, Any]:
    if isinstance(data, dict):
        copied = dict(data)
        for key in ("target", "y_true", "label_true"):
            if key in copied:
                return copied.pop(key), copied
        return None, copied
    return None, data


def _extract_predicted_label(model_output: Any) -> Any:
    if isinstance(model_output, dict):
        if "predictions" in model_output:
            preds = model_output["predictions"]
            if isinstance(preds, list) and preds:
                first = preds[0]
                if isinstance(first, list) and first:
                    return first[0]
                return first
        if "prediction" in model_output:
            return model_output["prediction"]
        return None

    if isinstance(model_output, list) and model_output:
        first = model_output[0]
        if isinstance(first, list) and first:
            return first[0]
        return first

    return None


def _update_accuracy_if_possible(true_label: Any, predicted_label: Any) -> None:
    global _eval_total, _eval_correct

    if true_label is None or predicted_label is None:
        return

    with _eval_lock:
        _eval_total += 1
        if str(predicted_label) == str(true_label):
            _eval_correct += 1
        MODEL_ACCURACY.set(_eval_correct / _eval_total)


@app.get("/health")
def health() -> Any:
    return jsonify({"status": "ok", "model_url": MODEL_URL})


@app.get("/metrics")
def metrics() -> Any:
    _update_system_metrics()
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@app.post("/predict")
def predict() -> Any:
    start = time.perf_counter()
    REQUEST_COUNT.inc()
    THROUGHPUT.inc()

    data = request.get_json(silent=True)
    if data is None:
        PREDICTION_FAILURE_TOTAL.inc()
        return jsonify({"error": "Body JSON wajib diisi."}), 400

    true_label, feature_payload = _extract_true_label(data)

    try:
        payload = _normalize_payload(feature_payload)
        model_resp = requests.post(
            MODEL_URL, json=payload, timeout=MODEL_TIMEOUT_SECONDS
        )
        model_resp.raise_for_status()
        prediction_result = model_resp.json()

        duration = time.perf_counter() - start
        REQUEST_LATENCY.observe(duration)
        PREDICTION_LATENCY.observe(duration)
        PREDICTION_TOTAL.inc()
        PREDICTION_SUCCESS_TOTAL.inc()

        predicted_label = _extract_predicted_label(prediction_result)
        _update_accuracy_if_possible(true_label, predicted_label)

        return (
            jsonify(
                {
                    "prediction": prediction_result,
                    "model_url": MODEL_URL,
                    "latency_seconds": round(duration, 6),
                    "received_target": true_label,
                    "predicted_label": predicted_label,
                }
            ),
            200,
        )
    except requests.RequestException as exc:
        PREDICTION_FAILURE_TOTAL.inc()
        return (
            jsonify({"error": "Gagal mengakses model server", "detail": str(exc)}),
            502,
        )
    except ValueError as exc:
        PREDICTION_FAILURE_TOTAL.inc()
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        PREDICTION_FAILURE_TOTAL.inc()
        return jsonify({"error": "Unexpected error", "detail": str(exc)}), 500


if __name__ == "__main__":
    _update_system_metrics()
    app.run(host=APP_HOST, port=APP_PORT)
