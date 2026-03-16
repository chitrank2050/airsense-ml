# API Endpoints

All endpoints are versioned under `/v1`. The API is built with FastAPI and validates all requests and responses via Pydantic.

Interactive docs available at `/docs` (Swagger UI) and `/redoc` (ReDoc).

---

## Base URL

| Environment | URL |
|---|---|
| Local | `http://localhost:8000` |
| Docker | `http://localhost:8000` |

---

## Endpoints

### `GET /v1/health`

Check service health and model load status.

**Response:**

```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2026-03-16T03:34:55.850097+00:00"
}
```

| Field | Type | Values |
|---|---|---|
| `status` | string | `healthy` or `degraded` |
| `model_loaded` | boolean | `true` if model is ready |
| `timestamp` | string | UTC ISO timestamp |

`status: degraded` means the service is running but the model failed to load. Run `make train` to generate a model artifact.

---

### `GET /v1/model/info`

Return metadata about the currently loaded model.

**Response:**

```json
{
  "model_version": "best_model",
  "model_path": "/app/models/best_model.pkl",
  "dataset_config": "/app/configs/delhi.yaml",
  "aqi_categories": {
    "0-50": "Good",
    "51-100": "Satisfactory",
    "101-200": "Moderate",
    "201-300": "Poor",
    "301-400": "Very Poor",
    "401-500": "Severe"
  }
}
```

**Status codes:**

| Code | Meaning |
|---|---|
| `200` | Model info returned |
| `503` | Model not loaded |

---

### `POST /v1/predict`

Predict AQI for a single location and time.

**Request body:**

```json
{
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
}
```

**Request fields:**

| Field | Type | Constraints | Description |
|---|---|---|---|
| `station` | string | required | Monitoring station name |
| `season` | string | required | `Winter` / `Summer` / `Monsoon` / `Post-Monsoon` |
| `latitude` | float | required | Station latitude (decimal degrees) |
| `longitude` | float | required | Station longitude (decimal degrees) |
| `temperature` | float | required | Temperature in Celsius |
| `humidity` | float | 0–100 | Relative humidity % |
| `wind_speed` | float | ≥ 0 | Wind speed in km/h |
| `visibility` | float | ≥ 0 | Visibility in km |
| `day` | int | 1–31 | Day of month |
| `month` | int | 1–12 | Month number |
| `hour` | int | 0–23 | Hour of day (24h format) |
| `day_of_week` | string | required | Full day name e.g. `Monday` |
| `is_weekend` | int | 0 or 1 | `1` if Saturday or Sunday |

**Response:**

```json
{
  "aqi_predicted": 451.05,
  "aqi_rounded": 451,
  "category": "Severe",
  "model_version": "best_model",
  "prediction_timestamp": "2026-03-16T03:34:55.919237+00:00"
}
```

**Response fields:**

| Field | Type | Description |
|---|---|---|
| `aqi_predicted` | float | Raw predicted AQI value |
| `aqi_rounded` | int | AQI rounded and clipped to 0–500 |
| `category` | string | CPCB AQI category label |
| `model_version` | string | Model artifact used for prediction |
| `prediction_timestamp` | string | UTC ISO timestamp of prediction |

**Status codes:**

| Code | Meaning |
|---|---|
| `200` | Prediction successful |
| `422` | Request validation failed — check field constraints |
| `500` | Inference failed unexpectedly |
| `503` | Model not loaded |

---

### `POST /v1/predict/batch`

Predict AQI for multiple inputs in a single call. Returns predictions in the same order as inputs.

**Request body:**

```json
{
  "requests": [
    {
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
    },
    {
      "station": "Okhla",
      "season": "Winter",
      "latitude": 28.5355,
      "longitude": 77.2720,
      "temperature": 13.8,
      "humidity": 85.0,
      "wind_speed": 2.8,
      "visibility": 1.9,
      "day": 15,
      "month": 1,
      "hour": 8,
      "day_of_week": "Monday",
      "is_weekend": 0
    }
  ]
}
```

**Constraints:**

- Minimum 1 request per call
- Maximum 100 requests per call

**Response:**

```json
{
  "predictions": [
    {
      "aqi_predicted": 451.05,
      "aqi_rounded": 451,
      "category": "Severe",
      "model_version": "best_model",
      "prediction_timestamp": "2026-03-16T03:34:55Z"
    },
    {
      "aqi_predicted": 478.32,
      "aqi_rounded": 478,
      "category": "Severe",
      "model_version": "best_model",
      "prediction_timestamp": "2026-03-16T03:34:55Z"
    }
  ],
  "count": 2
}
```

**Status codes:**

| Code | Meaning |
|---|---|
| `200` | All predictions successful |
| `422` | Any request in batch failed validation |
| `500` | Any inference failed |
| `503` | Model not loaded |

---

## AQI Categories (CPCB India)

| Range | Category | Health Implication |
|---|---|---|
| 0–50 | Good | Minimal impact |
| 51–100 | Satisfactory | Minor breathing discomfort for sensitive people |
| 101–200 | Moderate | Discomfort for people with lung/heart disease |
| 201–300 | Poor | Breathing discomfort for most people |
| 301–400 | Very Poor | Serious breathing discomfort, avoid outdoors |
| 401–500 | Severe | Health emergency, avoid all outdoor activity |

---

## Known Limitations

- `aqi_capped` feature defaults to `0` at inference time. The model may slightly underestimate AQI during peak winter pollution events (October–February) where true AQI exceeds 500.
- Predictions are for Delhi stations only in the current version. Multi-city support is planned for Phase 6.