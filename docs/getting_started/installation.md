# Installation

This guide covers setting up AirSense ML for local development.

---

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | 3.12+ | [python.org](https://www.python.org/downloads/) |
| uv | latest | `brew install uv` |
| Docker | latest | [docker.com](https://www.docker.com/) |
| Git | latest | [git-scm.com](https://git-scm.com/) |

---

## 1. Clone the Repository

```bash
git clone https://github.com/chitrank2050/airsense-ml.git
cd airsense-ml
```

---

## 2. Create Virtual Environment

```bash
make init
```

This creates `.venv/` using Python 3.12. If you have a `.python-version` file it reads the version from there.

---

## 3. Install Dependencies

**Full install (local development — includes training tools):**

```bash
uv sync --all-groups
```

This installs:

- **Production deps** — FastAPI, scikit-learn, XGBoost, LightGBM, Loguru, Pydantic
- **Training group** — MLflow, Optuna, SHAP, Matplotlib, Seaborn
- **Dev group** — Ruff, pre-commit, Jupyter, questionary

**Production only (API serving, no training tools):**

```bash
make install-prod
```

---

## 4. Install Pre-commit Hooks

```bash
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
```

This installs:
- Ruff linting and formatting on every commit
- Conventional commit message enforcement

---

## 5. Set Up Environment

```bash
cp .env.example .env.dev
```

Open `.env.dev` — defaults work for local development. No changes required to get started.

---

## 6. Download Dataset

Download the Delhi AQI dataset from Kaggle:

[Delhi NCR Air Quality & Pollution Dataset 2020–2025](https://www.kaggle.com/datasets/sohails07/delhi-weather-and-aqi-dataset-2025)

Place the CSV file in `data/raw/`:

```
data/raw/kaggle_delhi_ncr_aqi_dataset.csv
```

---

## 7. Track Data with DVC

```bash
uv run dvc add data/raw
git add data/raw.dvc data/.gitignore
git commit -m "chore: track raw data with DVC"
```

---

## Verify Installation

```bash
make tree        # check project structure
make train       # run training pipeline
make api         # start API server
make docker      # manage Docker images & containers (interactive)
```

If all three run without errors — installation is complete.

---

## Troubleshooting

**`zsh: command not found: dvc`**

DVC is installed in the virtual environment. Use `uv run dvc` or activate the venv:

```bash
source .venv/bin/activate
```

**`brew install libomp` required on macOS**

LightGBM requires OpenMP on macOS:

```bash
brew install libomp
```

**`ModuleNotFoundError: No module named src`**

Make sure you're running from the project root, not inside `src/`:

```bash
cd airsense-ml
uv run python -m src.models.train
```