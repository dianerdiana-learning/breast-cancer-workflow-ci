# breast-cancer-workflow-ci

Workflow ini memenuhi Kriteria 3 dengan menjalankan retraining model melalui MLflow Project, mengunggah artefak hasil training ke GitHub Actions, lalu membangun Docker image dari model terbaru untuk dipush ke Docker Hub.

## Struktur penting

- `MLProject/MLproject`: entry point MLflow Project untuk retraining.
- `MLProject/modelling.py`: training script yang menghasilkan model, metrics, dan artefak visual.
- `.github/workflows/retrain-mlflow.yml`: workflow CI untuk retraining, upload artefak, dan build Docker image.
- `MLProject/outputs`: folder output stabil yang dipakai CI setelah training berjalan.

## Trigger workflow

Workflow akan berjalan saat:

- ada `push` ke branch `main` atau `master`
- ada `pull_request` ke branch `main` atau `master`
- dipicu manual melalui `workflow_dispatch`

## Artefak yang dihasilkan

Job retraining mengunggah dua artifact GitHub Actions:

- `mlflow-training-output`: model, metric info, confusion matrix, ROC curve, feature importance, dan `latest_run.json`
- `mlflow-run-store`: folder `mlruns` untuk bukti run MLflow

## Secrets yang wajib diisi

Untuk memenuhi level Advance, isi GitHub Secrets berikut:

- `DOCKERHUB_USERNAME`: username Docker Hub
- `DOCKERHUB_TOKEN`: access token Docker Hub
- `DOCKERHUB_REPO`: nama repo lengkap Docker Hub, misalnya `username/breast-cancer-mlflow-ci`

Jika salah satu secret belum ada, job Docker akan gagal dengan pesan yang jelas.

## Cara menjalankan lokal

```bash
pip install -r MLProject/requirements.txt
mlflow run MLProject --env-manager local -e train
```

Hasil training lokal akan tersedia di folder `MLProject/outputs` dan metadata run terbaru tersimpan di `MLProject/outputs/latest_run.json`.
