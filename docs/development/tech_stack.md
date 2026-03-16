## Tech Stack

MLOps pipeline for air quality prediction.

## Table of status of each step
| Step                  | Tool                              | Status          |
|-----------------------|-----------------------------------|-----------------|
| Package Manager       | uv                                | ✅ Done         |
| Data Storage          | CSV → Parquet                     | 🔶 CSV only     |
| Data Processing       | Pandas                            | ✅ Done         |
| Data Versioning       | DVC                               | ✅ Done         |
| Data Validation       | Great Expectations                | ❌ Not started  |
| Feature Store         | Local Parquet                     | ❌ Not started  |
| Experiment Tracking   | MLflow                            | ✅ Done         |
| Orchestration         | Python scripts                    | ✅ Done         |
| Model Training        | Scikit-learn + XGBoost + LightGBM | ✅ Done         |
| Hyperparameter Tuning | Optuna                            | ❌ Not started  |
| Model Registry        | MLflow                            | ✅ Done         |
| Model Serving         | FastAPI + Docker                  | ✅ Done         |
| Monitoring            | Evidently                         | ❌ Not started  |
| Cloud Deploy          | Render / Railway                  | ✅ Done         |


## Table for comparison of local vs production tech stack for MLOps
| Step                  | Local or Free Tool                 | Production Equivalent |
|-----------------------|------------------------------------|-----------------------|
| Package Manager       | uv                                 | Same                  |
| Data Storage          | CSV → Parquet                      | S3 + Delta Lake       |
| Data Processing       | Pandas                             | Apache Spark          |
| Data Versioning       | DVC                                | Delta Lake / LakeFS   |
| Data Validation       | Great Expectations                 | Same                  |
| Feature Store         | Local Parquet                      | Feast / Tecton        |
| Experiment Tracking   | MLflow                             | Same / W&B / Neptune  |
| Orchestration         | Python scripts                     | Apache Airflow        |
| Model Training        | Scikit-learn + XGBoost + LightGBM  | Same + Ray / Dask     |
| Hyperparameter Tuning | Optuna                             | Same                  |
| Model Registry        | MLflow                             | SageMaker / Kubeflow  |
| Model Serving         | FastAPI + Docker                   | KServe / Seldon       |
| Monitoring            | Evidently                          | Arize / Fiddler       |
| Cloud Deploy          | Render / Railway                   | AWS / GCP / Azure     |