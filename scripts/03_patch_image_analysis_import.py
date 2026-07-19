from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGE_ANALYSIS_PATH = PROJECT_ROOT / "tabs" / "image_analysis.py"

OLD_IMPORT = "from utils.mock_ai import analyze_uploaded_image"
NEW_IMPORT = "from utils.image_model_service import analyze_uploaded_image"


def main() -> None:
    if not IMAGE_ANALYSIS_PATH.exists():
        raise FileNotFoundError(f"Cannot find {IMAGE_ANALYSIS_PATH}")

    text = IMAGE_ANALYSIS_PATH.read_text(encoding="utf-8")

    if NEW_IMPORT in text:
        print("Image Analysis page is already connected to the real image model.")
        return

    if OLD_IMPORT not in text:
        raise RuntimeError(
            "Could not find the old import line. Open tabs/image_analysis.py and manually replace:\n"
            f"  {OLD_IMPORT}\n"
            "with:\n"
            f"  {NEW_IMPORT}"
        )

    updated = text.replace(OLD_IMPORT, NEW_IMPORT, 1)
    IMAGE_ANALYSIS_PATH.write_text(updated, encoding="utf-8")

    print("Step 3 patch complete.")
    print(f"Updated: {IMAGE_ANALYSIS_PATH}")
    print(f"Replaced: {OLD_IMPORT}")
    print(f"With:     {NEW_IMPORT}")


if __name__ == "__main__":
    main()
