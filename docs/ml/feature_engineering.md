# Feature Engineering

AirSense ML uses weather and temporal features to predict AQI. The key engineering challenge is representing time correctly and avoiding data leakage.

---

## Feature Set

After leakage removal, the model uses 15 features across three categories:

### Numerical Features (StandardScaler applied)

| Feature | Description | Engineering |
|---|---|---|
| `temperature` | Celsius | Raw |
| `humidity` | Relative humidity % | Raw |
| `wind_speed` | km/h | Raw |
| `visibility` | km | Raw |
| `latitude` | Station latitude | Raw |
| `longitude` | Station longitude | Raw |
| `hour_sin` | Sine of hour | Cyclical encoding |
| `hour_cos` | Cosine of hour | Cyclical encoding |
| `month_sin` | Sine of month | Cyclical encoding |
| `month_cos` | Cosine of month | Cyclical encoding |
| `dow_sin` | Sine of day of week | Cyclical encoding |
| `dow_cos` | Cosine of day of week | Cyclical encoding |

### Categorical Features (OneHotEncoder applied)

| Feature | Description | Values |
|---|---|---|
| `season` | Season name | Winter / Summer / Monsoon / Post-Monsoon |
| `station` | Monitoring station | IGI Airport, Okhla, etc. |

### Ordinal Features (Passthrough)

| Feature | Description | Range |
|---|---|---|
| `day` | Day of month | 1–31 |
| `is_weekend` | Weekend flag | 0 or 1 |
| `aqi_capped` | Sensor ceiling flag | 0 or 1 |

---

## Cyclical Encoding

Hour, month, and day of week are all cyclical — hour 23 and hour 0 are one hour apart, but numerically they're 23 apart. A model treating them as raw integers learns the wrong relationship.

Cyclical encoding maps each value onto a circle using sine and cosine:

```python
# Hour (0–23 cycle)
df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)

# Month (1–12 cycle)
df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

# Day of week (0–6 cycle)
df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)
```

Two values (sin + cos) are needed to uniquely represent each position on the circle. Using sin alone is insufficient — sin(0) and sin(π) are both 0, which would make midnight and noon identical.

**Result:** The model correctly understands that December → January is a continuous transition, not a jump from 12 back to 1.

---

## Why Not Month as a Raw Integer?

Without cyclical encoding:

```
January  = 1
December = 12
Gap between them = 11
```

With cyclical encoding:

```
January  = (sin: 0.00, cos: 1.00)
December = (sin: -0.50, cos: 0.87)
Distance ≈ 0.54  — correctly close
```

This matters for AQI because the worst pollution is in November–January — spanning the year boundary. Raw month encoding would make the model think November (11) and January (1) are far apart.

---

## Why StandardScaler on Numerical Features?

Linear models require feature scaling — without it, temperature (range: -5 to 45) dominates humidity (range: 0 to 100) simply due to magnitude differences.

Tree models are scale-invariant — scaling has no effect on their predictions. But since the same pipeline serves both model families, scaling is applied uniformly. It costs nothing for tree models and is required for linear models.

---

## Why OneHotEncoder on Station and Season?

`station` and `season` are nominal categorical variables — there's no natural ordering between IGI Airport and Okhla, or between Winter and Summer.

OrdinalEncoder would imply `Winter < Summer < Monsoon` which is meaningless. OneHotEncoder creates a binary column per category, treating each as independent.

`handle_unknown='ignore'` ensures the API doesn't crash if a new station name appears at inference time.

---

## What Was Excluded and Why

| Column | Reason Excluded |
|---|---|
| `pm25`, `pm10`, `no2`, `so2`, `co`, `o3` | Leakage — components of AQI formula |
| `aqi_category` | Leakage — derived directly from AQI |
| `datetime`, `date` | Replaced by granular time features |
| `year` | No predictive value for future forecasting |
| `city` | Single city dataset — zero variance |

---

## sklearn Pipeline

All transformations are encapsulated in a `ColumnTransformer`:

```python
ColumnTransformer(
    transformers=[
        ("numerical", StandardScaler(), numerical_features),
        ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ("ordinal", "passthrough", ordinal_features),
    ],
    remainder="drop"  # safety — drops any unlisted columns
)
```

`remainder="drop"` ensures no accidental leakage if new columns appear in the data. The transformer is serialised as part of the full pipeline artifact — guaranteeing identical transformations at training and inference time.