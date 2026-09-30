
from __future__ import annotations

import base64
import hashlib
import io
from html import escape
from textwrap import dedent
from typing import Any

import streamlit as st

from utils.image_model_service import analyze_uploaded_image


SAMPLE_IMAGES = {
    "high": "https://images.unsplash.com/photo-1527482797697-8795b05a13fe?auto=format&fit=crop&w=700&q=80",
    "medium": "https://images.unsplash.com/photo-1584467541268-b040f83be3fd?auto=format&fit=crop&w=700&q=80",
    "low": "https://images.unsplash.com/photo-1594736797933-d0501ba2fe65?auto=format&fit=crop&w=700&q=80",
}


UPLOAD_ICON_SVG = """
<svg width="34" height="34" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path d="M7.4 18.4H17.1C19.25 18.4 21 16.66 21 14.52C21 12.63 19.63 11.04 17.81 10.72C17.21 7.76 14.7 5.55 11.68 5.55C8.9 5.55 6.52 7.36 5.76 10.02C4.17 10.42 3 11.88 3 13.62C3 16.26 4.98 18.4 7.4 18.4Z" fill="white"/>
    <path d="M12 16.05V10.55" stroke="#6DC4E8" stroke-width="2.35" stroke-linecap="round"/>
    <path d="M9.65 12.75L12 10.4L14.35 12.75" stroke="#6DC4E8" stroke-width="2.35" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""


class StoredUpload(io.BytesIO):
    def __init__(self, name: str, mime_type: str, data: bytes) -> None:
        super().__init__(data)
        self.name = name
        self.type = mime_type
        self.size = len(data)


def _safe(value: object) -> str:
    return escape(str(value))


def _html(markup: str) -> None:
    # Keep HTML flush-left so Streamlit Markdown never renders it as a code block.
    cleaned = dedent(markup).strip()
    cleaned = "\n".join(line.lstrip() for line in cleaned.splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)


def _rerun() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


def _bytes_to_data_uri(data: bytes, mime_type: str = "image/png") -> str:
    encoded = base64.b64encode(data).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def _file_hash(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def _inject_image_analysis_css() -> None:
    _html(
        """
        <style>
        .block-container {
            max-width: 930px !important;
            padding-top: 1.25rem !important;
            padding-left: 2.05rem !important;
            padding-right: 1.7rem !important;
            padding-bottom: 3rem !important;
        }

        .ia-page-title {
            margin: 0 0 5px 0;
            color: var(--navy);
            font-size: 30px;
            line-height: 1.1;
            font-weight: 950;
            letter-spacing: -0.7px;
        }

        .ia-page-subtitle {
            margin: 0 0 42px 0;
            color: rgba(0, 49, 82, 0.78);
            font-size: 13px;
            font-weight: 720;
            line-height: 1.45;
        }

        /* Main dashed upload box */

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker) {
            width: 100% !important;
            min-height: 330px !important;
            border-radius: 16px !important;
            border: 2px dashed rgba(250, 250, 250, 0.95) !important;
            background: rgba(255, 255, 255, 0.09) !important;
            backdrop-filter: blur(18px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(18px) saturate(180%) !important;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.20) !important;
            overflow: visible !important;
            position: relative !important;
            padding: 0 !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker) > div {
            min-height: 330px !important;
            width: 100% !important;
            padding: 16px 28px 20px 28px !important;
            box-sizing: border-box !important;
            position: relative !important;
        }

        .ia-upload-card-marker,
        .ia-remove-anchor,
        .ia-analyze-anchor,
        .ia-gallery-open-anchor {
            display: none !important;
        }

        /* Native uploader stays only at the top, so it never covers the preview X button */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker)
        div[data-testid="stFileUploader"] {
            width: 420px !important;
            max-width: 100% !important;
            margin: 0 auto 18px auto !important;
            position: relative !important;
            z-index: 25 !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker)
        div[data-testid="stFileUploader"] > label {
            display: none !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker)
        div[data-testid="stFileUploader"] section {
            height: 56px !important;
            min-height: 56px !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255, 255, 255, 0.35) !important;
            background: rgba(255, 255, 255, 0.28) !important;
            overflow: hidden !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            cursor: pointer !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker)
        div[data-testid="stFileUploader"] section [data-testid="stFileUploaderDropzoneInstructions"] {
            display: none !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker)
        div[data-testid="stFileUploaderFile"],
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker)
        div[data-testid="stFileUploaderFileName"],
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker)
        div[data-testid="stFileUploaderFileSize"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .ia-upload-visual {
            text-align: center;
            width: 100%;
            margin: 10px auto 0 auto;
            position: relative;
            z-index: 5;
            pointer-events: none;
        }

        .ia-upload-icon {
            width: 58px;
            height: 58px;
            margin: 0 auto 18px auto;
            border-radius: 999px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.22);
            border: 1px solid rgba(255, 255, 255, 0.42);
            box-shadow: 0 10px 28px rgba(0, 49, 82, 0.08);
            backdrop-filter: blur(16px) saturate(180%);
            -webkit-backdrop-filter: blur(16px) saturate(180%);
        }

        .ia-upload-title {
            margin: 0 0 7px 0;
            color: var(--navy);
            font-size: 20px;
            font-weight: 950;
            letter-spacing: -0.25px;
        }

        .ia-upload-copy {
            margin: 12px 0 0 0;
            color: rgba(0, 49, 82, 0.72);
            font-size: 12px;
            font-weight: 760;
        }

        .ia-preview-grid {
            width: 100%;
            max-width: 460px;
            margin: 10px auto 0 auto;
            display: grid;
            grid-template-columns: repeat(4, 98px);
            justify-content: center;
            gap: 13px;
        }

        .ia-preview-card {
            width: 98px;
            height: 76px;
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.56);
            box-shadow: 0 10px 24px rgba(0, 49, 82, 0.08);
            background: rgba(255, 255, 255, 0.16);
            position: relative;
        }

        .ia-preview-card img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            border-radius: 10px;
        }

        .ia-preview-more {
            position: absolute;
            inset: 0;
            display: grid;
            place-items: center;
            border-radius: 10px;
            background: rgba(0, 49, 82, 0.48);
            color: #ffffff;
            font-size: 20px;
            font-weight: 950;
        }

        /* Real Streamlit X buttons positioned above the preview images. */
        div.element-container:has(.ia-remove-anchor) {
            height: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
        }

        div.element-container:has(.ia-remove-anchor) + div[data-testid="stHorizontalBlock"] {
            width: 460px !important;
            max-width: 100% !important;
            margin: -2px auto -12px auto !important;
            position: relative !important;
            z-index: 80 !important;
            pointer-events: none !important;
        }

        div.element-container:has(.ia-remove-anchor) + div[data-testid="stHorizontalBlock"] div[data-testid="column"] {
            display: flex !important;
            justify-content: center !important;
        }

        div.element-container:has(.ia-remove-anchor) + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] {
            width: 98px !important;
            min-width: 98px !important;
            display: flex !important;
            justify-content: flex-end !important;
            margin: 0 !important;
            padding: 0 !important;
            pointer-events: auto !important;
        }

        div.element-container:has(.ia-remove-anchor) + div[data-testid="stHorizontalBlock"] button {
            width: 24px !important;
            min-width: 24px !important;
            max-width: 24px !important;
            height: 24px !important;
            min-height: 24px !important;
            padding: 0 !important;
            border-radius: 999px !important;
            background: rgba(250, 250, 250, 0.98) !important;
            border: 1px solid rgba(255, 255, 255, 0.9) !important;
            color: #003152 !important;
            font-size: 16px !important;
            font-weight: 950 !important;
            line-height: 1 !important;
            box-shadow: 0 8px 18px rgba(0, 49, 82, 0.16) !important;
            cursor: pointer !important;
        }

        /* Analyze Image button: centered, no absolute positioning, no overlap */
        div.element-container:has(.ia-analyze-anchor) {
            height: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
        }

        div.element-container:has(.ia-analyze-anchor) + div.element-container {
            width: 100% !important;
            margin: 20px auto 0 auto !important;
            display: flex !important;
            justify-content: center !important;
            position: relative !important;
            z-index: 50 !important;
        }

        div.element-container:has(.ia-analyze-anchor) + div.element-container div[data-testid="stButton"] {
            width: 150px !important;
            display: flex !important;
            justify-content: center !important;
            margin: 0 auto !important;
        }

        div.element-container:has(.ia-analyze-anchor) + div.element-container button {
            width: 150px !important;
            min-width: 150px !important;
            max-width: 150px !important;
            min-height: 43px !important;
            border-radius: 8px !important;
            background: rgba(250, 250, 250, 0.96) !important;
            border: 1px solid rgba(255, 255, 255, 0.75) !important;
            color: var(--navy) !important;
            font-size: 13px !important;
            font-weight: 850 !important;
            white-space: nowrap !important;
            line-height: 1 !important;
            box-shadow: 0 10px 24px rgba(0, 49, 82, 0.08) !important;
        }
        

        /* Recent Samples */
        .ia-samples-title {
            color: var(--navy);
            font-size: 16px;
            font-weight: 950;
            text-align: right;
            margin: -36px 0 14px 0;
        }

        .ia-sample-card {
            height: 124px;
            width: 100%;
            border-radius: 9px;
            overflow: hidden;
            position: relative;
            border: 1px solid rgba(255, 255, 255, 0.54);
            box-shadow: 0 10px 24px rgba(0, 49, 82, 0.08);
            background: rgba(255, 255, 255, 0.15);
            margin-bottom: 14px;
        }

        .ia-sample-card img {
            width: 100%;
            height: 80px;
            object-fit: cover;
            display: block;
        }

        .ia-sample-label {
            position: absolute;
            left: 0;
            right: 0;
            bottom: 0;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(157, 157, 157, 0.72);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            font-size: 16px;
            font-weight: 950;
        }

        .ia-label-high { color: #b42f31; }
        .ia-label-medium { color: #e2ba38; }
        .ia-label-low { color: #049b41; }
        .ia-label-uploaded { color: var(--navy); }

        .ia-plus-card {
            height: 124px;
            width: 100%;
            border-radius: 9px;
            overflow: hidden;
            position: relative;
            border: 1px solid rgba(255, 255, 255, 0.42);
            background: rgba(255, 255, 255, 0.08);
            display: flex;
            align-items: center;
            justify-content: center;
            color: rgba(250, 250, 250, 0.95);
            font-size: 36px;
            font-weight: 350;
            margin-bottom: 14px;
        }

        .ia-plus-card img {
            position: absolute;
            inset: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            filter: blur(1px);
            transform: scale(1.04);
            opacity: 0.72;
        }

        .ia-plus-overlay {
            position: absolute;
            inset: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: rgba(133, 188, 205, 0.42);
            color: var(--navy);
            font-weight: 950;
            text-align: center;
        }

        .ia-plus-big {
            font-size: 28px;
            line-height: 1;
        }

        .ia-plus-small {
            font-size: 11px;
            margin-top: 7px;
            color: rgba(0, 49, 82, 0.78);
        }

        /* Invisible real button on top of plus card */
        div.element-container:has(.ia-gallery-open-anchor) {
            height: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
        }

        div.element-container:has(.ia-gallery-open-anchor) + div.element-container {
            margin-top: -138px !important;
            height: 124px !important;
            position: relative !important;
            z-index: 40 !important;
        }

        div.element-container:has(.ia-gallery-open-anchor) + div.element-container div[data-testid="stButton"],
        div.element-container:has(.ia-gallery-open-anchor) + div.element-container button {
            width: 100% !important;
            height: 124px !important;
            min-height: 124px !important;
            border-radius: 9px !important;
            opacity: 0.001 !important;
            cursor: pointer !important;
        }

        .ia-gallery-wrap {
            max-height: 68vh;
            overflow-y: auto;
            padding: 4px 8px 12px 0;
        }

        .ia-gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
            gap: 14px;
        }

        .ia-gallery-card {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.35);
            background: rgba(255, 255, 255, 0.18);
        }

        .ia-gallery-card img {
            width: 100%;
            height: 126px;
            object-fit: cover;
            display: block;
        }

        .ia-gallery-label {
            padding: 10px 12px;
            color: var(--navy);
            font-weight: 850;
            font-size: 13px;
        }

        /* Results */
        .ia-section-title {
            margin: 24px 0 14px 0;
            color: var(--navy);
            font-size: 21px;
            font-weight: 950;
            letter-spacing: -0.25px;
        }

        .ia-result-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            margin-bottom: 18px;
        }

        .ia-result-card {
            min-height: 206px;
            border-radius: 12px;
            padding: 17px 15px;
            background: rgba(255, 255, 255, 0.16);
            border: 1px solid rgba(255, 255, 255, 0.38);
            backdrop-filter: blur(22px) saturate(180%);
            -webkit-backdrop-filter: blur(22px) saturate(180%);
            box-shadow: 0 12px 28px rgba(0, 49, 82, 0.045);
        }

        .ia-result-card h3 {
            margin: 0 0 17px 0;
            color: var(--navy);
            font-size: 17px;
            font-weight: 950;
        }

        .ia-status-row {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 14px;
            margin-bottom: 15px;
            color: rgba(0, 49, 82, 0.78);
            font-size: 13px;
            font-weight: 720;
            line-height: 1.4;
        }

        .ia-red { color: #b42f31 !important; font-weight: 950; }
        .ia-green { color: #049b41 !important; font-weight: 950; }
        .ia-yellow { color: #b48b08 !important; font-weight: 950; }
        .ia-dark { color: var(--navy) !important; font-weight: 880; }

        .ia-text {
            color: rgba(0, 49, 82, 0.78);
            font-size: 13px;
            line-height: 1.55;
            font-weight: 720;
        }

        .ia-list {
            padding-left: 18px;
            margin: 0;
        }

        .ia-list li {
            color: rgba(0, 49, 82, 0.78);
            font-size: 13px;
            line-height: 1.48;
            font-weight: 720;
            margin-bottom: 6px;
        }

        .ia-impact-pill {
            margin-top: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 9px;
            height: 30px;
            border-radius: 7px;
            background: #eed78c;
            color: #9b7804;
            font-size: 12px;
            font-weight: 950;
        }

        .ia-accuracy-panel {
            border-radius: 14px;
            min-height: 120px;
            padding: 24px 42px;
            background: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(255, 255, 255, 0.36);
            backdrop-filter: blur(22px) saturate(180%);
            -webkit-backdrop-filter: blur(22px) saturate(180%);
            display: grid;
            grid-template-columns: 1fr 134px;
            gap: 20px;
            align-items: center;
            box-shadow: 0 12px 28px rgba(0, 49, 82, 0.045);
        }

        .ia-accuracy-title {
            color: #ffffff !important;
            font-size: 18px;
            font-weight: 950;
            margin-bottom: 13px;
        }

        .ia-accuracy-copy {
            max-width: 510px;
            color: rgba(255, 255, 255, 0.92);
            font-size: 13px;
            line-height: 1.55;
            font-weight: 760;
        }

        .ia-confidence-ring {
            width: 92px;
            height: 92px;
            border-radius: 50%;
            display: grid;
            place-items: center;
            justify-self: center;
        }

        .ia-confidence-inner {
            width: 72px;
            height: 72px;
            border-radius: 50%;
            background: rgba(130, 200, 229, 0.94);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        .ia-confidence-value {
            color: #049b41;
            font-size: 19px;
            font-weight: 950;
        }

        .ia-confidence-label {
            color: rgba(0, 49, 82, 0.78);
            font-size: 10px;
            font-weight: 760;
            margin-top: 6px;
        }

        @media (max-width: 992px) {
            .block-container {
                max-width: 100% !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }

            div[data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
            }

            div[data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
            }

            .ia-samples-title {
                text-align: left;
                margin-top: 20px;
            }

            .ia-result-grid {
                grid-template-columns: 1fr 1fr;
            }

            .ia-accuracy-panel {
                grid-template-columns: 1fr;
                padding: 22px;
            }
        }

        @media (max-width: 560px) {
            .ia-preview-grid {
                grid-template-columns: repeat(2, 98px);
            }

            .ia-result-grid {
                grid-template-columns: 1fr;
            }
        }

        /* ===============================
           FINAL VISUAL OVERRIDES
           Keep the current working logic.
           Only fix the upload-card UI shape, preview X position,
           and Analyze button placement.
        ================================ */

        div[data-testid="stVerticalBlockBorderWrapper"] {
            width: 100% !important;
            min-height: 430px !important;
            border: 2px dashed rgba(250, 250, 250, 0.96) !important;
            border-radius: 18px !important;
            background: rgba(255, 255, 255, 0.08) !important;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.20) !important;
            backdrop-filter: blur(18px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(18px) saturate(180%) !important;
            overflow: visible !important;
            padding: 0 !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            min-height: 430px !important;
            padding: 16px 18px 24px 18px !important;
            box-sizing: border-box !important;
            position: relative !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]
        div[data-testid="stFileUploader"] {
            width: 100% !important;
            max-width: 100% !important;
            margin: 0 0 28px 0 !important;
            position: relative !important;
            z-index: 30 !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]
        div[data-testid="stFileUploader"] section {
            width: 100% !important;
            height: 68px !important;
            min-height: 68px !important;
            border-radius: 10px !important;
            background: rgba(255, 255, 255, 0.28) !important;
            border: 1px solid rgba(255, 255, 255, 0.32) !important;
        }

        .ia-upload-visual,
        .ia-upload-center {
            width: 100% !important;
            text-align: center !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }

        .ia-upload-icon {
            margin-top: 2px !important;
            margin-bottom: 26px !important;
        }

        .ia-upload-title {
            font-size: 20px !important;
            font-weight: 950 !important;
            margin-bottom: 12px !important;
        }

        .ia-upload-copy {
            font-size: 12px !important;
            font-weight: 760 !important;
            text-align: center !important;
        }

        .ia-selected-preview-wrap {
            display: flex !important;
            justify-content: center !important;
            width: 100% !important;
            margin: 8px auto 0 auto !important;
        }

        .ia-selected-preview-card {
            width: 154px !important;
            height: 116px !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            position: relative !important;
            border: 1px solid rgba(255, 255, 255, 0.58) !important;
            box-shadow: 0 10px 24px rgba(0, 49, 82, 0.10) !important;
        }

        .ia-selected-preview-card img {
            width: 100% !important;
            height: 100% !important;
            object-fit: cover !important;
            display: block !important;
        }

        /* X button must sit on the top-right corner of the preview image */
        div.element-container:has(.ia-remove-anchor),
        div[data-testid="stElementContainer"]:has(.ia-remove-anchor) {
            height: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
        }

        div.element-container:has(.ia-remove-anchor) + div.element-container,
        div[data-testid="stElementContainer"]:has(.ia-remove-anchor) + div[data-testid="stElementContainer"] {
            width: 154px !important;
            margin: -118px auto 94px auto !important;
            position: relative !important;
            z-index: 100 !important;
            pointer-events: none !important;
        }

        div.element-container:has(.ia-remove-anchor) + div.element-container div[data-testid="stButton"],
        div[data-testid="stElementContainer"]:has(.ia-remove-anchor) + div[data-testid="stElementContainer"] div[data-testid="stButton"] {
            width: 154px !important;
            display: flex !important;
            justify-content: flex-end !important;
            margin: 0 !important;
            pointer-events: auto !important;
        }

        div.element-container:has(.ia-remove-anchor) + div.element-container button,
        div[data-testid="stElementContainer"]:has(.ia-remove-anchor) + div[data-testid="stElementContainer"] button {
            width: 31px !important;
            min-width: 31px !important;
            max-width: 31px !important;
            height: 31px !important;
            min-height: 31px !important;
            padding: 0 !important;
            border-radius: 999px !important;
            border: 1px solid rgba(255, 255, 255, 0.95) !important;
            background: rgba(250, 250, 250, 0.98) !important;
            color: #003152 !important;
            font-size: 16px !important;
            font-weight: 950 !important;
            line-height: 1 !important;
            box-shadow: 0 8px 18px rgba(0, 49, 82, 0.16) !important;
            cursor: pointer !important;
        }

        .ia-selected-message {
            margin-top: 14px !important;
            text-align: center !important;
        }

        /* Analyze Image button must be centered INSIDE the dashed card */
        div.element-container:has(.ia-analyze-anchor),
        div[data-testid="stElementContainer"]:has(.ia-analyze-anchor) {
            height: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
        }

        div.element-container:has(.ia-analyze-anchor) + div.element-container,
        div[data-testid="stElementContainer"]:has(.ia-analyze-anchor) + div[data-testid="stElementContainer"] {
            width: 100% !important;
            margin: 38px auto 0 auto !important;
            display: flex !important;
            justify-content: center !important;
            position: relative !important;
            z-index: 80 !important;
        }

        div.element-container:has(.ia-analyze-anchor) + div.element-container div[data-testid="stButton"],
        div[data-testid="stElementContainer"]:has(.ia-analyze-anchor) + div[data-testid="stElementContainer"] div[data-testid="stButton"] {
            width: 180px !important;
            display: flex !important;
            justify-content: center !important;
            margin: 0 auto !important;
        }

        div.element-container:has(.ia-analyze-anchor) + div.element-container button,
        div[data-testid="stElementContainer"]:has(.ia-analyze-anchor) + div[data-testid="stElementContainer"] button {
            width: 180px !important;
            min-width: 180px !important;
            max-width: 180px !important;
            height: 46px !important;
            min-height: 46px !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255, 255, 255, 0.75) !important;
            background: rgba(250, 250, 250, 0.96) !important;
            color: var(--navy) !important;
            font-size: 13px !important;
            font-weight: 850 !important;
            white-space: nowrap !important;
            line-height: 1 !important;
            box-shadow: 0 10px 24px rgba(0, 49, 82, 0.08) !important;
        }


        /* Professional Image Analysis v2 overrides */
        .ia-neutral{color:#315c76 !important}.ia-muted{color:rgba(0,49,82,.48)!important}
        .ia-assessment-banner{display:grid;grid-template-columns:1fr 112px 112px;gap:14px;align-items:center;margin:10px 0 16px;padding:22px 24px;border:1px solid rgba(255,255,255,.5);border-radius:16px;background:rgba(255,255,255,.20);box-shadow:0 10px 28px rgba(0,49,82,.05)}
        .ia-eyebrow{font-size:9px;font-weight:900;letter-spacing:1.2px;color:rgba(0,49,82,.55);margin-bottom:7px}.ia-assessment-title{font-size:24px;font-weight:950;line-height:1.1;margin-bottom:8px}.ia-assessment-copy{font-size:11px;font-weight:650;line-height:1.55;color:rgba(0,49,82,.72);max-width:560px}
        .ia-metric{height:82px;border-radius:13px;background:rgba(255,255,255,.42);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}.ia-metric strong{font-size:20px;color:#003152}.ia-metric span{font-size:9px;font-weight:800;color:rgba(0,49,82,.6);margin-top:5px}
        .ia-prof-grid{display:grid;grid-template-columns:.95fr 1.05fr;gap:14px}.ia-prof-card{border:1px solid rgba(255,255,255,.5);border-radius:16px;background:rgba(255,255,255,.16);padding:20px}.ia-prof-card h3{margin:0 0 18px;font-size:15px;color:#003152}
        .ia-condition-row{display:flex;justify-content:space-between;gap:16px;padding:11px 0;border-bottom:1px solid rgba(255,255,255,.42);font-size:11px;color:rgba(0,49,82,.68);font-weight:750}.ia-condition-row strong{font-size:11px;font-weight:950;text-align:right}.ia-observation{padding-top:16px}.ia-observation span{font-size:10px;color:rgba(0,49,82,.58);font-weight:800}.ia-observation p{font-size:11px;line-height:1.55;color:rgba(0,49,82,.72);font-weight:650;margin:5px 0 0}
        .ia-action-row{display:grid;grid-template-columns:30px 1fr auto;gap:10px;align-items:center;padding:11px 0;border-bottom:1px solid rgba(255,255,255,.42)}.ia-action-num{width:27px;height:27px;border-radius:8px;background:rgba(255,255,255,.38);display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:900;color:rgba(0,49,82,.6)}.ia-action-text{font-size:11px;font-weight:800;color:#003152;line-height:1.4}.ia-action-priority{font-size:8px;font-weight:950;letter-spacing:.35px;padding:5px 7px;border-radius:999px}.ia-action-high{background:#fdebed;color:#c92d35}.ia-action-routine{background:#e8f7ef;color:#08753d}.ia-action-info{background:rgba(255,255,255,.55);color:#315c76}.ia-result-note{margin-top:12px;padding:11px 14px;border-radius:11px;background:rgba(255,255,255,.15);font-size:9px;font-weight:650;color:rgba(0,49,82,.58)}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker) div.element-container:has(.ia-analyze-anchor) + div.element-container,div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker) div[data-testid="stElementContainer"]:has(.ia-analyze-anchor) + div[data-testid="stElementContainer"]{width:100%!important;display:flex!important;justify-content:center!important;margin:26px auto 0!important}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker) div.element-container:has(.ia-analyze-anchor) + div.element-container button,div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker) div[data-testid="stElementContainer"]:has(.ia-analyze-anchor) + div[data-testid="stElementContainer"] button{width:210px!important;min-width:210px!important;max-width:210px!important;height:44px!important;border-radius:10px!important;background:#003152!important;color:#fff!important;border:1px solid #003152!important;font-size:12px!important;font-weight:850!important;box-shadow:0 8px 20px rgba(0,49,82,.14)!important}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker) button:disabled{background:rgba(255,255,255,.28)!important;color:rgba(0,49,82,.45)!important;border-color:rgba(255,255,255,.5)!important;box-shadow:none!important}
        div.element-container:has(.ia-gallery-open-anchor)+div.element-container button,div[data-testid="stElementContainer"]:has(.ia-gallery-open-anchor)+div[data-testid="stElementContainer"] button{width:auto!important;min-width:72px!important;height:32px!important;border-radius:9px!important;padding:0 12px!important;background:rgba(255,255,255,.42)!important;color:#003152!important;border:1px solid rgba(255,255,255,.6)!important;font-size:10px!important;font-weight:850!important;box-shadow:none!important}
        @media(max-width:760px){.ia-assessment-banner{grid-template-columns:1fr 1fr}.ia-assessment-banner>div:first-child{grid-column:1/-1}.ia-prof-grid{grid-template-columns:1fr}}

        /* Refined result typography */
        .ia-assessment-banner{grid-template-columns:190px minmax(0,1fr) 100px!important;gap:18px!important;padding:20px!important;align-items:stretch!important}
        .ia-result-preview{width:190px;height:128px;border-radius:13px;overflow:hidden;background:rgba(255,255,255,.3);border:1px solid rgba(255,255,255,.55)}
        .ia-result-preview img{width:100%;height:100%;object-fit:cover;display:block}
        .ia-eyebrow{font-size:10px!important;font-weight:700!important;letter-spacing:1.35px!important;color:rgba(0,49,82,.48)!important;margin-bottom:8px!important}
        .ia-assessment-title{font-size:29px!important;font-weight:750!important;letter-spacing:-.45px!important;line-height:1.08!important;margin-bottom:9px!important}
        .ia-assessment-copy{font-size:13px!important;font-weight:450!important;line-height:1.55!important;color:rgba(0,49,82,.68)!important;max-width:620px!important}
        .ia-metric{height:auto!important;min-height:96px!important}.ia-metric strong{font-size:22px!important;font-weight:700!important}.ia-metric span{font-size:10px!important;font-weight:600!important}
        .ia-prof-card{padding:22px 24px!important}.ia-prof-card h3{margin:0 0 18px!important;font-size:18px!important;font-weight:700!important;letter-spacing:-.2px!important}
        .ia-condition-row{padding:13px 0!important;font-size:13px!important;font-weight:450!important;color:rgba(0,49,82,.62)!important}.ia-condition-row strong{font-size:13px!important;font-weight:650!important}
        .ia-observation{padding-top:18px!important}.ia-observation span{font-size:10px!important;font-weight:700!important;letter-spacing:.7px!important;text-transform:uppercase!important;color:rgba(0,49,82,.46)!important}.ia-observation p{font-size:13px!important;line-height:1.58!important;font-weight:400!important;color:rgba(0,49,82,.66)!important;margin:7px 0 0!important}
        .ia-action-row{grid-template-columns:34px minmax(0,1fr) auto!important;gap:12px!important;align-items:start!important;padding:14px 0!important}.ia-action-num{width:30px!important;height:30px!important;border-radius:9px!important;font-size:10px!important;font-weight:700!important}.ia-action-text{font-size:13px!important;font-weight:600!important;line-height:1.45!important;padding-top:5px!important}.ia-action-priority{font-size:9px!important;font-weight:700!important;letter-spacing:.55px!important;padding:6px 9px!important;margin-top:2px!important}
        .ia-action-content{min-width:0;padding-top:1px}.ia-action-title{font-size:13px;font-weight:800;color:#003152;line-height:1.35}.ia-action-desc{margin-top:4px;font-size:11px;font-weight:650;color:rgba(0,49,82,.72);line-height:1.48}.ia-action-medium{background:#fff4da;color:#8a5a00}.ia-action-monitor{background:#e7f3fb;color:#245f80}.ia-condition-row{font-weight:650!important;color:rgba(0,49,82,.76)!important}.ia-condition-row strong{font-weight:800!important}.ia-observation span{font-weight:800!important;color:rgba(0,49,82,.68)!important}.ia-observation p{font-weight:650!important;color:rgba(0,49,82,.78)!important}
        .ia-result-note{font-size:11px!important;font-weight:400!important;line-height:1.5!important;padding:11px 15px!important;color:rgba(0,49,82,.52)!important}
        @media(max-width:980px){.ia-assessment-banner{grid-template-columns:150px 1fr!important}.ia-result-preview{width:150px}.ia-prof-grid{grid-template-columns:1fr!important}}
        @media(max-width:760px){.ia-assessment-banner{grid-template-columns:1fr!important}.ia-result-preview{width:100%;height:190px}.ia-prof-grid{grid-template-columns:1fr!important}}


        /* Professional interaction + motion system */
        .ia-assessment-banner,
        .ia-prof-card,
        .ia-sample-card,
        .ia-plus-card,
        .ia-gallery-card,
        .ia-result-preview,
        .ia-action-row,
        .ia-condition-row {
            transition: transform .22s cubic-bezier(.2,.8,.2,1),
                        box-shadow .22s ease,
                        border-color .22s ease,
                        background-color .22s ease,
                        opacity .22s ease;
        }

        .ia-assessment-banner,
        .ia-prof-card {
            will-change: transform;
        }

        .ia-assessment-banner:hover {
            transform: translateY(-2px);
            border-color: rgba(255,255,255,.72);
            box-shadow: 0 16px 34px rgba(0,49,82,.085);
        }

        .ia-prof-card:hover {
            transform: translateY(-3px);
            border-color: rgba(255,255,255,.72);
            background: rgba(255,255,255,.20);
            box-shadow: 0 15px 32px rgba(0,49,82,.075);
        }

        .ia-result-preview img,
        .ia-sample-card img,
        .ia-gallery-card img {
            transition: transform .28s cubic-bezier(.2,.8,.2,1), filter .28s ease;
        }

        .ia-result-preview:hover img { transform: scale(1.018); }

        .ia-sample-card:hover,
        .ia-plus-card:hover,
        .ia-gallery-card:hover {
            transform: translateY(-3px);
            border-color: rgba(255,255,255,.78);
            box-shadow: 0 12px 26px rgba(0,49,82,.10);
        }
        .ia-sample-card:hover img,
        .ia-gallery-card:hover img { transform: scale(1.025); }

        .ia-action-row {
            margin: 0 -10px;
            padding-left: 10px !important;
            padding-right: 10px !important;
            border-radius: 10px;
        }
        .ia-action-row:hover {
            transform: translateX(2px);
            background: rgba(255,255,255,.18);
        }
        .ia-action-row:hover .ia-action-num {
            background: rgba(255,255,255,.58);
            transform: translateY(-1px);
        }
        .ia-action-num,
        .ia-action-priority {
            transition: transform .2s ease, background-color .2s ease, box-shadow .2s ease;
        }
        .ia-action-row:hover .ia-action-priority {
            transform: translateY(-1px);
            box-shadow: 0 5px 12px rgba(0,49,82,.07);
        }

        .ia-condition-row {
            margin: 0 -8px;
            padding-left: 8px !important;
            padding-right: 8px !important;
            border-radius: 8px;
        }
        .ia-condition-row:hover { background: rgba(255,255,255,.13); }

        /* Result enters once after Streamlit renders the new assessment. */
        .ia-section-title,
        .ia-assessment-banner,
        .ia-prof-grid,
        .ia-result-note {
            animation: iaResultEnter .38s cubic-bezier(.2,.8,.2,1) both;
        }
        .ia-assessment-banner { animation-delay: .035s; }
        .ia-prof-grid { animation-delay: .075s; }
        .ia-result-note { animation-delay: .11s; }
        @keyframes iaResultEnter {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Native Streamlit controls: subtle lift only, no distracting scaling. */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker) button:not(:disabled),
        div.element-container:has(.ia-gallery-open-anchor)+div.element-container button,
        div[data-testid="stElementContainer"]:has(.ia-gallery-open-anchor)+div[data-testid="stElementContainer"] button {
            transition: transform .18s ease, box-shadow .18s ease, background-color .18s ease, border-color .18s ease !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker) button:not(:disabled):hover,
        div.element-container:has(.ia-gallery-open-anchor)+div.element-container button:hover,
        div[data-testid="stElementContainer"]:has(.ia-gallery-open-anchor)+div[data-testid="stElementContainer"] button:hover {
            transform: translateY(-1px);
            box-shadow: 0 10px 22px rgba(0,49,82,.14) !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker) button:not(:disabled):active,
        div.element-container:has(.ia-gallery-open-anchor)+div.element-container button:active,
        div[data-testid="stElementContainer"]:has(.ia-gallery-open-anchor)+div[data-testid="stElementContainer"] button:active {
            transform: translateY(0);
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker) {
            transition: border-color .22s ease, background-color .22s ease, box-shadow .22s ease !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker):hover {
            border-color: rgba(255,255,255,1) !important;
            background: rgba(255,255,255,.12) !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,.28), 0 12px 28px rgba(0,49,82,.045) !important;
        }

        @media (prefers-reduced-motion: reduce) {
            .ia-assessment-banner,
            .ia-prof-card,
            .ia-sample-card,
            .ia-plus-card,
            .ia-gallery-card,
            .ia-result-preview,
            .ia-result-preview img,
            .ia-sample-card img,
            .ia-gallery-card img,
            .ia-action-row,
            .ia-action-num,
            .ia-action-priority,
            .ia-condition-row,
            .ia-section-title,
            .ia-prof-grid,
            .ia-result-note {
                animation: none !important;
                transition: none !important;
                transform: none !important;
            }
        }
        
/* Single-image analysis workflow */
.ia-single-preview-grid{grid-template-columns:minmax(180px,280px)!important;justify-content:center!important;}
.ia-single-preview-card{width:min(280px,100%)!important;margin:0 auto!important;}
.ia-single-preview-card img{width:100%!important;aspect-ratio:16/10;object-fit:cover;}

        /* Selected-image workspace: compact, professional single-card state */
        .ia-selected-workspace{padding:4px 8px 0;animation:iaResultIn .28s ease both}
        .ia-selected-heading{font-size:14px;font-weight:800;color:#003152;letter-spacing:.01em;margin:2px 0 18px}
        .ia-selected-preview{width:min(100%,440px);aspect-ratio:4/3;margin:0 auto;border-radius:16px;overflow:hidden;background:rgba(255,255,255,.22);border:1px solid rgba(255,255,255,.66);box-shadow:0 12px 30px rgba(0,49,82,.08);display:flex;align-items:center;justify-content:center;transition:transform .22s ease,box-shadow .22s ease,border-color .22s ease}
        .ia-selected-preview:hover{transform:translateY(-2px);box-shadow:0 16px 34px rgba(0,49,82,.12);border-color:rgba(255,255,255,.9)}
        .ia-selected-preview img{width:100%;height:100%;object-fit:contain;display:block;background:rgba(255,255,255,.12)}
        .ia-selected-meta{display:flex;align-items:center;justify-content:space-between;gap:18px;margin:16px 2px 8px;padding:0 2px;font-size:12px;color:#315f7d}
        .ia-selected-filename{font-weight:700;color:#003152;max-width:65%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
        .ia-ready-status{display:inline-flex;align-items:center;gap:7px;font-weight:700;white-space:nowrap}
        .ia-ready-dot{width:7px;height:7px;border-radius:50%;background:#15925a;box-shadow:0 0 0 4px rgba(21,146,90,.10)}
        div.element-container:has(.ia-selected-actions-anchor),div[data-testid="stElementContainer"]:has(.ia-selected-actions-anchor){height:0!important;min-height:0!important;margin:0!important;padding:0!important}
        div.element-container:has(.ia-selected-actions-anchor)+div[data-testid="stHorizontalBlock"],div[data-testid="stElementContainer"]:has(.ia-selected-actions-anchor)+div[data-testid="stHorizontalBlock"]{align-items:center!important;margin-top:16px!important;gap:10px!important}
        div.element-container:has(.ia-selected-actions-anchor)+div[data-testid="stHorizontalBlock"] button,div[data-testid="stElementContainer"]:has(.ia-selected-actions-anchor)+div[data-testid="stHorizontalBlock"] button{height:44px!important;border-radius:11px!important;font-size:12px!important;font-weight:800!important;white-space:nowrap!important;transition:transform .2s ease,box-shadow .2s ease,background .2s ease,border-color .2s ease!important}
        div.element-container:has(.ia-selected-actions-anchor)+div[data-testid="stHorizontalBlock"] div[data-testid="column"]:first-child button,div[data-testid="stElementContainer"]:has(.ia-selected-actions-anchor)+div[data-testid="stHorizontalBlock"] div[data-testid="column"]:first-child button{background:rgba(255,255,255,.45)!important;color:#003152!important;border:1px solid rgba(255,255,255,.72)!important;box-shadow:none!important}
        div.element-container:has(.ia-selected-actions-anchor)+div[data-testid="stHorizontalBlock"] div[data-testid="column"]:first-child button:hover,div[data-testid="stElementContainer"]:has(.ia-selected-actions-anchor)+div[data-testid="stHorizontalBlock"] div[data-testid="column"]:first-child button:hover{background:rgba(255,255,255,.68)!important;transform:translateY(-1px)!important}
        div.element-container:has(.ia-selected-actions-anchor)+div[data-testid="stHorizontalBlock"] div[data-testid="column"]:last-child button,div[data-testid="stElementContainer"]:has(.ia-selected-actions-anchor)+div[data-testid="stHorizontalBlock"] div[data-testid="column"]:last-child button{background:#003152!important;color:#fff!important;border:1px solid #003152!important;box-shadow:0 8px 20px rgba(0,49,82,.16)!important}
        div.element-container:has(.ia-selected-actions-anchor)+div[data-testid="stHorizontalBlock"] div[data-testid="column"]:last-child button:hover,div[data-testid="stElementContainer"]:has(.ia-selected-actions-anchor)+div[data-testid="stHorizontalBlock"] div[data-testid="column"]:last-child button:hover{background:#0a456d!important;transform:translateY(-1px)!important;box-shadow:0 11px 24px rgba(0,49,82,.22)!important}
        @media(max-width:760px){.ia-selected-preview{width:min(100%,360px)}.ia-selected-meta{align-items:flex-start;flex-direction:column;gap:7px}.ia-selected-filename{max-width:100%}div.element-container:has(.ia-selected-actions-anchor)+div[data-testid="stHorizontalBlock"],div[data-testid="stElementContainer"]:has(.ia-selected-actions-anchor)+div[data-testid="stHorizontalBlock"]{gap:8px!important}}

        /* Mobile uploader reliability: keep Streamlit's native file input touchable. */
        @media (max-width: 760px) {
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker) {
                min-height: 0 !important;
                overflow: visible !important;
            }
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker) > div {
                min-height: 0 !important;
                padding: 14px !important;
            }
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker) div[data-testid="stFileUploader"] {
                width: 100% !important;
                margin: 0 0 20px 0 !important;
                position: relative !important;
                z-index: 100 !important;
                pointer-events: auto !important;
                touch-action: manipulation !important;
            }
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker) div[data-testid="stFileUploader"] section {
                width: 100% !important;
                height: auto !important;
                min-height: 74px !important;
                overflow: visible !important;
                position: relative !important;
                z-index: 101 !important;
                pointer-events: auto !important;
                touch-action: manipulation !important;
            }
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker) div[data-testid="stFileUploader"] section button {
                position: relative !important;
                z-index: 103 !important;
                pointer-events: auto !important;
                touch-action: manipulation !important;
            }
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.ia-upload-card-marker) div[data-testid="stFileUploader"] input[type="file"] {
                pointer-events: auto !important;
                touch-action: manipulation !important;
                z-index: 104 !important;
            }
            .ia-upload-visual {
                position: relative !important;
                z-index: 1 !important;
                pointer-events: none !important;
            }
        }
</style>
        """
    )


def _default_result() -> dict[str, Any]:
    return _summarize_many_results([])


def _ensure_state() -> None:
    if "image_analysis_result" not in st.session_state:
        st.session_state.image_analysis_result = _default_result()

    if "ia_pending_images" not in st.session_state:
        st.session_state.ia_pending_images = []

    if "analyzed_recent_images" not in st.session_state:
        st.session_state.analyzed_recent_images = []

    if "ia_uploader_version" not in st.session_state:
        st.session_state.ia_uploader_version = 0

    if "ia_gallery_open" not in st.session_state:
        st.session_state.ia_gallery_open = False


def _risk_rank(risk_level: str) -> int:
    risk = str(risk_level or "").lower()
    if risk == "high":
        return 3
    if risk == "medium":
        return 2
    if risk == "low":
        return 1
    return 0


def _risk_class(risk_level: str) -> str:
    risk = str(risk_level or "").lower()
    if risk == "low":
        return "ia-green"
    if risk == "medium":
        return "ia-yellow"
    return "ia-red"


def _sample_label_class(label: str) -> str:
    value = str(label or "").lower()
    if value == "high":
        return "ia-label-high"
    if value == "medium":
        return "ia-label-medium"
    if value == "low":
        return "ia-label-low"
    if value in {"not relevant", "unrelated"}:
        return "ia-label-uploaded"
    if value in {"flood detected", "high risk"}:
        return "ia-label-high"
    return "ia-label-uploaded"


def _normalize_single_result(raw: dict[str, Any] | None, file_name: str = "") -> dict[str, Any]:
    """Normalize only values actually returned by the image classifier.

    The trained image model is a 3-class classifier (Flood / Non_Flood / Unrelated).
    Do not invent water coverage, severity, or confidence when the backend did not return them.
    """
    raw = raw or {}

    def first(*keys, default=None):
        for key in keys:
            value = raw.get(key)
            if value is not None and value != "":
                return value
        return default

    predicted = str(first("classification", "predicted_class", "class_name", "class", "label", "prediction", default="")).strip()
    token = predicted.lower().replace("-", "_").replace(" ", "_")
    if token in {"flood", "flooded"}:
        category = "Flood"
    elif token in {"non_flood", "nonflood", "no_flood", "normal"}:
        category = "Non_Flood"
    elif token in {"unrelated", "not_relevant", "irrelevant"}:
        category = "Unrelated"
    else:
        # Older service versions may return flood_detected/risk_level instead of a class name.
        detected = str(first("flood_detected", default="")).lower()
        category = "Flood" if detected == "yes" else "Non_Flood" if detected == "no" else "Unknown"

    confidence = first("confidence", "confidence_score", "probability", "score")
    try:
        confidence = float(confidence)
        if 0 <= confidence <= 1:
            confidence *= 100
        confidence = int(round(max(0, min(100, confidence))))
    except (TypeError, ValueError):
        confidence = None

    backend_risk = first("risk_level", "severity")
    if category == "Unrelated":
        risk_level = "Not Relevant"
        flood_detected = "Not assessed"
    elif category == "Non_Flood":
        risk_level = "Low" if not backend_risk else str(backend_risk)
        flood_detected = "No"
    elif category == "Flood":
        risk_level = str(backend_risk) if backend_risk else "Flood Detected"
        flood_detected = "Yes"
    else:
        risk_level = "Unable to Assess"
        flood_detected = "Not assessed"

    water = first("water_coverage", "water_coverage_percent", "coverage_percent")
    try:
        water = int(round(float(water))) if water is not None else None
        if water is not None:
            water = max(0, min(100, water))
    except (TypeError, ValueError):
        water = None

    road_impact = first("road_impact", "access_impact")
    context = first("context", "what_happening", "description")
    actions = first("recommendations", "what_you_should_do", "actions")
    if isinstance(actions, str):
        actions = [actions]
    elif not isinstance(actions, list):
        actions = []

    if not context:
        if category == "Flood":
            context = "Flood conditions were detected in the uploaded image. Use the image result together with local observations and official warnings."
        elif category == "Non_Flood":
            context = "No flood condition was detected in the uploaded image. Continue monitoring if weather or water levels are changing."
        elif category == "Unrelated":
            context = "This image is not relevant to flood-condition analysis. Upload a clear photo of a road, street, river, drainage area, or visible floodwater."
        else:
            context = "The image could not be assessed reliably. Try another clear image showing the surrounding ground or water conditions."

    if not actions:
        if category == "Flood":
            actions = ["Avoid entering visible floodwater", "Check local flood warnings", "Use a safer route or move to higher ground if conditions worsen"]
        elif category == "Non_Flood":
            actions = ["Continue normal monitoring", "Reassess if rainfall or water levels increase"]
        elif category == "Unrelated":
            actions = ["Upload a flood-related field image", "Include roads, ground, drainage, riverbanks, or visible water"]
        else:
            actions = ["Upload a clearer image", "Make sure the scene is visible and not heavily blurred or obstructed"]

    return {
        "file_name": file_name,
        "classification": category,
        "flood_detected": flood_detected,
        "risk_level": risk_level,
        "confidence": confidence,
        "water_coverage": water,
        "road_impact": road_impact,
        "context": str(context),
        "recommendations": [str(x) for x in actions if str(x).strip()],
    }


def _summarize_many_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    if not results:
        return {
            "uploaded_count": 0,
            "classification": "No Image",
            "flood_detected": "Not assessed",
            "risk_level": "No Image",
            "confidence": None,
            "water_coverage": None,
            "road_impact": None,
            "context": "Upload one or more JPG, PNG, or JPEG images to start a flood-condition assessment.",
            "recommendations": ["Upload a clear field image to begin"],
        }

    def rank(item: dict[str, Any]) -> int:
        cls = item.get("classification")
        if cls == "Flood": return 3
        if cls == "Non_Flood": return 2
        if cls == "Unrelated": return 1
        return 0

    primary = max(results, key=rank)
    relevant = [r for r in results if r.get("classification") != "Unrelated"]
    confidences = [r["confidence"] for r in results if isinstance(r.get("confidence"), (int, float))]
    coverages = [r["water_coverage"] for r in relevant if isinstance(r.get("water_coverage"), (int, float))]
    classes = {r.get("classification") for r in results}

    if classes == {"Unrelated"}:
        classification = "Unrelated"
        flood_detected = "Not assessed"
        risk_level = "Not Relevant"
    else:
        classification = primary.get("classification", "Unknown")
        flood_detected = primary.get("flood_detected", "Not assessed")
        risk_level = primary.get("risk_level", "Unable to Assess")

    return {
        "uploaded_count": len(results),
        "classification": classification,
        "flood_detected": flood_detected,
        "risk_level": risk_level,
        "confidence": round(sum(confidences) / len(confidences)) if confidences else None,
        "water_coverage": round(sum(coverages) / len(coverages)) if coverages else None,
        "road_impact": primary.get("road_impact"),
        "context": primary.get("context", ""),
        "recommendations": primary.get("recommendations", []),
    }


def _render_header() -> None:
    _html(
        """
        <h1 class="ia-page-title">Flood Image Analysis</h1>
        <p class="ia-page-subtitle">Assess visible flood conditions from field imagery.</p>
        """
    )


def _add_new_upload(uploaded_file: Any) -> None:
    """Keep exactly one pending image for one analysis."""
    if uploaded_file is None:
        return

    data = uploaded_file.getvalue()
    image_hash = _file_hash(data)

    # Do not rerun repeatedly when Streamlit returns the same uploader value.
    if st.session_state.ia_pending_images and st.session_state.ia_pending_images[0].get("hash") == image_hash:
        return

    st.session_state.ia_pending_images = [
        {
            "name": getattr(uploaded_file, "name", "Uploaded image"),
            "type": getattr(uploaded_file, "type", "image/png") or "image/png",
            "data": data,
            "hash": image_hash,
        }
    ]
    st.session_state.ia_uploader_version += 1
    _rerun()


def _render_upload_visual() -> None:
    pending = st.session_state.ia_pending_images

    if not pending:
        _html(
            f"""
            <div class="ia-upload-visual">
                <div class="ia-upload-icon">{UPLOAD_ICON_SVG}</div>
                <div class="ia-upload-title">Upload image here or browse file</div>
                <div class="ia-upload-copy">Supported formats: JPG, PNG, JPEG • Max file size: 20MB</div>
            </div>
            """
        )
        return

    item = pending[0]
    src = _bytes_to_data_uri(item["data"], item["type"])
    _html(
        f"""
        <div class="ia-selected-workspace">
            <div class="ia-selected-heading">Selected image</div>
            <div class="ia-selected-preview">
                <img src="{src}" alt="Selected image preview">
            </div>
            <div class="ia-selected-meta">
                <span class="ia-selected-filename">{_safe(item.get('name', 'Uploaded image'))}</span>
                <span class="ia-ready-status"><span class="ia-ready-dot"></span>Ready to analyze</span>
            </div>
        </div>
        """
    )


def _render_selected_actions() -> tuple[bool, bool]:
    """Render the compact secondary/primary actions from the selected-image workspace."""
    if not st.session_state.ia_pending_images:
        return False, False

    _html('<span class="ia-selected-actions-anchor"></span>')
    left, spacer, right = st.columns([1.15, 2.2, 2.0])
    with left:
        remove_clicked = st.button(
            "Remove",
            key=f"ia_remove_pending_{st.session_state.ia_pending_images[0]['hash']}",
            use_container_width=True,
        )
    with right:
        analyze_clicked = st.button(
            "Analyze Flood Conditions",
            key="analyze_uploaded_image_button",
            use_container_width=True,
        )
    return remove_clicked, analyze_clicked


def _render_static_sample_card(key: str, label: str, label_class: str) -> None:
    _html(
        f"""
        <div class="ia-sample-card">
            <img src="{SAMPLE_IMAGES[key]}" alt="{_safe(label)} sample">
            <div class="ia-sample-label {label_class}">{_safe(label)}</div>
        </div>
        """
    )


def _render_uploaded_sample_card(item: dict[str, str]) -> None:
    label = item.get("label", "Uploaded")
    label_class = _sample_label_class(label)

    _html(
        f"""
        <div class="ia-sample-card">
            <img src="{item["src"]}" alt="Uploaded analyzed image">
            <div class="ia-sample-label {label_class}">{_safe(label)}</div>
        </div>
        """
    )


def _render_plus_card(more_items: list[dict[str, str]]) -> None:
    if more_items:
        src = more_items[0]["src"]
        count = len(more_items)

        _html(
            f"""
            <div class="ia-plus-card">
                <img src="{src}" alt="More uploaded images">
                <div class="ia-plus-overlay">
                    <div class="ia-plus-big">+{count}</div>
                    <div class="ia-plus-small">more</div>
                </div>
            </div>
            """
        )

        _html('<span class="ia-gallery-open-anchor"></span>')

        if st.button("View all", key="ia_open_gallery", use_container_width=False):
            st.session_state.ia_gallery_open = True
            _rerun()
    else:
        _html('<div class="ia-plus-card"><span>+</span></div>')


def _recent_sample_items() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    uploaded_items = list(st.session_state.analyzed_recent_images)
    visible_uploaded = uploaded_items[:3]
    hidden_uploaded = uploaded_items[3:]

    visible: list[dict[str, str]] = visible_uploaded[:]

    fallback_items = [
        {"kind": "static", "key": "high", "label": "High Risk", "class": "ia-label-high"},
        {"kind": "static", "key": "medium", "label": "Medium Risk", "class": "ia-label-medium"},
        {"kind": "static", "key": "low", "label": "Low Risk", "class": "ia-label-low"},
    ]

    for item in fallback_items:
        if len(visible) >= 3:
            break
        visible.append(item)

    return visible[:3], hidden_uploaded


def _render_recent_samples() -> None:
    _html('<div class="ia-samples-title">Recent Analyses</div>')

    visible, hidden = _recent_sample_items()

    row1 = st.columns(2, gap="small")
    row2 = st.columns(2, gap="small")

    slots = [
        (row1[0], visible[0] if len(visible) > 0 else None),
        (row1[1], visible[1] if len(visible) > 1 else None),
        (row2[0], visible[2] if len(visible) > 2 else None),
        (row2[1], {"kind": "plus"}),
    ]

    for col, item in slots:
        with col:
            if item is None:
                _html('<div class="ia-plus-card"><span>+</span></div>')
            elif item.get("kind") == "static":
                _render_static_sample_card(
                    key=item["key"],
                    label=item["label"],
                    label_class=item["class"],
                )
            elif item.get("kind") == "plus":
                _render_plus_card(hidden)
            else:
                _render_uploaded_sample_card(item)


def _render_gallery_content() -> None:
    items = list(st.session_state.analyzed_recent_images)

    if not items:
        st.info("No analyzed uploaded images yet.")
        return

    cards = ""

    for index, item in enumerate(items, start=1):
        cards += (
            '<div class="ia-gallery-card">'
            f'<img src="{item["src"]}" alt="Uploaded image {index}">'
            f'<div class="ia-gallery-label">{index}. {_safe(item.get("label", "Uploaded"))}</div>'
            '</div>'
        )

    _html(f'<div class="ia-gallery-wrap"><div class="ia-gallery-grid">{cards}</div></div>')

    if st.button("Close gallery", key="ia_close_gallery"):
        st.session_state.ia_gallery_open = False
        _rerun()


def _render_gallery_if_open() -> None:
    if not st.session_state.ia_gallery_open:
        return

    if hasattr(st, "dialog"):
        @st.dialog("Uploaded Images", width="large")
        def gallery_dialog() -> None:
            _render_gallery_content()

        gallery_dialog()
    else:
        with st.expander("Uploaded Images", expanded=True):
            _render_gallery_content()


def _pending_to_upload_objects() -> list[StoredUpload]:
    return [
        StoredUpload(
            name=item["name"],
            mime_type=item["type"],
            data=item["data"],
        )
        for item in st.session_state.ia_pending_images
    ]


def _run_image_analysis(uploaded_files: list[StoredUpload]) -> dict[str, Any]:
    if not uploaded_files:
        return _summarize_many_results([])

    results: list[dict[str, Any]] = []

    for uploaded_file in uploaded_files:
        uploaded_file.seek(0)

        try:
            raw = analyze_uploaded_image(
                uploaded_file=uploaded_file,
                file_name=uploaded_file.name,
            )
        except TypeError:
            raw = analyze_uploaded_image(uploaded_file=uploaded_file)

        results.append(_normalize_single_result(raw, file_name=uploaded_file.name))

    return _summarize_many_results(results)


def _save_pending_to_recent(result: dict[str, Any]) -> None:
    if not st.session_state.ia_pending_images:
        return

    classification = str(result.get("classification", "Unknown"))
    if classification == "Unrelated":
        risk_label = "Not Relevant"
    elif classification == "Non_Flood":
        risk_label = "Low Risk"
    else:
        risk_label = str(result.get("risk_level", "Flood Detected"))

    new_items = []

    for item in st.session_state.ia_pending_images:
        new_items.append(
            {
                "src": _bytes_to_data_uri(item["data"], item["type"]),
                "label": risk_label,
            }
        )

    st.session_state.analyzed_recent_images = new_items + st.session_state.analyzed_recent_images


def _render_upload_area() -> None:
    analyze_clicked = False
    remove_clicked = False

    with st.container(border=True):
        _html('<span class="ia-upload-card-marker"></span>')

        # Keep the uploader visible only before a file is selected. Once selected,
        # the same card becomes a focused preview workspace.
        if not st.session_state.ia_pending_images:
            uploaded_file = st.file_uploader(
                label="Upload a flood image",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=False,
                label_visibility="collapsed",
                key=f"flood_image_uploader_{st.session_state.ia_uploader_version}",
            )
            _add_new_upload(uploaded_file)

        _render_upload_visual()

        if st.session_state.ia_pending_images:
            remove_clicked, analyze_clicked = _render_selected_actions()

    if remove_clicked:
        st.session_state.ia_pending_images = []
        st.session_state.ia_uploader_version += 1
        _rerun()

    if analyze_clicked:
        uploads = _pending_to_upload_objects()

        with st.spinner("Analyzing image with Mekhala AI..."):
            result = _run_image_analysis(uploads)
            result["analyzed_images"] = [_bytes_to_data_uri(st.session_state.ia_pending_images[0]["data"], st.session_state.ia_pending_images[0]["type"])]
            st.session_state.image_analysis_result = result
            _save_pending_to_recent(result)

            st.session_state.ia_pending_images = []
            st.session_state.ia_uploader_version += 1
            _rerun()


def _professional_actions(result: dict[str, Any]) -> list[dict[str, str]]:
    """Return concise, class-appropriate guidance without claiming facts the classifier cannot measure."""
    classification = str(result.get("classification", "Unknown"))
    confidence = result.get("confidence")
    confidence = float(confidence) if isinstance(confidence, (int, float)) else None

    if classification == "Flood":
        first_priority = "HIGH" if confidence is None or confidence >= 75 else "MEDIUM"
        return [
            {"title": "Avoid visible floodwater", "description": "Do not drive or walk through visibly flooded areas until local conditions are verified.", "priority": first_priority},
            {"title": "Check official flood warnings", "description": "Review current local alerts and emergency guidance before travelling or changing routes.", "priority": "MEDIUM"},
            {"title": "Reassess if conditions change", "description": "Upload a new field image if water levels, rainfall, or access conditions visibly change.", "priority": "MONITOR"},
        ]
    if classification == "Non_Flood":
        return [
            {"title": "Continue local monitoring", "description": "No flood was classified in this image; keep watching rainfall, drainage, and nearby water levels.", "priority": "MONITOR"},
            {"title": "Check warnings before travel", "description": "Use current official alerts when conditions are changing; one image cannot confirm route safety.", "priority": "MEDIUM"},
            {"title": "Reassess after visible change", "description": "Analyze a newer image if standing water, river level, or road conditions change.", "priority": "MONITOR"},
        ]
    if classification == "Unrelated":
        return [
            {"title": "Choose a flood-related scene", "description": "Upload a clear image of a road, street, river, drainage area, ground surface, or visible floodwater.", "priority": "INFO"},
            {"title": "Keep the scene clearly visible", "description": "Use a well-lit image with enough surrounding context for the classifier to assess relevance.", "priority": "INFO"},
        ]
    return [
        {"title": "Try another clear image", "description": "Use a well-lit field image with the scene unobstructed and in focus.", "priority": "INFO"},
        {"title": "Recheck the image context", "description": "Include roads, ground, drainage, riverbanks, or visible water so the scene can be assessed.", "priority": "INFO"},
    ]


def _render_results(result: dict[str, Any]) -> None:
    if int(result.get("uploaded_count", 0) or 0) == 0:
        return

    classification = str(result.get("classification", "Unknown"))
    risk_level = str(result.get("risk_level", "Unable to Assess"))
    confidence = result.get("confidence")
    water = result.get("water_coverage")
    road = result.get("road_impact")

    if risk_level.lower() in {"high", "severe", "critical"}:
        status_class = "ia-red"
    elif risk_level.lower() in {"medium", "moderate"}:
        status_class = "ia-yellow"
    elif risk_level.lower() in {"low", "no flood"}:
        status_class = "ia-green"
    else:
        status_class = "ia-neutral"

    if classification == "Flood" and risk_level == "Flood Detected":
        status_class = "ia-red"
    elif classification == "Unrelated":
        status_class = "ia-neutral"

    detected = result.get("flood_detected", "Not assessed")
    detected_class = "ia-red" if detected == "Yes" else "ia-green" if detected == "No" else "ia-neutral"
    confidence_text = f"{int(confidence)}%" if isinstance(confidence, (int, float)) else "Not available"
    water_text = f"{int(water)}%" if isinstance(water, (int, float)) else "Not available"
    road_text = str(road) if road not in (None, "") else ("Potential" if classification == "Flood" else "Not indicated" if classification == "Non_Flood" else "Not assessed")

    rows = [
        ("Floodwater detected", str(detected), detected_class),
        ("Assessment status", risk_level, status_class),
        ("Model confidence", confidence_text, "ia-dark"),
    ]
    # Coverage is shown transparently: only a real backend value gets a percentage.
    rows.append(("Estimated water coverage", water_text, "ia-dark" if water is not None else "ia-muted"))
    rows.append(("Road / access impact", road_text, "ia-dark"))

    condition_rows = "".join(
        f'<div class="ia-condition-row"><span>{_safe(label)}</span><strong class="{cls}">{_safe(value)}</strong></div>'
        for label, value, cls in rows
    )

    action_rows = []
    for i, action in enumerate(_professional_actions(result), 1):
        priority = action["priority"]
        priority_class = {
            "HIGH": "ia-action-high",
            "MEDIUM": "ia-action-medium",
            "MONITOR": "ia-action-monitor",
            "ROUTINE": "ia-action-routine",
        }.get(priority, "ia-action-info")
        action_rows.append(
            f'<div class="ia-action-row"><span class="ia-action-num">{i:02d}</span>'
            f'<div class="ia-action-content"><div class="ia-action-title">{_safe(action["title"])}</div>'
            f'<div class="ia-action-desc">{_safe(action["description"])}</div></div>'
            f'<span class="ia-action-priority {priority_class}">{_safe(priority)}</span></div>'
        )

    analyzed_images = result.get("analyzed_images") or []
    preview_html = (f'<div class="ia-result-preview"><img src="{_safe(analyzed_images[0])}" alt="Analyzed image"></div>' if analyzed_images else "")

    _html(
        '<div class="ia-section-title">Analysis Results</div>'
        '<div class="ia-assessment-banner">'
        f'{preview_html}'
        '<div><div class="ia-eyebrow">IMAGE ASSESSMENT</div>'
        f'<div class="ia-assessment-title {status_class}">{_safe(risk_level)}</div>'
        f'<div class="ia-assessment-copy">{_safe(result.get("context", ""))}</div></div>'
        f'<div class="ia-metric"><strong>{_safe(confidence_text)}</strong><span>Confidence</span></div>'
        '</div>'
        '<div class="ia-prof-grid">'
        '<div class="ia-prof-card"><h3>Detected Conditions</h3>'
        f'{condition_rows}'
        '<div class="ia-observation"><span>Observed condition</span>'
        f'<p>{_safe(result.get("context", ""))}</p></div></div>'
        '<div class="ia-prof-card"><h3>Recommended Actions</h3>'
        f'{"".join(action_rows)}</div></div>'
        '<div class="ia-result-note">Model confidence describes classification certainty. Measurements marked “Not available” were not produced by the current image classifier; no placeholder percentage is inserted.</div>'
    )


def _render_accuracy_panel(result: dict[str, Any]) -> None:
    # Confidence is already presented in the assessment summary; avoid duplicate AI-info panels.
    return


def render_image_analysis() -> None:
    _ensure_state()
    _inject_image_analysis_css()
    _render_header()

    upload_col, sample_col = st.columns([1.45, 1], gap="large")

    with upload_col:
        _render_upload_area()

    with sample_col:
        _render_recent_samples()

    _render_gallery_if_open()

    result = st.session_state.image_analysis_result
    _render_results(result)
    _render_accuracy_panel(result)
