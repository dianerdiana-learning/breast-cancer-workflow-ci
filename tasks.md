# Tasks Kriteria 4 untuk Pemula (Prometheus + Grafana)

Dokumen ini dibuat untuk kamu yang belum pernah pakai Prometheus dan Grafana.
Targetnya sederhana: kamu bisa menjalankan semuanya dari nol, lalu mengumpulkan bukti sesuai format penilaian Dicoding.

## 1) Pahami Dulu Tujuannya

Kriteria 4 meminta 3 hal utama:

1. Model berhasil di-serving secara lokal.
2. Metrik model dimonitor oleh Prometheus.
3. Metrik yang sama divisualkan di Grafana, lalu dibuat alert.

Catatan penting:

- Dashboard Grafana wajib diberi nama username Dicoding kamu.
- Bukti yang dikumpulkan utamanya screenshot.

## 2) Istilah Penting (Versi Singkat)

- Serving model: model dijalankan sebagai service/API di localhost.
- Metric: angka yang dipantau (contoh: jumlah prediksi, latency, accuracy).
- Exporter: script Python yang menyediakan metric ke endpoint /metrics.
- Scrape: proses Prometheus mengambil metric dari endpoint tersebut.
- Dashboard: tampilan grafik metric di Grafana.
- Alert: notifikasi jika metric melewati ambang batas.

## 3) Struktur Bukti yang Harus Ada

```tree
Monitoring dan Logging/
├── 1.bukti_serving
├── 2.prometheus.yml
├── 3.prometheus_exporter.py
├── 4.bukti monitoring Prometheus/
├── 5.bukti monitoring Grafana/
├── 6.bukti alerting Grafana/
├── 7.inference.py
└── file/folder tambahan (opsional)
```

## 4) Alur Kerja Paling Aman untuk Pemula

Ikuti urutan ini tanpa lompat langkah.

1. Pastikan model bisa serving dulu.
2. Jalankan exporter metric.
3. Jalankan Prometheus dan cek target UP.
4. Jalankan Grafana dan hubungkan ke Prometheus.
5. Buat dashboard (nama = username Dicoding).
6. Ambil screenshot monitoring.
7. Buat alert, tes, dan screenshot notifikasinya.

## 5) Setup Awal (Sekali Saja)

Checklist:

- [ ] Python sudah bisa jalan.
- [ ] MLflow dari kriteria 3 sudah siap.
- [ ] Download Prometheus dari https://prometheus.io/download/.
- [ ] Download Grafana dari https://grafana.com/grafana/download.
- [ ] Install package Python:

```bash
pip install prometheus-client flask requests psutil
```

## 6) Langkah Praktis Detail

### Langkah A - Serving Model

1. Jalankan model serving (pilih salah satu metode kriteria 3).
2. Contoh perintah MLflow:

```bash
mlflow models serve -m <model_uri> --port 5000
```

3. Cek di browser/curl bahwa endpoint hidup.
4. Screenshot terminal/browser, simpan ke folder 1.bukti_serving.

Checkpoint A (harus lolos):

- [ ] Service model berjalan di localhost.

### Langkah B - Buat Exporter Metric

1. Buat file 3.prometheus_exporter.py.
2. Exporter jalan di port 8000 dan menyediakan endpoint /metrics.
3. Metric minimal (untuk Basic):
   - model_predictions_total
   - model_prediction_latency_seconds
   - model_accuracy

Contoh kode paling sederhana:

```python
from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time
import random

app = Flask(__name__)

predictions_total = Counter("model_predictions_total", "Total jumlah prediksi")
prediction_latency = Histogram("model_prediction_latency_seconds", "Waktu prediksi")
model_accuracy = Gauge("model_accuracy", "Akurasi model")

@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

@app.post("/predict")
def predict():
    start = time.time()

    # Simulasi proses prediksi (ganti dengan model asli kamu)
    data = request.json
    result = {"prediction": 1, "input": data}

    predictions_total.inc()
    prediction_latency.observe(time.time() - start)
    model_accuracy.set(round(random.uniform(0.85, 0.99), 4))

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

4. Jalankan exporter:

```bash
python 3.prometheus_exporter.py
```

5. Buka http://localhost:8000/metrics dan pastikan metric terlihat.

Checkpoint B (harus lolos):

- [ ] Endpoint /metrics menampilkan teks metric Prometheus.

### Langkah C - Konfigurasi Prometheus

1. Buat file 2.prometheus.yml:

```yaml
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: 'ml-model'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

2. Jalankan Prometheus dari folder instalasi:

```bash
prometheus.exe --config.file="<path_ke>/2.prometheus.yml"
```

3. Buka http://localhost:9090.
4. Masuk menu Status -> Targets.
5. Pastikan job ml-model statusnya UP.

Checkpoint C (harus lolos):

- [ ] Target Prometheus = UP.

### Langkah D - Konfigurasi Grafana

1. Jalankan Grafana.
2. Buka http://localhost:3000.
3. Login awal: admin / admin (jika default belum diubah).
4. Tambah data source:
   - Connections -> Data sources -> Add data source -> Prometheus.
   - URL: http://localhost:9090.
   - Save & test.
5. Buat dashboard baru.
6. Nama dashboard wajib: username Dicoding kamu.
7. Tambahkan panel untuk metric yang sama seperti Prometheus.

Catatan penting agar panel tidak kosong:

- Gunakan nama metric asli (contoh: `model_accuracy`), bukan nama file screenshot (`monitoring_model_accuracy`).
- Set time range ke Last 1 hour atau Last 6 hours.
- Jalankan traffic generator (Langkah E) dulu sebelum cek panel.

Checkpoint D (harus lolos):

- [ ] Panel metric tampil normal di Grafana.
- [ ] Nama dashboard sesuai username Dicoding.

### Langkah E - Generate Data Supaya Grafik Bergerak

Kalau grafik kosong, biasanya karena belum ada request ke /predict.

Kirim request berkali-kali (contoh Python script 7.inference.py):

```python
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
```

Jalankan:

```bash
python 7.inference.py
```

Checkpoint E (harus lolos):

- [ ] Nilai metric berubah dari waktu ke waktu.

### Langkah F - Paket Query Grafana Siap Pakai (Target Advance)

Gunakan query berikut untuk membuat minimal 10 panel metric. Ini aman dipakai dengan exporter yang sekarang.

Tips:

- Untuk panel tipe Stat, pilih reducer Last.
- Untuk panel time series, pertahankan interval default Grafana.

Daftar query panel (format siap tempel di dashboard):

- title: Total Prediksi Model
  description: monitoring_model_predictions_total
  query: model_predictions_total

- title: Laju Prediksi Model 5 Menit
  description: monitoring_rate_model_predictions_total_5m
  query: rate(model_predictions_total[5m])

- title: Jumlah Observasi Latency Model
  description: monitoring_model_prediction_latency_seconds_count
  query: model_prediction_latency_seconds_count

- title: Rata-rata Latency Model 5 Menit
  description: monitoring_model_prediction_latency_avg_5m
  query: rate(model_prediction_latency_seconds_sum[5m]) / rate(model_prediction_latency_seconds_count[5m])

- title: P95 Latency Model 5 Menit
  description: monitoring_model_prediction_latency_p95_5m
  query: histogram_quantile(0.95, sum by (le) (rate(model_prediction_latency_seconds_bucket[5m])))

- title: Total HTTP Request
  description: monitoring_http_requests_total
  query: http_requests_total

- title: HTTP Throughput 5 Menit
  description: monitoring_http_requests_throughput_5m
  query: rate(http_requests_total[5m])

- title: Jumlah Observasi Latency HTTP
  description: monitoring_http_request_duration_seconds_count
  query: http_request_duration_seconds_count

- title: Rata-rata Latency HTTP 5 Menit
  description: monitoring_http_request_duration_avg_5m
  query: rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])

- title: CPU Usage Sistem
  description: monitoring_system_cpu_usage
  query: system_cpu_usage

- title: RAM Usage Sistem
  description: monitoring_system_ram_usage
  query: system_ram_usage

- title: Total Prediksi Berhasil
  description: monitoring_model_prediction_success_total
  query: model_prediction_success_total

- title: Total Prediksi Gagal
  description: monitoring_model_prediction_failure_total
  query: model_prediction_failure_total

- title: Akurasi Model Berjalan
  description: monitoring_model_accuracy
  query: model_accuracy

Catatan: metric model_accuracy hanya akan terisi jika request ke /predict menyertakan target/y_true/label_true.

## 7) Checklist Bukti yang Harus Discreenshot

### 7.1 Bukti Prometheus

Simpan di folder 4.bukti monitoring Prometheus.

Minimum Basic:

- [ ] monitoring_model_predictions_total
- [ ] monitoring_model_prediction_latency_seconds
- [ ] monitoring_model_accuracy

Tambahan untuk target Advance (minimal total 10 bukti metric):

- [ ] monitoring_rate_model_predictions_total_5m
- [ ] monitoring_model_prediction_latency_seconds_count
- [ ] monitoring_model_prediction_latency_avg_5m
- [ ] monitoring_model_prediction_latency_p95_5m
- [ ] monitoring_http_requests_total
- [ ] monitoring_http_requests_throughput_5m
- [ ] monitoring_http_request_duration_seconds_count
- [ ] monitoring_http_request_duration_avg_5m
- [ ] monitoring_system_cpu_usage
- [ ] monitoring_system_ram_usage
- [ ] monitoring_model_prediction_success_total
- [ ] monitoring_model_prediction_failure_total

### 7.2 Bukti Grafana

Simpan di folder 5.bukti monitoring Grafana.

Minimum Basic:

- [ ] monitoring_model_predictions_total
- [ ] monitoring_model_prediction_latency_seconds
- [ ] monitoring_model_accuracy
- [ ] screenshot yang terlihat nama dashboard (username Dicoding)

Tambahan untuk target Advance (minimal total 10 panel metric):

- [ ] monitoring_rate_model_predictions_total_5m
- [ ] monitoring_model_prediction_latency_seconds_count
- [ ] monitoring_model_prediction_latency_avg_5m
- [ ] monitoring_model_prediction_latency_p95_5m
- [ ] monitoring_http_requests_total
- [ ] monitoring_http_requests_throughput_5m
- [ ] monitoring_http_request_duration_seconds_count
- [ ] monitoring_http_request_duration_avg_5m
- [ ] monitoring_system_cpu_usage
- [ ] monitoring_system_ram_usage
- [ ] monitoring_model_prediction_success_total
- [ ] monitoring_model_prediction_failure_total

### 7.3 Bukti Alert Grafana (untuk Skilled/Advance)

Simpan di folder 6.bukti alerting Grafana.

- [ ] rules_alert_1
- [ ] notifikasi_alert_1
- [ ] rules_alert_2 (Advance)
- [ ] notifikasi_alert_2 (Advance)
- [ ] rules_alert_3 (Advance)
- [ ] notifikasi_alert_3 (Advance)

Format penamaan file screenshot yang disarankan:

- [ ] rules_alert_1_latency_http_tinggi
- [ ] notifikasi_alert_1_latency_http_tinggi
- [ ] rules_alert_2_failure_request_prediksi
- [ ] notifikasi_alert_2_failure_request_prediksi
- [ ] rules_alert_3_throughput_rendah
- [ ] notifikasi_alert_3_throughput_rendah

## 8) Cara Buat Alert Paling Mudah (Siap Advance)

Gunakan 3 alert ini supaya sesuai syarat Advance dan stabil dipakai di Windows.

1. Alert 1 - Latency HTTP Tinggi
   - Query:

```promql
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])
```

- Kondisi: IS ABOVE 0.50 selama 1m.
- Severity: critical.

2. Alert 2 - Failure Request Prediksi
   - Query:

```promql
increase(model_prediction_failure_total[5m])
```

- Kondisi: IS ABOVE 0 selama 1m.
- Severity: warning.

3. Alert 3 - Throughput Rendah
   - Query:

```promql
rate(http_requests_total[5m])
```

- Kondisi: IS BELOW 0.05 selama 2m.
- Severity: warning.

Opsional (jika payload menyertakan target/y_true/label_true):

- Alert Accuracy Drop dengan query model_accuracy dan kondisi IS BELOW 0.90 selama 1m.

Tips tes alert cepat:

- Ubah threshold sementara agar mudah terpicu.
- Tunggu 1-2 menit.
- Screenshot rule dan notifikasinya.
- Aktifkan traffic generator saat test alert:

```bash
python 7.inference.py
```

## 9) Target Penilaian (Pilih Mau Ke Level Mana)

### Basic (2 poin)

- [ ] Serving model lokal berjalan.
- [ ] Prometheus monitoring minimal 3 metric.
- [ ] Grafana menampilkan 3 metric yang sama.

### Skilled (3 poin)

- [ ] Semua syarat Basic.
- [ ] Grafana menampilkan minimal 5 metric.
- [ ] Minimal 1 alert Grafana aktif + bukti notifikasi.
- [ ] Rekomendasi praktik: buat 5 panel dari daftar Langkah F.

### Advance (4 poin)

- [ ] Semua syarat Skilled.
- [ ] Grafana menampilkan minimal 10 metric.
- [ ] Minimal 3 alert Grafana aktif + bukti notifikasi.
- [ ] Gunakan minimal 10 panel dari daftar Langkah F.
- [ ] Gunakan 3 alert dari Langkah 8 (Latency HTTP Tinggi, Failure Request Prediksi, Throughput Rendah).
- [ ] Simpan semua screenshot rule + notifikasi sesuai checklist 7.3.

## 10) Troubleshooting Cepat

1. Target Prometheus DOWN:
   - Cek exporter jalan di port 8000.
   - Cek URL target di prometheus.yml.

2. Metric tidak muncul di Grafana:
   - Cek data source Prometheus berhasil (Save & test).
   - Cek query metric benar (tanpa typo).
   - Pastikan nama metric tidak diawali `monitoring_` karena itu hanya nama file screenshot.
   - Untuk Windows, prioritaskan metric `system_cpu_usage` dan `system_ram_usage`, bukan `process_*`.

3. Grafik kosong:
   - Jalankan 7.inference.py untuk kirim request.

4. Alert tidak pernah firing:
   - Turunkan threshold sementara.
   - Pastikan evaluation interval cukup singkat.
   - Untuk alert failure, kirim payload yang sengaja salah agar `model_prediction_failure_total` naik.

## 11) Ringkasan Eksekusi Harian (Supaya Tidak Bingung)

Urutan saat praktik:

1. Jalankan model serving.
2. Jalankan 3.prometheus_exporter.py.
3. Jalankan Prometheus.
4. Jalankan Grafana.
5. Jalankan 7.inference.py untuk generate traffic.
6. Ambil screenshot Prometheus.
7. Ambil screenshot Grafana.
8. Buat dan tes alert, ambil screenshot.

Jika semua checklist tercentang, artefak Kriteria 4 kamu sudah siap dikumpulkan.
