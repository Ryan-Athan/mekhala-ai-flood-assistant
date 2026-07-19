from __future__ import annotations

import hashlib
import json
import random
import shutil
import zipfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Optional

import pandas as pd
from PIL import Image, ImageOps, UnidentifiedImageError

# ============================================================
# FloodMind Image Dataset Cleaning Script - v7
# Purpose:
#   Merge all existing + new image zip files in:
#       data/raw/image_sources/
#
# Supports your current sources:
#   - flood images 5.zip                 -> Flood
#   - Non Flood Images(1).zip            -> Non_Flood
#   - Unrelated Images(1).zip            -> Unrelated
#   - images 300.zip/Flood/...           -> Flood
#   - images 300.zip/Unflood/...         -> Non_Flood
#   - images 300.zip/Unrelated/...       -> Unrelated
#   - alleyfloodnet.zip/.../flooding/... -> Flood
#   - alleyfloodnet.zip/.../non-flooding -> Non_Flood
#   - roadway_flooding_dataset.zip       -> Flood
#   - natural_images_unrelated.zip       -> Unrelated
#
# Output:
#   data/processed/image_dataset_clean_224/
#   data/processed/image_dataset_balanced_224/
#   data/processed/image_dataset_*_manifest.csv
#   reports/01_IMAGE_DATASET_VALIDATION_REPORT.json
# ============================================================

RANDOM_SEED = 42
IMAGE_SIZE = (224, 224)
VALID_CLASSES = ["Flood", "Non_Flood", "Unrelated"]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}

SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parents[1]

RAW_SOURCE_DIR = PROJECT_ROOT / "data" / "raw" / "image_sources"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
SPLITS_DIR = PROJECT_ROOT / "data" / "splits"
MODELS_DIR = PROJECT_ROOT / "models"

CLEAN_DATASET_DIR = PROCESSED_DIR / "image_dataset_clean_224"
BALANCED_DATASET_DIR = PROCESSED_DIR / "image_dataset_balanced_224"
SAMPLE_PREVIEW_DIR = PROCESSED_DIR / "sample_previews"

CLEAN_MANIFEST_CSV = PROCESSED_DIR / "image_dataset_clean_manifest.csv"
BALANCED_MANIFEST_CSV = PROCESSED_DIR / "image_dataset_balanced_224_manifest.csv"
CLASS_SUMMARY_CSV = PROCESSED_DIR / "image_dataset_class_summary.csv"
CLEANING_STATS_JSON = PROCESSED_DIR / "image_dataset_cleaning_stats.json"
CLASS_MAPPING_JSON = PROCESSED_DIR / "image_class_mapping.json"
VALIDATION_REPORT_JSON = REPORTS_DIR / "01_IMAGE_DATASET_VALIDATION_REPORT.json"
DEBUG_REPORT_JSON = REPORTS_DIR / "01_IMAGE_DATASET_DEBUG_REPORT.json"


@dataclass
class ImageRecord:
    class_name: str
    source_zip: str
    source_member: str
    clean_path: str
    sha256: str
    width: int
    height: int
    original_mode: str
    original_format: str


def ensure_dirs() -> None:
    for path in [RAW_SOURCE_DIR, PROCESSED_DIR, REPORTS_DIR, SPLITS_DIR, MODELS_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def reset_output_dirs() -> None:
    for path in [CLEAN_DATASET_DIR, BALANCED_DATASET_DIR, SAMPLE_PREVIEW_DIR]:
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)

    for class_name in VALID_CLASSES:
        (CLEAN_DATASET_DIR / class_name).mkdir(parents=True, exist_ok=True)
        (BALANCED_DATASET_DIR / class_name).mkdir(parents=True, exist_ok=True)
        (SAMPLE_PREVIEW_DIR / class_name).mkdir(parents=True, exist_ok=True)


def normalize_name(text: str) -> str:
    text = text.lower().strip()
    for ch in ["_", "-", ".", "(", ")", "[", "]", "{", "}", "/", "\\"]:
        text = text.replace(ch, " ")
    return " ".join(text.split())


def class_from_text(text: str) -> Optional[str]:
    """Map a folder/file/zip text fragment to a class.

    Non_Flood checks MUST happen before Flood because strings like
    'non-flooding' contain the word 'flood'.
    """
    name = normalize_name(text)

    non_flood_patterns = [
        "non flood",
        "non flooded",
        "non flooding",
        "nonflood",
        "nonflooded",
        "nonflooding",
        "no flood",
        "not flood",
        "un flood",
        "unflood",
        "unflooded",
        "unflooding",
        "without flood",
        "normal road",
        "normal street",
        "normal",
        "dry road",
        "dry street",
        "dry",
    ]
    unrelated_patterns = [
        "unrelated",
        "natural images",
        "natural image",
        "other",
        "random",
        "irrelevant",
        "unknown",
        "person",
        "people",
        "cat",
        "dog",
        "flower",
        "fruit",
        "airplane",
        "aeroplane",
        "motorbike",
        "motorcycle",
        "bike",
        "car",
        "food",
    ]
    flood_patterns = [
        "flood",
        "flooded",
        "flooding",
        "roadway flooding",
        "road flood",
        "urban flood",
    ]

    if any(pattern in name for pattern in non_flood_patterns):
        return "Non_Flood"
    if any(pattern in name for pattern in unrelated_patterns):
        return "Unrelated"
    if any(pattern in name for pattern in flood_patterns):
        return "Flood"
    return None


def class_from_member_path(member_name: str) -> Optional[str]:
    """Detect class from any folder/file name inside the zip.

    This is important for zips like AlleyFloodNet where the class folder may
    be the 2nd/3rd folder, not the first folder.
    """
    normalized_member = member_name.replace("\\", "/")
    parts = [part for part in normalized_member.split("/") if part]

    # First check each path segment. This avoids one unrelated word hiding in a long path.
    for part in parts:
        detected = class_from_text(part)
        if detected is not None:
            return detected

    # Then check the full member path as backup.
    return class_from_text(normalized_member)


def class_from_zip_name(zip_name: str) -> Optional[str]:
    """Detect class from zip filename only when the filename is reliable."""
    name = normalize_name(zip_name)

    # Strong special cases for your current sources.
    if "natural" in name or "unrelated" in name:
        return "Unrelated"
    if "non flood" in name or "nonflood" in name or "unflood" in name:
        return "Non_Flood"
    if "roadway" in name and "flood" in name:
        return "Flood"
    if name.startswith("flood images"):
        return "Flood"

    # Do NOT let 'alleyfloodnet' force all images to Flood.
    # AlleyFloodNet must be detected by its internal class folders.
    if "alleyfloodnet" in name or "alley flood net" in name:
        return None

    # Generic fallback for simple future zip names like more_flood_images.zip
    if "flood" in name:
        return "Flood"
    return None


def class_from_zip_member(zip_name: str, member_name: str) -> Optional[str]:
    # Prefer internal folder/file labels.
    from_member = class_from_member_path(member_name)
    if from_member is not None:
        return from_member

    # Fall back to zip filename only for reliable zip names.
    return class_from_zip_name(zip_name)


def is_basic_skipped_member(member_name: str) -> bool:
    normalized = member_name.replace("\\", "/")
    lower = normalized.lower()
    filename = Path(normalized).name
    stem = Path(filename).stem.lower()
    suffix = Path(filename).suffix.lower()

    if normalized.endswith("/"):
        return True
    if not filename:
        return True
    if filename.startswith("."):
        return True
    if "__macosx" in lower:
        return True
    if lower.endswith("thumbs.db"):
        return True
    if lower.endswith("desktop.ini"):
        return True

    # Avoid accidentally training on segmentation masks or annotation preview images.
    # We want real camera/photos only.
    mask_words = [
        "/mask/",
        "/masks/",
        "_mask",
        "-mask",
        " mask",
        "/label/",
        "/labels/",
        "/annotation/",
        "/annotations/",
        "ground_truth",
        "ground truth",
        "/gt/",
    ]
    if suffix in IMAGE_EXTENSIONS and any(word in lower for word in mask_words):
        return True
    if suffix in IMAGE_EXTENSIONS and stem in {"mask", "label", "annotation", "gt"}:
        return True

    return False


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def open_image_from_bytes(data: bytes) -> Image.Image:
    image = Image.open(BytesIO(data))
    image.load()
    return image


def convert_to_clean_rgb(image: Image.Image) -> Image.Image:
    image = ImageOps.exif_transpose(image)
    if image.mode != "RGB":
        image = image.convert("RGB")
    image = ImageOps.fit(image, IMAGE_SIZE, method=Image.Resampling.LANCZOS)
    return image


def save_clean_image(image: Image.Image, class_name: str, index: int) -> Path:
    output_path = CLEAN_DATASET_DIR / class_name / f"{class_name}_{index:06d}.jpg"
    image.save(output_path, format="JPEG", quality=92, optimize=True)
    return output_path


def scan_zip_files() -> tuple[pd.DataFrame, dict]:
    zip_files = sorted(RAW_SOURCE_DIR.glob("*.zip"))

    if not zip_files:
        raise FileNotFoundError(
            f"No .zip files found in {RAW_SOURCE_DIR}. Put your image zip files there."
        )

    print("\nFloodMind Image Dataset Cleaning - All Sources v7")
    print("=" * 60)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Raw source folder: {RAW_SOURCE_DIR}")
    print("Zip files found:")
    for zip_path in zip_files:
        print(f"- {zip_path.name}")

    records: list[ImageRecord] = []
    seen_hashes: set[str] = set()
    per_class_index = {class_name: 0 for class_name in VALID_CLASSES}

    stats = {
        "script_version": "v7_all_sources",
        "raw_source_folder": str(RAW_SOURCE_DIR),
        "zip_files": [zip_path.name for zip_path in zip_files],
        "image_size": list(IMAGE_SIZE),
        "total_zip_files": len(zip_files),
        "total_files_inside_zips": 0,
        "total_files_tested": 0,
        "total_valid_images": 0,
        "total_invalid_images": 0,
        "total_duplicates_removed": 0,
        "total_unknown_class_skipped": 0,
        "total_mask_or_label_skipped": 0,
        "zip_details": [],
        "invalid_examples": [],
        "unknown_class_examples": [],
    }

    for zip_path in zip_files:
        zip_detail = {
            "zip_name": zip_path.name,
            "files_inside_zip": 0,
            "files_tested_after_basic_skip_rules": 0,
            "files_with_common_image_extensions": 0,
            "valid_images": 0,
            "invalid_images": 0,
            "duplicates_removed": 0,
            "unknown_class_skipped": 0,
            "class_counts_from_this_zip": {class_name: 0 for class_name in VALID_CLASSES},
            "invalid_examples": [],
            "unknown_class_examples": [],
        }

        print("\n" + "-" * 60)
        print(f"Reading: {zip_path.name}")

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                members = zf.infolist()
                zip_detail["files_inside_zip"] = len(members)
                stats["total_files_inside_zips"] += len(members)

                for member in members:
                    member_name = member.filename

                    if is_basic_skipped_member(member_name):
                        continue

                    zip_detail["files_tested_after_basic_skip_rules"] += 1
                    stats["total_files_tested"] += 1

                    if Path(member_name).suffix.lower() in IMAGE_EXTENSIONS:
                        zip_detail["files_with_common_image_extensions"] += 1

                    class_name = class_from_zip_member(zip_path.name, member_name)
                    if class_name not in VALID_CLASSES:
                        zip_detail["unknown_class_skipped"] += 1
                        stats["total_unknown_class_skipped"] += 1
                        if len(zip_detail["unknown_class_examples"]) < 10:
                            example = f"{zip_path.name} -> {member_name}"
                            zip_detail["unknown_class_examples"].append(example)
                            if len(stats["unknown_class_examples"]) < 50:
                                stats["unknown_class_examples"].append(example)
                        continue

                    try:
                        data = zf.read(member)
                    except Exception as exc:
                        zip_detail["invalid_images"] += 1
                        stats["total_invalid_images"] += 1
                        if len(zip_detail["invalid_examples"]) < 10:
                            example = f"{zip_path.name} -> {member_name} -> read error: {exc}"
                            zip_detail["invalid_examples"].append(example)
                            if len(stats["invalid_examples"]) < 50:
                                stats["invalid_examples"].append(example)
                        continue

                    digest = sha256_bytes(data)
                    if digest in seen_hashes:
                        zip_detail["duplicates_removed"] += 1
                        stats["total_duplicates_removed"] += 1
                        continue

                    try:
                        image = open_image_from_bytes(data)
                        original_width, original_height = image.size
                        original_mode = image.mode
                        original_format = image.format or Path(member_name).suffix.lower().replace(".", "").upper()
                        clean_image = convert_to_clean_rgb(image)
                    except (UnidentifiedImageError, OSError, ValueError, Exception) as exc:
                        zip_detail["invalid_images"] += 1
                        stats["total_invalid_images"] += 1
                        if len(zip_detail["invalid_examples"]) < 10:
                            example = f"{zip_path.name} -> {member_name} -> invalid image: {exc}"
                            zip_detail["invalid_examples"].append(example)
                            if len(stats["invalid_examples"]) < 50:
                                stats["invalid_examples"].append(example)
                        continue

                    seen_hashes.add(digest)
                    per_class_index[class_name] += 1
                    clean_path = save_clean_image(clean_image, class_name, per_class_index[class_name])

                    records.append(
                        ImageRecord(
                            class_name=class_name,
                            source_zip=zip_path.name,
                            source_member=member_name,
                            clean_path=str(clean_path.relative_to(PROJECT_ROOT)),
                            sha256=digest,
                            width=int(original_width),
                            height=int(original_height),
                            original_mode=str(original_mode),
                            original_format=str(original_format),
                        )
                    )

                    zip_detail["valid_images"] += 1
                    zip_detail["class_counts_from_this_zip"][class_name] += 1
                    stats["total_valid_images"] += 1

        except zipfile.BadZipFile as exc:
            example = f"{zip_path.name} -> bad zip file: {exc}"
            zip_detail["invalid_examples"].append(example)
            stats["invalid_examples"].append(example)

        print(f"Files inside zip: {zip_detail['files_inside_zip']}")
        print(f"Files tested after basic skip rules: {zip_detail['files_tested_after_basic_skip_rules']}")
        print(f"Files with common image extensions: {zip_detail['files_with_common_image_extensions']}")
        print(f"Valid images from this zip: {zip_detail['valid_images']}")
        print(f"Invalid images from this zip: {zip_detail['invalid_images']}")
        print(f"Duplicates from this zip: {zip_detail['duplicates_removed']}")
        print(f"Unknown class skipped: {zip_detail['unknown_class_skipped']}")
        print(f"Class counts from this zip: {zip_detail['class_counts_from_this_zip']}")

        if zip_detail["invalid_examples"]:
            print("Invalid examples:")
            for example in zip_detail["invalid_examples"][:5]:
                print(f"  - {example}")
        if zip_detail["unknown_class_examples"]:
            print("Unknown class examples:")
            for example in zip_detail["unknown_class_examples"][:5]:
                print(f"  - {example}")

        stats["zip_details"].append(zip_detail)

    manifest = pd.DataFrame([record.__dict__ for record in records])

    if manifest.empty:
        raise RuntimeError("No valid images found after cleaning. Check your zip files and class folder names.")

    return manifest, stats


def make_class_summary(manifest: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for class_name in VALID_CLASSES:
        cdf = manifest[manifest["class_name"] == class_name].copy()
        width_values = pd.to_numeric(cdf.get("width", pd.Series(dtype=float)), errors="coerce").dropna()
        height_values = pd.to_numeric(cdf.get("height", pd.Series(dtype=float)), errors="coerce").dropna()
        rows.append(
            {
                "class_name": class_name,
                "image_count": int(len(cdf)),
                "min_width": int(width_values.min()) if len(width_values) else 0,
                "max_width": int(width_values.max()) if len(width_values) else 0,
                "min_height": int(height_values.min()) if len(height_values) else 0,
                "max_height": int(height_values.max()) if len(height_values) else 0,
            }
        )
    return pd.DataFrame(rows)


def copy_balanced_dataset(manifest: pd.DataFrame) -> pd.DataFrame:
    counts = {class_name: int((manifest["class_name"] == class_name).sum()) for class_name in VALID_CLASSES}
    missing_classes = [class_name for class_name, count in counts.items() if count == 0]
    if missing_classes:
        raise RuntimeError(
            "One or more required classes has 0 valid images after cleaning.\n"
            f"Class counts: {counts}\n"
            f"Missing classes: {missing_classes}\n"
            "Expected classes are Flood, Non_Flood, Unrelated.\n"
            "Supported folders include Flood, flooding, flooded, Unflood, non-flooding, Non Flood, and Unrelated."
        )

    balance_count = min(counts.values())
    rng = random.Random(RANDOM_SEED)
    balanced_parts = []

    print("\n" + "=" * 60)
    print("Clean class counts:")
    for class_name in VALID_CLASSES:
        print(f"- {class_name}: {counts[class_name]}")
    print(f"\nBalancing dataset to {balance_count} images per class...")

    for class_name in VALID_CLASSES:
        cdf = manifest[manifest["class_name"] == class_name].copy().reset_index(drop=True)
        selected_indices = list(range(len(cdf)))
        rng.shuffle(selected_indices)
        selected_indices = selected_indices[:balance_count]
        selected = cdf.iloc[selected_indices].copy().reset_index(drop=True)

        for output_index, (_, row) in enumerate(selected.iterrows(), start=1):
            source_path = PROJECT_ROOT / row["clean_path"]
            output_path = BALANCED_DATASET_DIR / class_name / f"{class_name}_{output_index:06d}.jpg"
            shutil.copy2(source_path, output_path)
            selected.loc[output_index - 1, "balanced_path"] = str(output_path.relative_to(PROJECT_ROOT))

            if output_index <= 6:
                preview_path = SAMPLE_PREVIEW_DIR / class_name / output_path.name
                shutil.copy2(output_path, preview_path)

        balanced_parts.append(selected)

    balanced_manifest = pd.concat(balanced_parts, ignore_index=True)
    balanced_manifest = balanced_manifest.sample(frac=1.0, random_state=RANDOM_SEED).reset_index(drop=True)
    return balanced_manifest


def create_simple_split_files(balanced_manifest: pd.DataFrame) -> None:
    rng = random.Random(RANDOM_SEED)
    train_rows = []
    val_rows = []
    test_rows = []

    for class_name in VALID_CLASSES:
        cdf = balanced_manifest[balanced_manifest["class_name"] == class_name].copy().reset_index(drop=True)
        indices = list(range(len(cdf)))
        rng.shuffle(indices)
        n = len(indices)
        n_train = int(n * 0.70)
        n_val = int(n * 0.15)

        train_idx = indices[:n_train]
        val_idx = indices[n_train : n_train + n_val]
        test_idx = indices[n_train + n_val :]

        train_rows.append(cdf.iloc[train_idx])
        val_rows.append(cdf.iloc[val_idx])
        test_rows.append(cdf.iloc[test_idx])

    pd.concat(train_rows, ignore_index=True).to_csv(SPLITS_DIR / "image_train_split.csv", index=False)
    pd.concat(val_rows, ignore_index=True).to_csv(SPLITS_DIR / "image_validation_split.csv", index=False)
    pd.concat(test_rows, ignore_index=True).to_csv(SPLITS_DIR / "image_test_split.csv", index=False)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    reset_output_dirs()

    manifest, stats = scan_zip_files()

    class_summary = make_class_summary(manifest)
    balanced_manifest = copy_balanced_dataset(manifest)
    create_simple_split_files(balanced_manifest)

    manifest.to_csv(CLEAN_MANIFEST_CSV, index=False)
    balanced_manifest.to_csv(BALANCED_MANIFEST_CSV, index=False)
    class_summary.to_csv(CLASS_SUMMARY_CSV, index=False)

    class_mapping = {
        "class_to_index": {name: i for i, name in enumerate(VALID_CLASSES)},
        "index_to_class": {str(i): name for i, name in enumerate(VALID_CLASSES)},
    }
    write_json(CLASS_MAPPING_JSON, class_mapping)
    write_json(MODELS_DIR / "image_class_mapping.json", class_mapping)

    final_counts = {class_name: int((manifest["class_name"] == class_name).sum()) for class_name in VALID_CLASSES}
    balanced_counts = {class_name: int((balanced_manifest["class_name"] == class_name).sum()) for class_name in VALID_CLASSES}

    stats.update(
        {
            "clean_class_counts": final_counts,
            "balanced_class_counts": balanced_counts,
            "balanced_images_per_class": min(balanced_counts.values()) if balanced_counts else 0,
            "clean_manifest_csv": str(CLEAN_MANIFEST_CSV.relative_to(PROJECT_ROOT)),
            "balanced_manifest_csv": str(BALANCED_MANIFEST_CSV.relative_to(PROJECT_ROOT)),
            "balanced_dataset_folder": str(BALANCED_DATASET_DIR.relative_to(PROJECT_ROOT)),
        }
    )

    validation_report = {
        "status": "PASS" if all(balanced_counts.get(c, 0) > 0 for c in VALID_CLASSES) else "FAIL",
        "valid_classes": VALID_CLASSES,
        "clean_class_counts": final_counts,
        "balanced_class_counts": balanced_counts,
        "total_clean_images": int(len(manifest)),
        "total_balanced_images": int(len(balanced_manifest)),
        "image_size": list(IMAGE_SIZE),
        "notes": [
            "This script merges all zip files in data/raw/image_sources.",
            "It supports old zips, images 300.zip, AlleyFloodNet, roadway flooding, and natural images.",
            "Exact duplicate images are removed by SHA-256 hash.",
            "The balanced training folder uses the smallest class count after cleaning.",
            "If AlleyFloodNet shows many Unknown class skipped images, check its folder names in the zip.",
        ],
    }

    write_json(CLEANING_STATS_JSON, stats)
    write_json(VALIDATION_REPORT_JSON, validation_report)
    write_json(DEBUG_REPORT_JSON, stats)

    print("\n" + "=" * 60)
    print("Scan complete.")
    print(f"Raw files scanned: {stats['total_files_inside_zips']}")
    print(f"Clean unique images: {len(manifest)}")
    print(f"Exact duplicates removed: {stats['total_duplicates_removed']}")
    print(f"Invalid images: {stats['total_invalid_images']}")
    print(f"Unknown class skipped: {stats['total_unknown_class_skipped']}")

    print("\nClean class counts:")
    for class_name in VALID_CLASSES:
        print(f"- {class_name}: {final_counts[class_name]}")

    print("\nBalanced training-ready class counts:")
    for class_name in VALID_CLASSES:
        print(f"- {class_name}: {balanced_counts[class_name]}")

    print("\nSaved outputs:")
    print(f"- {CLEAN_MANIFEST_CSV}")
    print(f"- {BALANCED_MANIFEST_CSV}")
    print(f"- {BALANCED_DATASET_DIR}")
    print(f"- {VALIDATION_REPORT_JSON}")
    print("\nNext commands for best accuracy:")
    print("python scripts/05_train_resnet18_image_classifier.py")
    print("python scripts/04_test_image_result_calibration.py")


if __name__ == "__main__":
    main()
