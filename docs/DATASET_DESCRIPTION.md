# Dataset Description — AI Flood Assistant

## Dataset

The AI Flood Assistant uses the Disaster Response Messages dataset provided in `archive.zip`.

## Raw files

- `disaster_messages.csv`: contains message text, original text, and message genre.
- `disaster_categories.csv`: contains semicolon-separated disaster category labels for each message ID.

## Cleaned files

### `clean_disaster_messages_full.csv`

Full cleaned dataset with parsed binary label columns.

Important columns:

- `id`
- `message`
- `message_clean`
- `message_clean_lower`
- `original`
- `original_clean`
- `genre`
- `message_word_count`
- `active_label_count`
- `active_labels`
- category label columns such as `related`, `request`, `aid_related`, `weather_related`, `floods`, etc.

### `clean_flood_disaster_chatbot_messages.csv`

A flood/disaster-relevant subset prepared for later chatbot training. Rows are selected using flood-related category labels and flood-related keywords.

## Cleaned dataset statistics

- Full cleaned rows: 26137
- Flood/disaster chatbot-relevant rows: 15854
- Category labels after cleaning: 35

## Purpose in project

This cleaned dataset will be used to train a flood/disaster intent classification model for the AI Flood Assistant. The model will classify user messages into disaster-related categories and then return flood-safety guidance from a knowledge base.
