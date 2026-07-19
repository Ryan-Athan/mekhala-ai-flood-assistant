from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1] if Path(__file__).parent.name == "scripts" else Path.cwd()
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "disaster_response"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

MESSAGES_PATH = RAW_DIR / "disaster_messages.csv"
CATEGORIES_PATH = RAW_DIR / "disaster_categories.csv"

FLOOD_FOCUS_LABELS = [
    "floods", "weather_related", "storm", "water", "shelter", "buildings", "electricity",
    "transport", "infrastructure_related", "medical_help", "medical_products", "search_and_rescue",
    "request", "aid_related", "direct_report",
]

FLOOD_KEYWORDS = re.compile(
    r"\b(flood|flooding|flooded|rain|rainfall|storm|hurricane|river|water|drainage|shelter|evacuat|rescue|road|bridge|electric|power|dam)\b",
    re.IGNORECASE,
)

_url_re = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_html_re = re.compile(r"<[^>]+>")
_email_re = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")
_multi_space_re = re.compile(r"\s+")


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).replace("\u00a0", " ")
    text = _html_re.sub(" ", text)
    text = _url_re.sub(" URL ", text)
    text = _email_re.sub(" EMAIL ", text)
    text = text.replace("\\n", " ").replace("\n", " ").replace("\r", " ")
    text = _multi_space_re.sub(" ", text).strip()
    return text


def main() -> None:
    messages_raw = pd.read_csv(MESSAGES_PATH)
    categories_raw = pd.read_csv(CATEGORIES_PATH)

    stats = {
        "cleaned_at_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "raw_messages_rows": int(len(messages_raw)),
        "raw_categories_rows": int(len(categories_raw)),
        "duplicate_message_ids_removed": int(messages_raw.duplicated("id").sum()),
        "duplicate_category_ids_removed": int(categories_raw.duplicated("id").sum()),
    }

    messages = messages_raw.drop_duplicates(subset="id", keep="first").copy()
    categories = categories_raw.drop_duplicates(subset="id", keep="first").copy()

    category_split = categories["categories"].str.split(";", expand=True)
    category_names = [str(value).rsplit("-", 1)[0] for value in category_split.iloc[0].tolist()]
    category_values = category_split.apply(lambda col: col.str.rsplit("-", n=1).str[1].astype(int))
    category_values.columns = category_names

    stats["related_value_counts_before_fix"] = {
        str(k): int(v) for k, v in category_values["related"].value_counts(dropna=False).to_dict().items()
    }
    category_values["related"] = category_values["related"].replace(2, 1)

    positive_counts = category_values.sum(axis=0)
    empty_labels = [label for label, count in positive_counts.items() if int(count) == 0]
    category_values = category_values.drop(columns=empty_labels, errors="ignore")
    stats["empty_labels_dropped"] = empty_labels

    clean = messages.merge(
        pd.concat([categories[["id"]].reset_index(drop=True), category_values.reset_index(drop=True)], axis=1),
        on="id",
        how="inner",
    )

    label_cols = list(category_values.columns)
    clean["message_clean"] = clean["message"].map(clean_text)
    clean["original_clean"] = clean["original"].map(clean_text) if "original" in clean.columns else ""
    clean["message_clean_lower"] = clean["message_clean"].str.lower()

    empty_text_mask = clean["message_clean"].str.len() == 0
    stats["empty_messages_removed"] = int(empty_text_mask.sum())
    clean = clean.loc[~empty_text_mask].copy()

    clean["message_word_count"] = clean["message_clean"].str.split().map(len)
    clean["active_label_count"] = clean[label_cols].sum(axis=1).astype(int)
    clean["active_labels"] = clean[label_cols].apply(
        lambda row: ";".join([col for col, val in row.items() if int(val) == 1]), axis=1
    )

    before_message_dedup = len(clean)
    clean = clean.sort_values(["message_clean_lower", "active_label_count"], ascending=[True, False])
    clean = clean.drop_duplicates(subset="message_clean_lower", keep="first").copy()
    clean = clean.sort_values("id").reset_index(drop=True)
    stats["duplicate_normalized_messages_removed"] = int(before_message_dedup - len(clean))
    stats["final_clean_rows"] = int(len(clean))

    flood_focus_labels = [label for label in FLOOD_FOCUS_LABELS if label in clean.columns]
    label_focus_mask = clean[flood_focus_labels].sum(axis=1) > 0 if flood_focus_labels else False
    keyword_focus_mask = clean["message_clean"].str.contains(FLOOD_KEYWORDS, regex=True, na=False)
    clean["is_flood_chatbot_relevant"] = (label_focus_mask | keyword_focus_mask).astype(int)
    flood_focus = clean.loc[clean["is_flood_chatbot_relevant"] == 1].copy()
    stats["flood_focus_rows"] = int(len(flood_focus))
    stats["flood_focus_labels_used"] = flood_focus_labels

    front_cols = [
        "id", "message", "message_clean", "message_clean_lower", "original", "original_clean", "genre",
        "message_word_count", "active_label_count", "active_labels", "is_flood_chatbot_relevant"
    ]
    front_cols = [col for col in front_cols if col in clean.columns]
    remaining_cols = [col for col in clean.columns if col not in front_cols]

    clean[front_cols + remaining_cols].to_csv(PROCESSED_DIR / "clean_disaster_messages_full.csv", index=False)
    flood_focus[front_cols + remaining_cols].to_csv(PROCESSED_DIR / "clean_flood_disaster_chatbot_messages.csv", index=False)

    label_summary = []
    for label in label_cols:
        positives = int(clean[label].sum())
        label_summary.append({
            "label": label,
            "positive_count": positives,
            "positive_rate": round(positives / len(clean), 6) if len(clean) else 0,
        })
    label_summary_df = pd.DataFrame(label_summary).sort_values("positive_count", ascending=False)
    label_summary_df.to_csv(PROCESSED_DIR / "label_summary.csv", index=False)

    stats["final_genre_distribution"] = {str(k): int(v) for k, v in clean["genre"].value_counts().to_dict().items()}
    stats["top_15_labels_after_cleaning"] = label_summary_df.head(15).to_dict(orient="records")
    (PROCESSED_DIR / "cleaning_stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")

    print("Cleaning complete.")
    print(f"Full clean dataset: {PROCESSED_DIR / 'clean_disaster_messages_full.csv'}")
    print(f"Flood chatbot subset: {PROCESSED_DIR / 'clean_flood_disaster_chatbot_messages.csv'}")
    print(f"Final rows: {stats['final_clean_rows']}")
    print(f"Flood chatbot relevant rows: {stats['flood_focus_rows']}")


if __name__ == "__main__":
    main()
