# Step 2 Report — Flood Risk Predictor Model Training

## Objective

Train a real machine-learning model for the Flood Risk Predictor page.

The model replaces the earlier mock/rule-based calculation for the AI Prediction Result area, while Local Weather Forecast remains a separate real-time weather feature.

## Dataset

Input dataset from Step 1:

- `data/processed/flood_risk_clean_full.csv`

Cleaned rows used for training:

- 1,066,034

## Feature columns

| Model Feature | UI Control |
|---|---|
| rainfall | Rainfall Level |
| storm_freq | Weather getting worse? |
| land_drainage | Area Type |
| coastal_risk | Distance to coast |
| river_mgmt | River control |
| dam_quality | Dam condition |
| drainage | Drainage quality |

## Target column

- `flood_probability`

## Model selected

`PolynomialFeatures(degree=2) + Ridge Regression`

Reason:

- Fast to train on a large dataset.
- Stable for deployment in Streamlit.
- Predicts numeric flood probability directly.
- Easy to retrain locally and explain in a university report.

## Evaluation

| Metric | Value |
|---|---:|
| MAE | 0.035666 |
| RMSE | 0.044163 |
| R² Score | 0.256059 |
| Risk-band Accuracy | 0.6844 |
| Macro F1 | 0.3831 |

## Risk thresholds

| Risk Level | Rule |
|---|---|
| Low Risk | probability < 0.45 |
| Medium Risk | 0.45 <= probability < 0.55 |
| High Risk | probability >= 0.55 |

## Output artifacts

- `models/flood_risk_predictor_model.pkl`
- `models/flood_risk_predictor_metadata.json`
- `utils/flood_risk_model_service.py`
- `reports/02_MODEL_TRAINING_METRICS.json`
- `reports/02_SAMPLE_PREDICTIONS.csv`

## Limitation

The available model inputs are only seven processed features. If the team can obtain more environmental features such as water level, soil saturation, elevation, river discharge, historical flood events, and real rainfall time-series, the model can be improved.
