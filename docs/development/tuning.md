# What Optuna does in 3 steps:

## Step 1 — Trial
Optuna suggests a set of hyperparameters:
    n_estimators=350, learning_rate=0.03, max_depth=7...

## Step 2 — Evaluate
Train model with those params, measure val RMSE

## Step 3 — Learn
Optuna sees the result and suggests better params next trial
Repeats 50 times per model, getting smarter each trial

## Expected outcome:
```text
Baseline Random Forest RMSE:  22.23
Tuned Random Forest RMSE:     ~18-20 (estimate)

Baseline XGBoost RMSE:        22.24
Tuned XGBoost RMSE:           ~17-19 (estimate)

Baseline LightGBM RMSE:       22.27
Tuned LightGBM RMSE:          ~17-19 (estimate)
Tree model winner will likely change after tuning — XGBoost or LightGBM often beats Random Forest with optimised params.
```