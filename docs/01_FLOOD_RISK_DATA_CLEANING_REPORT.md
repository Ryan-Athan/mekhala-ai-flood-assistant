# Step 1: Flood Risk Predictor Dataset Cleaning & Validation Report

## Objective
Clean and validate the Flood Risk Predictor tabular dataset before training the real AI prediction model.

## Input Files
- `flood_processed_train_data.xls` uploaded by the team. The extension is `.xls`, but the file content is plain CSV text.
- `flood_data_preprocessing.ipynb`, the team preprocessing notebook.

## Confirmed UI-to-Feature Mapping
| UI Control | Model Feature | Original Notebook Column |
|---|---|---|
| Rainfall Level | `rainfall` | `MonsoonIntensity` |
| Weather getting worse? | `storm_freq` | `ClimateChange` |
| Area Type | `land_drainage` | `TopographyDrainage` |
| Distance to coast | `coastal_risk` | `CoastalVulnerability` |
| River control | `river_mgmt` | `RiverManagement` |
| Dam condition | `dam_quality` | `DamsQuality` |
| Drainage quality | `drainage` | `DrainageSystems` |

## Target Column
- `flood_probability`
- Numeric probability from 0 to 1.

## Cleaning Actions Completed
1. Verified expected 8 columns.
2. Confirmed all features and target are numeric.
3. Removed rows with missing/non-numeric values.
4. Validated `flood_probability` is within 0 to 1.
5. Removed exact duplicate rows.
6. Added `flood_probability_percent`.
7. Added `risk_label` for app display.
8. Added `analysis_band` for data exploration.
9. Generated summary tables and validation reports.

## Cleaning Results
- Raw rows: **1,097,096**
- Final cleaned rows: **1,066,034**
- Invalid rows removed: **0**
- Exact duplicate rows removed: **31,062**
- Validation status: **PASS**

## Risk Label Distribution
| Risk Label | Count |
|---|---:|
| Medium Risk | 1,048,814 |
| Low Risk | 17,072 |
| High Risk | 148 |


## Analysis Band Distribution
| Band | Count |
|---|---:|
| Low Band (<0.45) | 138,180 |
| Middle Band (0.45-0.55) | 714,277 |
| High Band (>=0.55) | 213,577 |


## Important Note
The feature columns are already StandardScaler-standardized. This is confirmed by the team notebook. Step 2 should train the model using these cleaned scaled features.

## Main Output Files
- `data/processed/flood_risk_clean_full.csv`
- `data/processed/flood_risk_clean_sample_5000.csv`
- `data/processed/flood_risk_feature_summary.csv`
- `data/processed/flood_risk_label_summary.csv`
- `data/processed/feature_ui_mapping.json`
- `reports/01_CORRELATION_MATRIX.csv`
- `reports/01_FLOOD_RISK_VALIDATION_REPORT.json`
