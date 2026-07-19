# Model Card — Flood Risk Predictor Model

## Model name

FloodMind Flood Risk Predictor Regression Model

## Model type

Polynomial Ridge Regression

## Intended use

Predict flood probability for the Flood Risk Predictor page using the seven environmental/infrastructure slider inputs.

## Inputs

- rainfall
- land_drainage
- river_mgmt
- storm_freq
- dam_quality
- drainage
- coastal_risk

## Output

- `flood_probability`: decimal value from 0 to 1

## Risk conversion

- Low Risk: probability < 0.45
- Medium Risk: 0.45 <= probability < 0.55
- High Risk: probability >= 0.55

## Evaluation summary

- MAE: 0.035666
- RMSE: 0.044163
- R²: 0.256059
- Risk-band accuracy: 0.6844

## Limitations

This model depends on the processed dataset quality. It should support decision-making but should not be treated as an official emergency warning system.
