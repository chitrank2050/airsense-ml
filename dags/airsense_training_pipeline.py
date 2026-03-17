from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "airsense-ml",
    "depends_on_past": False,
    "start_date": datetime(2025, 1, 1),
    "retries": 0,
}

dag = DAG(
    "airsense_training_pipeline",
    default_args=default_args,
    description="Orchestrates the AirSense ML training pipeline",
    schedule_interval=None,  # Set to '@daily' or similar when ready for automated runs
    catchup=False,
)

# Since we mounted the current directory to /opt/airflow/airsense-ml
# We navigate into the directory and run uv commands. We explicitly use the uv
# binary path if it is not globally available in the container.

# Wait to ensure dependencies are installed (in this containerized environment)
install_deps = BashOperator(
    task_id="install_dependencies",
    bash_command="cd /opt/airflow/airsense-ml && uv sync --all-groups",
    dag=dag,
)

# Run the training pipeline block
train_models = BashOperator(
    task_id="train_models",
    bash_command="cd /opt/airflow/airsense-ml && uv run make train",
    dag=dag,
)

install_deps >> train_models
