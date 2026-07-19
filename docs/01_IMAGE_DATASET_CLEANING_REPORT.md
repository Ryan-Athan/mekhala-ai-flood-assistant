# Step 1 - Image Dataset Cleaning Report

## Purpose

This step cleaned and validated the Image Analysis dataset for a 3-class flood image classifier.

## Target classes

- Flood
- Non_Flood
- Unrelated

## Input source folder

`data/raw/image_sources/`

## Cleaning actions

1. Loaded all zip files from `data/raw/image_sources/`.
2. Inferred class labels from zip names.
3. Opened image files using Pillow to verify that they are valid images.
4. Converted valid images to RGB.
5. Resized/cropped images to 224x224.
6. Removed exact duplicate images using SHA-256 hashes.
7. Saved all cleaned images to `data/processed/image_dataset_all_valid_224/`.
8. Created a balanced dataset using the smallest class count.
9. Saved training-ready images to `data/processed/image_dataset_balanced_224/`.

## Cleaning statistics

- Raw zip files: 3
- Raw files inside zips: 4093
- Files tested with Pillow: 4093
- Clean unique images: 4092
- Exact duplicates removed: 1
- Invalid images: 0
- Output image size: 224x224

## Clean class summary

```text
class_name  image_count  min_width  max_width  min_height  max_height  avg_file_size_kb
     Flood          150        284       2560         177        1921            781.00
 Non_Flood         3747        224        224         224         224             11.44
 Unrelated          195         92        162          50         140              4.47
```

## Balanced class counts

```json
{
  "Flood": 150,
  "Non_Flood": 150,
  "Unrelated": 150
}
```

## Main output for Step 2

`data/processed/image_dataset_balanced_224/`

