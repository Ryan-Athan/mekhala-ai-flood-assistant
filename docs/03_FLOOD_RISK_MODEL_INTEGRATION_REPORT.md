# Step 3 — Flood Risk Predictor Model Integration Report

## Goal
Connect the trained Flood Risk Predictor model to the Streamlit **Flood Risk Predictor** page without changing the visual UI design.

## Integrated Files

```text
models/flood_risk_predictor_model.pkl
models/flood_risk_predictor_metadata.json
data/processed/flood_risk_feature_quantiles.csv
utils/flood_risk_model_service.py
tabs/flood_risk_predictor.py
components/fm_risk_controls/index.html
```

## What Changed

The previous page used `_predict_with_mock_model()` for the AI Prediction Result. In this Step 3 package, `_calculate_result()` now calls:

```python
from utils.flood_risk_model_service import predict_flood_risk_from_ui
st.session_state.prediction_result = predict_flood_risk_from_ui(st.session_state.frp_inputs)
```

The **Local Weather Forecast** card is not used by the ML prediction and remains separate.

## Data Flow

```text
Custom slider component
→ st.session_state.frp_inputs
→ predict_flood_risk_from_ui()
→ UI slider values mapped to dataset feature quantiles
→ trained model predicts flood_probability
→ probability converted to Low / Medium / High Risk
→ AI Prediction Result and Emergency Actions update
```

## UI-to-Model Feature Mapping

| UI Control | Model Feature |
|---|---|
| Rainfall Level | rainfall |
| Weather getting worse? | storm_freq |
| Area Type | land_drainage |
| Distance to coast | coastal_risk |
| River control | river_mgmt |
| Dam condition | dam_quality |
| Drainage quality | drainage |

## Model Used

```text
Polynomial Ridge Regression
```

Target:

```text
flood_probability
```

## Metrics From Step 2

```text
MAE: 0.03566595911979675
RMSE: 0.04416322456626424
R²: 0.2560592293739319
Risk-band accuracy: 0.6844475087590933
```

## Notes

- The model predicts flood probability from the 7 environmental/infrastructure inputs only.
- The weather card is real-time display information and is intentionally kept separate from this model.
- If your local scikit-learn version shows warning messages for `.pkl` files, retrain locally with `scripts/02_train_flood_risk_predictor_model.py` from Step 2.
