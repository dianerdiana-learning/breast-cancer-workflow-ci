from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    RocCurveDisplay,
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.utils import estimator_html_repr

from dotenv import load_dotenv

# load file .env
load_dotenv()

TARGET_COLUMN = "target"
RANDOM_STATE = 42
TEST_SIZE = 0.2


def project_root() -> Path:
    return Path(__file__).resolve().parent


def dataset_path() -> Path:
    return project_root() / "breast_cancer_preprocessed.csv"


def _is_dagshub_mode() -> bool:
    return bool(os.getenv("DAGSHUB_REPO_OWNER") and os.getenv("DAGSHUB_REPO_NAME"))


def configure_tracking() -> None:
    if _is_dagshub_mode():
        import dagshub  # noqa: PLC0415

        dagshub.init(
            repo_owner=os.environ["DAGSHUB_REPO_OWNER"],
            repo_name=os.environ["DAGSHUB_REPO_NAME"],
            mlflow=True,
        )
        return

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
        return

    local_store = (Path(__file__).resolve().parent / "mlruns").resolve()
    local_store.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(local_store.as_uri())


def load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)
    if df.empty:
        raise ValueError("Dataset is empty.")
    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Column '{TARGET_COLUMN}' is missing from dataset.")
    return df


def get_metrics(y_true, y_pred, y_proba=None) -> dict[str, float]:
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred),
        "recall": recall_score(y_true, y_pred),
        "f1": f1_score(y_true, y_pred),
    }

    if y_proba is not None:
        metrics["roc_auc"] = roc_auc_score(y_true, y_proba)

    return metrics


def main() -> None:
    configure_tracking()
    experiment_name = (
        "breast-cancer-advance" if _is_dagshub_mode() else "breast-cancer-tuning-manual"
    )
    mlflow.set_experiment(experiment_name)

    data = load_dataset(dataset_path())
    X = data.drop(columns=[TARGET_COLUMN])
    y = data[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    base_model = LogisticRegression(random_state=RANDOM_STATE)
    param_grid = {
        "C": [0.01, 0.1, 1.0, 10.0],
        "solver": ["liblinear", "lbfgs"],
        "max_iter": [500, 1000],
    }

    search = GridSearchCV(
        estimator=base_model,
        param_grid=param_grid,
        scoring="f1",
        cv=5,
        n_jobs=-1,
    )
    search.fit(X_train, y_train)
    best_model = search.best_estimator_

    y_train_pred = best_model.predict(X_train)
    y_test_pred = best_model.predict(X_test)
    y_train_proba = best_model.predict_proba(X_train)[:, 1]
    y_test_proba = best_model.predict_proba(X_test)[:, 1]

    train_metrics = get_metrics(y_train, y_train_pred, y_train_proba)
    test_metrics = get_metrics(y_test, y_test_pred, y_test_proba)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        metric_info_file = tmp_path / "metric_info.json"
        metric_info_file.write_text(
            json.dumps(
                {
                    "best_cv_score": search.best_score_,
                    "best_params": search.best_params_,
                    "train_metrics": train_metrics,
                    "test_metrics": test_metrics,
                    "classification_report": classification_report(
                        y_test,
                        y_test_pred,
                        output_dict=True,
                    ),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        estimator_file = tmp_path / "estimator.html"
        estimator_file.write_text(estimator_html_repr(best_model), encoding="utf-8")

        cm_file = tmp_path / "training_confusion_matrix.png"
        fig, ax = plt.subplots(figsize=(6, 5))
        disp = ConfusionMatrixDisplay.from_predictions(y_test, y_test_pred, ax=ax)
        disp.ax_.set_title("Confusion Matrix - Best Model")
        fig.tight_layout()
        fig.savefig(cm_file, dpi=150)
        plt.close(fig)

        # Also persist a run artifact folder `model/` matching reviewer checklist.
        model_dir = tmp_path / "model"
        mlflow.sklearn.save_model(best_model, path=str(model_dir))

        # ---------- Additional Advance artifacts ----------
        # 1) ROC Curve
        roc_file = tmp_path / "roc_curve.png"
        fig_roc, ax_roc = plt.subplots(figsize=(6, 5))
        RocCurveDisplay.from_predictions(
            y_test, y_test_proba, ax=ax_roc, name="Best Model"
        )
        ax_roc.set_title("ROC Curve")
        fig_roc.tight_layout()
        fig_roc.savefig(roc_file, dpi=150)
        plt.close(fig_roc)

        # 2) Feature importance (LogReg coefficients)
        feature_names = X.columns.tolist()
        coefs = best_model.coef_[0]
        fi_file = tmp_path / "feature_importance.csv"
        fi_df = pd.DataFrame(
            {
                "feature": feature_names,
                "coefficient": coefs,
                "abs_coefficient": np.abs(coefs),
            }
        ).sort_values("abs_coefficient", ascending=False)
        fi_df.to_csv(fi_file, index=False)
        # -------------------------------------------------

        with mlflow.start_run(run_name="tuning-manual-logreg"):
            mlflow.log_param("model_type", "LogisticRegression")
            mlflow.log_param("cv_folds", 5)
            mlflow.log_param("scoring", "f1")
            mlflow.log_param("param_grid", json.dumps(param_grid))
            mlflow.log_params(search.best_params_)
            mlflow.log_metric("best_cv_score", search.best_score_)

            for key, value in train_metrics.items():
                mlflow.log_metric(f"train_{key}", value)
            for key, value in test_metrics.items():
                mlflow.log_metric(f"test_{key}", value)

            mlflow.sklearn.log_model(best_model, artifact_path="model")
            mlflow.log_artifacts(str(model_dir), artifact_path="model")
            mlflow.log_artifact(str(estimator_file))
            mlflow.log_artifact(str(metric_info_file))
            mlflow.log_artifact(str(cm_file))

            # Advance extra artifacts
            mlflow.log_artifact(str(roc_file))
            mlflow.log_artifact(str(fi_file))

            print("Training Skilled/Advance selesai.")
            print(f"Tracking URI: {mlflow.get_tracking_uri()}")
            print(f"Run ID: {mlflow.active_run().info.run_id}")


if __name__ == "__main__":
    main()
