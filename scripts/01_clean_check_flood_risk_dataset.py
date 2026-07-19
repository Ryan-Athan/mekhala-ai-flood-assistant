from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path
from datetime import datetime

RAW_PATH = Path("data/raw/flood_risk/flood_processed_train_data.csv")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_COLUMNS = ["rainfall", "land_drainage", "river_mgmt", "storm_freq", "dam_quality", "drainage", "coastal_risk", "flood_probability"]
FEATURE_COLUMNS = EXPECTED_COLUMNS[:-1]

def risk_label(probability: float) -> str:
    if probability < 0.40:
        return "Low Risk"
    if probability < 0.70:
        return "Medium Risk"
    return "High Risk"

def analysis_band(probability: float) -> str:
    if probability < 0.45:
        return "Low Band (<0.45)"
    if probability < 0.55:
        return "Middle Band (0.45-0.55)"
    return "High Band (>=0.55)"

def main() -> None:
    cleaned_path = OUT_DIR / "flood_risk_clean_full.csv"
    sample_path = OUT_DIR / "flood_risk_clean_sample_5000.csv"
    stats = {"created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z", "source_file": str(RAW_PATH), "raw_rows": 0, "valid_rows": 0, "invalid_rows": 0, "duplicate_rows_removed": 0, "missing_or_non_numeric_by_column": {c: 0 for c in EXPECTED_COLUMNS}, "target_out_of_range_rows": 0}
    seen = set()
    out_cols = EXPECTED_COLUMNS + ["flood_probability_percent", "risk_label", "analysis_band"]
    with RAW_PATH.open(newline="", encoding="utf-8", errors="replace") as f_in, cleaned_path.open("w", newline="", encoding="utf-8") as f_out, sample_path.open("w", newline="", encoding="utf-8") as f_sample:
        reader = csv.DictReader(f_in)
        writer = csv.DictWriter(f_out, fieldnames=out_cols)
        sample_writer = csv.DictWriter(f_sample, fieldnames=out_cols)
        writer.writeheader(); sample_writer.writeheader()
        for row in reader:
            stats["raw_rows"] += 1
            parsed = {}
            ok = True
            for col in EXPECTED_COLUMNS:
                try:
                    parsed[col] = float((row.get(col, "") or "").strip())
                except Exception:
                    stats["missing_or_non_numeric_by_column"][col] += 1
                    ok = False
            if not ok:
                stats["invalid_rows"] += 1
                continue
            prob = parsed["flood_probability"]
            if not (0 <= prob <= 1):
                stats["target_out_of_range_rows"] += 1
                stats["invalid_rows"] += 1
                continue
            key = tuple(f"{parsed[c]:.12g}" for c in EXPECTED_COLUMNS)
            if key in seen:
                stats["duplicate_rows_removed"] += 1
                continue
            seen.add(key)
            out = {c: f"{parsed[c]:.15g}" for c in EXPECTED_COLUMNS}
            out["flood_probability_percent"] = f"{prob * 100:.2f}"
            out["risk_label"] = risk_label(prob)
            out["analysis_band"] = analysis_band(prob)
            writer.writerow(out)
            if stats["valid_rows"] < 5000:
                sample_writer.writerow(out)
            stats["valid_rows"] += 1
    stats["validation_status"] = "PASS" if stats["valid_rows"] > 0 and stats["invalid_rows"] == 0 else "CHECK"
    (OUT_DIR / "flood_risk_cleaning_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()
