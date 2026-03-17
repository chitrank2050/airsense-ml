# Pipeline Orchestration (Apache Airflow)

AirSense ML uses a zero-cost local setup of **Apache Airflow** to orchestrate the end-to-end ML pipeline (`data -> featurize -> train -> evaluate`).

Airflow provides a high-level overview of task dependencies, job failures, and logging.

## Setting Up Airflow Locally

Airflow requires a database (PostgreSQL) and webserver + scheduler components. You do not need to install these heavily into your local environment. Instead, we use `docker-compose`.

### 1. Start the Environment

Ensure Docker is running, then spin up the cluster:

```bash
make airflow
# Select "Start Airflow cluster"
```
*(Alternatively: `make _airflow-up` to run directly)*

This will pull the required images, run database migrations, and create a default admin user.

### 2. Access the Airflow UI

Visit `http://localhost:8080` in your web browser.
- **Username:** `admin`
- **Password:** `admin`

### 3. Run the Training DAG

1. In the DAGs view, find `airsense_training_pipeline`.
2. Toggle the switch to "Unpause" the DAG.
3. Click the "Trigger DAG" (Play) button to manually run the pipeline.

The DAG will install dependencies inside the container and then execute `make train`, allowing you to visually see success or failure states.

## Cleaning Up

When you are done monitoring the pipeline, you can tear down the cluster to free up system resources:

```bash
make airflow
# Select "Stop Airflow cluster"
```
*(Alternatively: `make _airflow-down` to run directly)*
*(The `-v` flag removes the associated volume so you start fresh next time).*
