Kriteria 4: Membuat Sistem Monitoring dan Logging
Monitoring dan Logging merupakan tahapan yang tidak bisa berdiri sendiri karena membutuhkan artefak yang dihasilkan oleh kriteria tiga. Nantinya, Anda hanya akan mengumpulkan tangkapan layar mengenai skill yang diampu dengan struktur seperti berikut ini.

```tree
Monitoring dan Logging
├── 1.bukti_serving
├── 2.prometheus.yml
├── 3.prometheus_exporter.py
├── 4.bukti monitoring Prometheus (folder)
    └── 1.monitoring_<metriks>
    └── 2.monitoring_<metriks>
    └── dst (sesuaikan dengan poin yang diraih)
├── 5.bukti monitoring Grafana (folder)
    └── 1.monitoring_<metriks>
    └── 2.monitoring_<metriks>
    └── dst (sesuaikan dengan poin yang diraih)
├── 6.bukti alerting Grafana (folder)
    └── 1.rules_<metriks>
    └── 2.notifikasi_<metriks>
    └── 3.rules_<metriks>
    └── 4.notifikasi_<metriks>
    └── dst (sesuaikan dengan poin yang diraih)
├── 7.inference.py
├── folder/file tambahan
```

Penting, pastikan untuk membuat dashboard dengan nama username akun Dicoding sehingga tangkapan layar yang Anda kirimkan akan berisikan kredensial.

Berikut adalah penilaian lengkap untuk kriteria 4:

Reject (0 pts)

- Tidak melakukan serving model pada environment local.
- Tidak melakukan monitoring performa sistem machine learning menggunakan Prometheus
- Tidak menggunakan Grafana sebagai tools visualisasi dan alerting sistem machine learning

Basic (2 pts)

- Melakukan serving model baik itu melalui artefak yang sudah dibuat atau pull Images (jika menerapkan kriteria CI untuk melakukan push ke Docker Hub)
- Bisa melalui mlflow model serve, mlflow deployments, atau pull images jika memenuhi kriteria 3 advanced.
- Melakukan monitoring menggunakan Prometheus minimal dengan tiga metriks yang berbeda.
- Melakukan monitoring menggunakan Grafana dengan metriks yang sama dengan Prometheus.

Skilled (3 pts)

- Melakukan monitoring menggunakan Grafana dengan minimal 5 metriks yang berbeda.
- Membuat satu alerting menggunakan Grafana.

Advance (4 pts)

- Melakukan monitoring menggunakan Grafana dengan minimal 10 metriks yang berbeda.
- Membuat tiga alerting menggunakan Grafana.
