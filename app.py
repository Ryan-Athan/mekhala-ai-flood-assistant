from __future__ import annotations

import base64
from pathlib import Path
from urllib.parse import quote

from PIL import Image
import streamlit as st

from tabs.ai_assistant import render_ai_assistant
from tabs.flood_risk_predictor import render_flood_risk_predictor
from tabs.image_analysis import render_image_analysis
import utils.styling as styling


PROJECT_ROOT = Path(__file__).resolve().parent
BRAND_NAME = "Mekhala"
APP_TITLE = "Mekhala | AI Flood Risk Detection"
LOGO_PATH = PROJECT_ROOT / "assets" / "mekhala_logo.png"


def _load_page_icon():
    try:
        if LOGO_PATH.exists():
            return Image.open(LOGO_PATH)
    except Exception:
        pass
    return "🌊"


st.set_page_config(
    page_title=APP_TITLE,
    page_icon=_load_page_icon(),
    layout="wide",
    initial_sidebar_state="expanded",
)


def _image_data_uri(path: Path) -> str:
    try:
        if not path.exists():
            return ""
        suffix = path.suffix.lower().replace(".", "") or "png"
        mime = "png" if suffix == "png" else "jpeg"
        encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
        return f"data:image/{mime};base64,{encoded}"
    except Exception:
        return ""


def _brand_logo_html(class_name: str) -> str:
    logo_uri = _image_data_uri(LOGO_PATH)
    if logo_uri:
        return f'<div class="{class_name}"><img src="{logo_uri}" alt="{BRAND_NAME} logo" /></div>'
    return f'<div class="{class_name} mk-logo-fallback">🌊</div>'


PAGE_OPTIONS = {
    "Flood Risk Predictor": {
        # "icon": "🌊",
        "renderer": render_flood_risk_predictor,
    },
    "AI Flood Assistant": {
        # "icon": "🤖",
        "renderer": render_ai_assistant,
    },
    "Image Analysis": {
        # "icon": "🖼️",
        "renderer": render_image_analysis,
    },
}


def _get_query_page() -> str | None:
    try:
        value = st.query_params.get("page", None)
    except Exception:
        try:
            params = st.experimental_get_query_params()
            raw_value = params.get("page", [None])
            value = raw_value[0] if isinstance(raw_value, list) else raw_value
        except Exception:
            value = None

    if isinstance(value, list):
        value = value[0] if value else None

    if value in PAGE_OPTIONS:
        return value

    return None


def _set_query_page(page_name: str) -> None:
    try:
        st.query_params["page"] = page_name
    except Exception:
        try:
            st.experimental_set_query_params(page=page_name)
        except Exception:
            pass


def apply_existing_global_styles() -> None:
    possible_style_functions = [
        "inject_global_styles",
        "inject_global_style",
        "inject_styles",
        "inject_custom_css",
        "load_global_css",
        "apply_global_styles",
    ]

    for function_name in possible_style_functions:
        function = getattr(styling, function_name, None)
        if callable(function):
            function()
            return

    st.markdown(
        """
<style>
:root {
    --navy: #003152;
}

html,
body,
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #bde2f1 0%, #82c8e5 52%, #47aed9 100%) !important;
    color: #003152 !important;
}

.main .block-container {
    padding-top: 1.25rem !important;
}

#MainMenu,
footer,
header {
    visibility: hidden !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def inject_desktop_sidebar_css() -> None:
    st.markdown(
        """
<style>
section[data-testid="stSidebar"] {
    width: 285px !important;
    min-width: 285px !important;
    max-width: 285px !important;
    background: linear-gradient(
        180deg,
        rgba(189, 226, 241, 0.98) 0%,
        rgba(130, 200, 229, 0.90) 58%,
        rgba(71, 174, 217, 0.82) 100%
    ) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.42) !important;
    box-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.18) !important;
}

section[data-testid="stSidebar"] > div {
    background: transparent !important;
}

section[data-testid="stSidebar"] div[data-testid="stSidebarHeader"] {
    display: none !important;
}

div[data-testid="collapsedControl"],
div[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}

section[data-testid="stSidebar"] .block-container,
section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"],
section[data-testid="stSidebar"] .element-container {
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
}

section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

.mk-sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 72px 0 78px 16px;
    padding: 0;
}

.mk-sidebar-logo {
    width: 48px;
    height: 48px;
    min-width: 48px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    padding: 6px;
    background: rgba(250, 250, 250, 0.82);
    border: 1px solid rgba(255, 255, 255, 0.86);
    box-shadow:
        0 14px 30px rgba(0, 49, 82, 0.12),
        inset 0 1px 0 rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(16px) saturate(180%);
    -webkit-backdrop-filter: blur(16px) saturate(180%);
}

.mk-sidebar-logo img {
    width: 38px;
    height: 38px;
    object-fit: contain;
    display: block;
    border-radius: 50%;
}

.mk-logo-fallback {
    color: #003152;
    font-size: 26px;
    line-height: 1;
}

.mk-sidebar-title {
    color: #003152;
    font-size: 31px;
    line-height: 1;
    font-weight: 950;
    letter-spacing: -0.9px;
}

section[data-testid="stSidebar"] div[data-testid="stRadio"] > label {
    display: none !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 19px !important;
    padding: 0 14px 0 14px !important;
}

section[data-testid="stSidebar"] label[data-baseweb="radio"] {
    width: 100% !important;
    min-height: 43px !important;
    margin: 0 !important;
    padding: 0 17px !important;
    border-radius: 8px !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    box-shadow: none !important;
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    cursor: pointer !important;
    transition: all 0.22s ease !important;
}

section[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) {
    background: rgba(250, 250, 250, 0.94) !important;
    border: 1px solid rgba(255, 255, 255, 0.72) !important;
    box-shadow: 0 12px 24px rgba(0, 49, 82, 0.07) !important;
}

section[data-testid="stSidebar"] label[data-baseweb="radio"] > div:first-child {
    width: 17px !important;
    height: 17px !important;
    min-width: 17px !important;
    border-radius: 999px !important;
    border: 1.5px solid rgba(0, 49, 82, 0.26) !important;
    background: rgba(255, 255, 255, 0.14) !important;
    box-shadow: none !important;
    display: grid !important;
    place-items: center !important;
}

section[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) > div:first-child {
    background: #003152 !important;
    border-color: #003152 !important;
}

section[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) > div:first-child::after {
    content: "";
    width: 6px;
    height: 6px;
    border-radius: 999px;
    background: #fafafa;
}

section[data-testid="stSidebar"] label[data-baseweb="radio"] svg {
    display: none !important;
}

section[data-testid="stSidebar"] label[data-baseweb="radio"] p,
section[data-testid="stSidebar"] label[data-baseweb="radio"] div[data-testid="stMarkdownContainer"] p {
    margin: 0 !important;
    color: #003152 !important;
    font-size: 13.5px !important;
    line-height: 1 !important;
    font-weight: 720 !important;
    white-space: nowrap !important;
}

section[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) p {
    font-weight: 780 !important;
}

section[data-testid="stSidebar"] label[data-baseweb="radio"]:hover {
    background: rgba(255, 255, 255, 0.28) !important;
}

.mk-sidebar-footer {
    position: fixed;
    left: 20px;
    bottom: 22px;
    width: 172px;
    height: 36px;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #003152;
    font-size: 11px;
    font-weight: 900;
    background: rgba(255, 255, 255, 0.18);
    border: 1px solid rgba(255, 255, 255, 0.48);
    box-shadow: 0 10px 24px rgba(0, 49, 82, 0.06);
    backdrop-filter: blur(18px) saturate(180%);
    -webkit-backdrop-filter: blur(18px) saturate(180%);
}
</style>
        """,
        unsafe_allow_html=True,
    )


def inject_mobile_css() -> None:
    st.markdown(
        """
<style>
html,
body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {
    overflow-x: hidden !important;
}

.mk-mobile-menu-button,
.mk-mobile-menu,
.mk-mobile-menu-backdrop {
    display: none;
}

/* ===============================
   PHONE + TABLET ENGINE
================================ */
@media (max-width: 900px) {
    section[data-testid="stSidebar"] {
        display: none !important;
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    .mk-mobile-menu-button {
        position: fixed !important;
        top: 20px !important;
        left: 20px !important;
        z-index: 9999999 !important;

        width: 46px !important;
        height: 46px !important;
        border-radius: 999px !important;

        display: flex !important;
        align-items: center !important;
        justify-content: center !important;

        background: rgba(250, 250, 250, 0.94) !important;
        border: 1px solid rgba(255, 255, 255, 0.78) !important;
        color: #003152 !important;

        text-decoration: none !important;
        font-size: 26px !important;
        font-weight: 950 !important;
        line-height: 1 !important;

        box-shadow: 0 14px 34px rgba(0, 49, 82, 0.16) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
    }

    .mk-mobile-menu {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        bottom: 0 !important;

        width: min(82vw, 310px) !important;
        max-width: min(82vw, 310px) !important;
        height: 100dvh !important;

        z-index: 9999998 !important;

        transform: translateX(-110%) !important;
        transition: transform 0.28s ease-in-out !important;

        display: block !important;

        background: linear-gradient(
            180deg,
            rgba(189, 226, 241, 0.98) 0%,
            rgba(130, 200, 229, 0.96) 58%,
            rgba(71, 174, 217, 0.92) 100%
        ) !important;

        border-right: 1px solid rgba(255, 255, 255, 0.50) !important;
        box-shadow: 24px 0 55px rgba(0, 49, 82, 0.22) !important;

        padding: 108px 18px 80px 18px !important;
        box-sizing: border-box !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
    }

    .mk-mobile-menu:target {
        transform: translateX(0) !important;
    }

    .mk-mobile-menu:target ~ .mk-mobile-menu-backdrop {
        display: block !important;
    }

    .mk-mobile-close {
        position: absolute !important;
        top: 20px !important;
        right: 18px !important;

        width: 46px !important;
        height: 46px !important;
        border-radius: 999px !important;

        display: flex !important;
        align-items: center !important;
        justify-content: center !important;

        background: rgba(255, 255, 255, 0.34) !important;
        border: 1px solid rgba(255, 255, 255, 0.66) !important;
        color: #003152 !important;

        text-decoration: none !important;
        font-size: 27px !important;
        font-weight: 950 !important;

        box-shadow: 0 14px 34px rgba(0, 49, 82, 0.10) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
    }

    .mk-mobile-menu-backdrop {
        position: fixed !important;
        inset: 0 !important;
        z-index: 9999997 !important;
        background: rgba(0, 49, 82, 0.16) !important;
        backdrop-filter: blur(1.5px) !important;
        -webkit-backdrop-filter: blur(1.5px) !important;
    }

    .mk-mobile-brand {
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        margin: 0 0 52px 0 !important;
    }

    .mk-mobile-logo {
        width: 48px !important;
        height: 48px !important;
        min-width: 48px !important;
        border-radius: 50% !important;
        display: grid !important;
        place-items: center !important;
        padding: 6px !important;
        background: rgba(250, 250, 250, 0.82) !important;
        border: 1px solid rgba(255, 255, 255, 0.86) !important;
        box-shadow: 0 14px 30px rgba(0, 49, 82, 0.12) !important;
    }

    .mk-mobile-logo img {
        width: 38px !important;
        height: 38px !important;
        object-fit: contain !important;
        display: block !important;
        border-radius: 50% !important;
    }

    .mk-mobile-title {
        color: #003152 !important;
        font-size: 29px !important;
        font-weight: 950 !important;
        letter-spacing: -0.8px !important;
        line-height: 1 !important;
        white-space: nowrap !important;
    }

    .mk-mobile-nav {
        display: flex !important;
        flex-direction: column !important;
        gap: 15px !important;
    }

    .mk-mobile-nav-link {
        min-height: 45px !important;
        border-radius: 9px !important;

        display: flex !important;
        align-items: center !important;
        gap: 11px !important;

        padding: 0 16px !important;

        text-decoration: none !important;
        color: #003152 !important;
        font-size: 13.5px !important;
        font-weight: 760 !important;

        background: transparent !important;
        border: 1px solid transparent !important;
        transition: all 0.2s ease !important;
    }

    .mk-mobile-nav-link.active {
        background: rgba(250, 250, 250, 0.94) !important;
        border: 1px solid rgba(255, 255, 255, 0.72) !important;
        box-shadow: 0 12px 24px rgba(0, 49, 82, 0.07) !important;
        font-weight: 850 !important;
    }

    .mk-mobile-dot {
        width: 17px !important;
        height: 17px !important;
        border-radius: 999px !important;
        border: 1.5px solid rgba(0, 49, 82, 0.26) !important;
        background: rgba(255, 255, 255, 0.14) !important;
        display: grid !important;
        place-items: center !important;
        flex: 0 0 17px !important;
    }

    .mk-mobile-nav-link.active .mk-mobile-dot {
        background: #003152 !important;
        border-color: #003152 !important;
    }

    .mk-mobile-nav-link.active .mk-mobile-dot::after {
        content: "";
        width: 6px;
        height: 6px;
        border-radius: 999px;
        background: #fafafa;
    }

    .mk-mobile-footer {
        position: fixed !important;
        left: 18px !important;
        bottom: 18px !important;

        width: 172px !important;
        height: 36px !important;
        border-radius: 999px !important;

        display: flex !important;
        align-items: center !important;
        justify-content: center !important;

        color: #003152 !important;
        font-size: 11px !important;
        font-weight: 900 !important;

        background: rgba(255, 255, 255, 0.18) !important;
        border: 1px solid rgba(255, 255, 255, 0.48) !important;
        box-shadow: 0 10px 24px rgba(0, 49, 82, 0.06) !important;
        backdrop-filter: blur(18px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(18px) saturate(180%) !important;
    }

    .main .block-container {
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;

        margin: 0 auto !important;

        padding-left: 1.15rem !important;
        padding-right: 1.15rem !important;
        padding-top: 6.25rem !important;
        padding-bottom: 3rem !important;

        overflow-x: hidden !important;
        box-sizing: border-box !important;
    }

    .main .block-container * {
        min-width: 0 !important;
        box-sizing: border-box !important;
    }

    div[data-testid="stHorizontalBlock"] {
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;

        display: flex !important;
        flex-direction: column !important;
        flex-wrap: nowrap !important;

        gap: 1rem !important;
    }

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
        flex: 1 1 100% !important;
    }

    .fm-page-header {
        width: 100% !important;
        max-width: 100% !important;

        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;

        gap: 0.85rem !important;
        margin: 0 0 1.35rem 0 !important;
        padding: 0 !important;
    }

    .fm-page-title,
    .ia-page-title,
    .fm-assistant-title,
    .main h1 {
        width: 100% !important;
        max-width: 100% !important;

        margin-left: 0 !important;
        margin-right: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;

        color: #003152 !important;
        font-size: clamp(2.05rem, 9.2vw, 3.05rem) !important;
        line-height: 1.12 !important;
        letter-spacing: -0.065rem !important;

        text-align: left !important;
        white-space: normal !important;
        word-break: normal !important;
        overflow-wrap: normal !important;
    }

    .ia-page-subtitle,
    .fm-assistant-subtitle,
    .main p {
        max-width: 100% !important;
        white-space: normal !important;
        overflow-wrap: normal !important;
    }

    .fm-ai-badge {
        align-self: flex-start !important;
    }

    .fm-sim-main-card,
    .fm-result-card,
    .fm-action-panel,
    .fm-weather-card,
    .ia-result-card,
    .ia-accuracy-panel {
        width: 100% !important;
        max-width: 100% !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
    }

    .fm-result-grid,
    .fm-metric-grid,
    .fm-weather-row,
    .ia-result-grid,
    .ia-accuracy-panel {
        display: grid !important;
        grid-template-columns: 1fr !important;
        width: 100% !important;
        max-width: 100% !important;
        gap: 1rem !important;
    }

    .fm-gauge {
        width: min(64vw, 210px) !important;
        height: min(64vw, 210px) !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    .fm-gauge-inner {
        width: 72% !important;
        height: 72% !important;
    }

    .fm-days {
        grid-template-columns: repeat(4, minmax(38px, 1fr)) !important;
        width: 100% !important;
    }

    .ia-page-title {
        font-size: clamp(2.15rem, 9.5vw, 3.05rem) !important;
        line-height: 1.1 !important;
        margin-bottom: 0.75rem !important;
    }

    .ia-page-subtitle {
        margin-bottom: 1.75rem !important;
        font-size: 0.92rem !important;
        line-height: 1.55 !important;
    }

    .ia-samples-title {
        text-align: left !important;
        margin-top: 1.35rem !important;
        margin-bottom: 0.9rem !important;
    }

    .ia-sample-grid {
        display: grid !important;
        grid-template-columns: 1fr !important;
        gap: 1rem !important;
        width: 100% !important;
    }

    .ia-sample-card,
    .ia-add-card {
        width: 100% !important;
        max-width: 100% !important;
        min-height: 150px !important;
    }

    .ia-upload-content {
        width: 100% !important;
        max-width: 100% !important;
        padding-left: 0.7rem !important;
        padding-right: 0.7rem !important;
    }

    .ia-upload-title {
        width: 100% !important;
        max-width: 100% !important;

        font-size: clamp(1.22rem, 5.25vw, 1.55rem) !important;
        line-height: 1.24 !important;

        text-align: center !important;
        white-space: normal !important;
        word-break: normal !important;
        overflow-wrap: normal !important;
    }

    .ia-upload-copy {
        width: 100% !important;
        max-width: 100% !important;

        font-size: 0.72rem !important;
        line-height: 1.45 !important;

        text-align: center !important;
        white-space: normal !important;
        word-break: normal !important;
        overflow-wrap: normal !important;
    }

    .fm-chat-active,
    .fm-chat-history,
    .fm-assistant-empty {
        width: 100% !important;
        max-width: 100% !important;
    }

    .fm-assistant-empty {
        margin-top: 1rem !important;
        text-align: left !important;
    }

    .fm-assistant-hero {
        align-items: flex-start !important;
    }

    .fm-assistant-bot {
        align-self: center !important;
    }

    .fm-chat-content {
        max-width: 86% !important;
    }

    .fm-chat-bubble {
        font-size: 0.88rem !important;
        line-height: 1.55 !important;
        padding: 0.85rem 1rem !important;
    }

    div[data-testid="stForm"] {
        width: 100% !important;
        max-width: 100% !important;
    }

    div[data-testid="stForm"] div[data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: 1fr 56px !important;
        gap: 0.75rem !important;
        align-items: center !important;
        flex-direction: row !important;
    }

    div[data-testid="stForm"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        min-width: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
    }
}

@media (max-width: 430px) {
    .main .block-container {
        padding-left: 0.9rem !important;
        padding-right: 0.9rem !important;
        padding-top: 6.15rem !important;
    }

    .fm-page-title,
    .ia-page-title,
    .fm-assistant-title,
    .main h1 {
        font-size: clamp(1.95rem, 9.1vw, 2.58rem) !important;
        line-height: 1.13 !important;
    }

    .fm-sim-main-card,
    .fm-result-card,
    .fm-action-panel,
    .fm-weather-card {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .fm-sim-section {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .fm-section-title {
        font-size: 1.05rem !important;
    }

    .fm-ticks span {
        font-size: 0.62rem !important;
    }

    .ia-upload-title {
        font-size: clamp(1.14rem, 5vw, 1.38rem) !important;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def render_mobile_menu(active_page: str) -> None:
    # Keep the entire mobile menu as one compact HTML fragment.
    # Leading indentation/newlines in mixed Markdown/HTML can be interpreted as
    # a Markdown code block on some Streamlit/mobile browser combinations.
    links = []
    for page_name in PAGE_OPTIONS:
        active_class = " active" if page_name == active_page else ""
        page_url = f"?page={quote(page_name)}"
        links.append(
            f'<a class="mk-mobile-nav-link{active_class}" href="{page_url}" target="_self">'
            f'<span class="mk-mobile-dot"></span>'
            f'<span>{page_name}</span>'
            f'</a>'
        )

    menu_html = (
        '<a class="mk-mobile-menu-button" href="#mk-mobile-menu" aria-label="Open menu">☰</a>'
        '<nav id="mk-mobile-menu" class="mk-mobile-menu">'
        '<a class="mk-mobile-close" href="#" aria-label="Close menu">‹</a>'
        '<div class="mk-mobile-brand">'
        f'{_brand_logo_html("mk-mobile-logo")}'
        f'<div class="mk-mobile-title">{BRAND_NAME}</div>'
        '</div>'
        '<div class="mk-mobile-nav">'
        f'{"".join(links)}'
        '</div>'
        '<div class="mk-mobile-footer">Powered by Eggvengers</div>'
        '</nav>'
        '<a class="mk-mobile-menu-backdrop" href="#" aria-label="Close menu"></a>'
    )
    st.markdown(menu_html, unsafe_allow_html=True)

def _on_desktop_page_change() -> None:
    selected_page = st.session_state.get("desktop_active_page")
    if selected_page in PAGE_OPTIONS:
        st.session_state.active_page = selected_page
        st.session_state._last_query_page = selected_page
        _set_query_page(selected_page)


def render_desktop_sidebar(active_page: str) -> str:
    page_names = list(PAGE_OPTIONS.keys())

    with st.sidebar:
        st.markdown(
            f"""
            <div class="mk-sidebar-brand">
                {_brand_logo_html("mk-sidebar-logo")}
                <div class="mk-sidebar-title">{BRAND_NAME}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Use a separate widget key. Never use key="active_page" for the radio,
        # because active_page is the real app navigation state.
        if st.session_state.get("desktop_active_page") not in page_names:
            st.session_state.desktop_active_page = active_page
        elif st.session_state.get("desktop_active_page") != active_page:
            st.session_state.desktop_active_page = active_page

        selected_page = st.radio(
            label="Navigation",
            options=page_names,
            # format_func=lambda page: f"{PAGE_OPTIONS[page]['icon']} {page}",
            key="desktop_active_page",
            label_visibility="collapsed",
            on_change=_on_desktop_page_change,
        )

        st.markdown(
            """
            <div class="mk-sidebar-footer">
                Powered by Eggvengers
            </div>
            """,
            unsafe_allow_html=True,
        )

    return selected_page

def get_active_page() -> str:
    page_names = list(PAGE_OPTIONS.keys())
    query_page = _get_query_page()

    # First load: allow URL query like ?page=Image Analysis.
    if "active_page" not in st.session_state:
        st.session_state.active_page = query_page or "Flood Risk Predictor"
        st.session_state._last_query_page = query_page or st.session_state.active_page

    # Later: only accept query changes when the URL actually changed.
    # This prevents the old ?page=Flood Risk Predictor value from forcing
    # the app back when the sidebar radio is clicked.
    elif query_page and query_page != st.session_state.get("_last_query_page"):
        st.session_state.active_page = query_page
        st.session_state._last_query_page = query_page

    if st.session_state.active_page not in page_names:
        st.session_state.active_page = "Flood Risk Predictor"
        st.session_state._last_query_page = st.session_state.active_page

    return st.session_state.active_page

def main() -> None:
    apply_existing_global_styles()
    inject_desktop_sidebar_css()

    # IMPORTANT: inject the mobile-menu CSS before rendering its HTML.
    # Streamlit reruns (for example after Regional Forecast -> Use This Location)
    # can otherwise briefly paint the menu markup before the CSS arrives, which
    # looks like raw <div> / <a> source code flashing above the page.
    inject_mobile_css()

    active_page = get_active_page()
    render_mobile_menu(active_page)

    selected_page = render_desktop_sidebar(active_page)

    # Fallback for Streamlit versions where radio on_change does not fire in time.
    if selected_page != st.session_state.active_page:
        st.session_state.active_page = selected_page
        st.session_state._last_query_page = selected_page
        _set_query_page(selected_page)
        st.rerun()

    PAGE_OPTIONS[st.session_state.active_page]["renderer"]()

if __name__ == "__main__":
    main()