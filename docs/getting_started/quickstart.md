# Quickstart

Get AirSense ML running in under 10 minutes.

---

## Option A — Docker (fastest)

No Python setup required. Pull and run the pre-built image:

```bash
docker pull chitrank2050/airsense-ml:latest
docker run -p 8000:8000 chitrank2050/airsense-ml:latest
```

Open `http://localhost:8000/docs` — the Swagger UI loads with all endpoints ready to test.

---

## Option B — Local Development

### Step 1 — Train the model

```bash
make train
```

Expected output:

```
Train: (145197, 14) | Val: (16134, 14) | Test: (40333, 14)

Training linear_regression...
Training ridge...
Training lasso...
Training elastic_net...
Training random_forest...
Training xgboost...
Training lightgbm...

Best model: random_forest
Best val RMSE: 22.23
Saved to: models/best_model.pkl
```

Training takes ~3-5 minutes on a modern machine.

### Step 2 — Start the API

```bash
make api
```

### Step 3 — Make your first prediction

```bash
curl -X POST http://127.0.0.1:8000/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "station": "IGI Airport",
    "season": "Winter",
    "latitude": 28.5562,
    "longitude": 77.1000,
    "temperature": 14.5,
    "humidity": 82.0,
    "wind_speed": 3.2,
    "visibility": 2.1,
    "day": 15,
    "month": 1,
    "hour": 8,
    "day_of_week": "Monday",
    "is_weekend": 0
  }'
```

Expected response:

```json
{
  "aqi_predicted": 451.05,
  "aqi_rounded": 451,
  "category": "Severe",
  "model_version": "best_model",
  "prediction_timestamp": "2026-03-16T03:34:55.919237+00:00"
}
```

---

## Explore with Bruno

If you have [Bruno](https://www.usebruno.com/) installed:

1. Open Bruno → **Open Collection**
2. Select the `bruno/` folder in the project root
3. Set environment to **local**
4. Run any request — health check, single prediction, or batch

All requests include automated tests that validate the response structure.

---

## View Experiment Results in MLflow

```bash
make mlflow
```

*Note: You can also use the interactive menu: `make ml` (planned) or explore results via `mlflow`.*

Open `http://127.0.0.1:5000` to see all 7 models compared across RMSE, R², MAE, and RMSLE.

---

## Next Steps

- [API Endpoints](../api/endpoints.md) — full endpoint reference
- [Model Training](../ml/training.md) — how the training pipeline works
- [Feature Engineering](../ml/feature_engineering.md) — what features are used and why