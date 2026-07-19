# Step 1 — Disaster Response Dataset Cleaning Report

## Dataset source

- Dataset file provided by project team: `archive.zip`
- Extracted files:
  - `data/raw/disaster_response/disaster_messages.csv`
  - `data/raw/disaster_response/disaster_categories.csv`

This dataset is used for the **AI Flood Assistant** chatbot module. It is not a question-answer dataset; it is a real disaster-message classification dataset. We clean it first so it can be used later to train a disaster/flood intent classifier.

## Raw dataset overview

| Item | Count |
|---|---:|
| Raw message rows | 26248 |
| Raw category rows | 26248 |
| Duplicate message IDs removed | 68 |
| Duplicate category IDs removed | 68 |
| Rows after ID de-duplication and merge | 26180 |

## Cleaning operations performed

1. Loaded `disaster_messages.csv` and `disaster_categories.csv`.
2. Removed duplicate `id` rows before merging to prevent duplicate cross-join records.
3. Split the `categories` string column into separate binary label columns.
4. Fixed the `related` label because the raw dataset contains value `2`; it was converted to `1` so all labels are binary.
5. Dropped labels with no positive examples. Dropped labels: `child_alone`.
6. Merged messages and category labels by `id`.
7. Cleaned message text:
   - removed HTML tags,
   - normalized whitespace,
   - replaced URLs with `URL`,
   - replaced emails with `EMAIL`,
   - created lowercase normalized text for ML training.
8. Removed empty messages.
9. Removed duplicate normalized messages and kept the version with more active category labels.
10. Created a flood/disaster chatbot subset using flood-relevant labels and flood-related keywords.

## Final cleaned output

| Output | Rows |
|---|---:|
| Full cleaned disaster dataset | 26137 |
| Flood/disaster chatbot-relevant subset | 15854 |
| Number of usable category labels | 35 |

## Genre distribution after cleaning

| Genre | Count |
|---|---:|
| news | 13035 |
| direct | 10724 |
| social | 2378 |

## Top labels after cleaning

| Label | Positive count | Positive rate |
|---|---:|---:|
| related | 20047 | 0.766997 |
| aid_related | 10839 | 0.414699 |
| weather_related | 7282 | 0.278609 |
| direct_report | 5060 | 0.193595 |
| request | 4463 | 0.170754 |
| other_aid | 3440 | 0.131614 |
| food | 2917 | 0.111604 |
| earthquake | 2448 | 0.09366 |
| storm | 2440 | 0.093354 |
| shelter | 2308 | 0.088304 |
| floods | 2149 | 0.082221 |
| medical_help | 2081 | 0.079619 |
| infrastructure_related | 1704 | 0.065195 |
| water | 1669 | 0.063856 |
| other_weather | 1376 | 0.052646 |

## Files created

- `data/processed/clean_disaster_messages_full.csv`
- `data/processed/clean_flood_disaster_chatbot_messages.csv`
- `data/processed/label_summary.csv`
- `data/processed/cleaning_stats.json`
- `scripts/01_clean_disaster_dataset.py`

## Notes for the next step

The next step is to train a flood/disaster intent classifier using `clean_flood_disaster_chatbot_messages.csv` or the full multilabel dataset. For chatbot response quality, the classifier should be connected to a flood-safety knowledge base instead of directly returning raw disaster messages.
