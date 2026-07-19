# FloodMind Project Log

## Step 1 — Dataset Cleaning for AI Flood Assistant

Date: 2026-07-09

### Goal

Prepare the Kaggle Disaster Response Messages dataset for the AI Flood Assistant chatbot.

### Input files

- `data/raw/disaster_response/disaster_messages.csv`
- `data/raw/disaster_response/disaster_categories.csv`

### Actions completed

- Loaded raw messages and category files.
- Removed duplicate IDs.
- Parsed the `categories` column into binary category label columns.
- Fixed non-binary `related=2` values by converting them to `related=1`.
- Dropped labels with zero positive examples: `child_alone`.
- Cleaned text by normalizing whitespace and replacing URLs/emails.
- Removed empty and duplicate normalized messages.
- Created a flood/disaster chatbot-relevant subset.
- Saved cleaning statistics and a label summary.

### Output files

- `data/processed/clean_disaster_messages_full.csv`
- `data/processed/clean_flood_disaster_chatbot_messages.csv`
- `data/processed/label_summary.csv`
- `data/processed/cleaning_stats.json`
- `docs/01_DATA_CLEANING_REPORT.md`

### Results

- Final cleaned full dataset rows: **26137**
- Flood/disaster chatbot-relevant rows: **15854**
- Usable category labels: **35**

### Next step

Train a flood/disaster intent classifier using the cleaned dataset.

## Image Analysis Step 1: Dataset Cleaning

Cleaned and validated a 3-class image dataset for Flood, Non_Flood, and Unrelated classes. Generated balanced 224x224 RGB images for Step 2 model training.
