# FloodMind Project Log

## Step 1 — Dataset Cleaning

Dataset: Kaggle Disaster Response Messages dataset

Actions completed:

- Loaded disaster messages and categories
- Parsed category labels
- Fixed invalid category values
- Removed duplicates and empty text
- Created cleaned full dataset
- Created flood/disaster-chatbot subset

Main outputs:

```text
data/processed/clean_disaster_messages_full.csv
data/processed/clean_flood_disaster_chatbot_messages.csv
```

## Step 2 — Flood/Disaster Intent Classifier Training

Date: 2026-07-09T04:51:55.660513Z

Actions completed:

- Loaded cleaned flood/disaster chatbot dataset
- Converted multi-label disaster categories into one chatbot routing intent
- Created `primary_intent` target label
- Trained TF-IDF + LinearSVC model
- Evaluated model on 20% test split
- Saved trained classifier, metadata, mapping rules, and reports

Model output:

```text
models/flood_disaster_intent_classifier.pkl
```

Metrics:

```text
Accuracy: 0.5661
Balanced Accuracy: 0.5582
Macro F1: 0.5384
Weighted F1: 0.5621
```

Next planned step:

```text
Step 3 — Build flood-safety knowledge base
```
