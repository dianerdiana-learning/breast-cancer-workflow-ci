Kriteria 3: Membuat Workflow CI
Setelah membuat dan memastikan file modelling.py berjalan dengan baik, selanjutnya Anda harus membuat workflow CI menggunakan MLflow Project agar dapat melakukan re-training model secara otomatis ketika trigger dipantik.

Silakan Anda buat sebuah project repository baru di GitHub dengan struktur seperti berikut ini.

```tree
Workflow-CI
├── .workflow
├── MLProject (folder)
    └── modelling.py
    └── conda.yaml
    └── MLProject
    └── namadataset_preprocessing (bisa berupa file atau folder)
    └── Tautan ke Docker Hub
    └── (file tambahan jika diperlukan)
```

Anda dapat menggunakan file modelling.py, conda.yaml serta dataset yang sudah siap dilatih dari hasil eksperimen sebelumnya. Pada tahap ini, Anda hanya perlu membuat struktur yang diminta beserta file MLProjectnya saja. Namun, tidak menutup kemungkinan Anda harus menyesuaikan file modelling.py ketika masuk ke tahap ini.

Berikut adalah penilaian lengkap untuk kriteria 3:

Reject (0 pts)

- Tidak membuat folder MLProject.
- Tidak membuat workflow CI menggunakan GitHub Actions.

Basic (2 pts)

- Membuat folder MLProject.
- Membuat Worflow CI yang dapat membuat model machine learning ketika trigger terpantik.

Skilled (3 pts)

- Membuat workflow CI dan menyimpan artefak ke suatu repositori (GitHub yang sama atau Google Drive).

Advance (4 pts)

- Membuat workflow CI dan menyimpan artefak ke suatu repositori (GitHub yang sama atau Google Drive) serta membuat Docker Images ke Docker Hub menggunakan fungsi mlflow build-docker.
