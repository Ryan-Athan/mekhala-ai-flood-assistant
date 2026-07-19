# Flood Risk Predictor Dataset Description

## Purpose
This dataset will be used to train the real AI model for the **Flood Risk Predictor** page.

## Dataset Type
Tabular numeric dataset for flood probability regression.

## Input Features
1. `rainfall`
2. `land_drainage`
3. `river_mgmt`
4. `storm_freq`
5. `dam_quality`
6. `drainage`
7. `coastal_risk`

## Target
- `flood_probability`
- Continuous numeric probability between 0 and 1.

## Preprocessing Status
The uploaded processed training file is already scaled using `StandardScaler`, according to the preprocessing notebook. The original raw columns were selected, renamed, scaled, and exported for model training.

## Next Step
Step 2 should train a regression model to predict `flood_probability` from the 7 features. The app will convert the model output into a percentage and Low/Medium/High risk result.
