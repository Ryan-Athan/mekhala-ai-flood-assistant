from __future__ import annotations

from textwrap import dedent

import streamlit as st


def load_global_css() -> None:
    st.markdown(
        dedent(
            """
            <style>
            :root {
                --bg-light: #bde2f1;
                --bg-mid: #82c8e5;
                --bg-dark: #47aed9;
                --navy: #003152;
                --navy-soft: rgba(0, 49, 82, 0.74);
                --white: #fafafa;
                --glass: rgba(255, 255, 255, 0.24);
                --glass-inner: rgba(255, 255, 255, 0.31);
                --border: rgba(255, 255, 255, 0.45);
                --blue: #34b9df;
                --red: #b42f31;
                --red-light: #ee8c8e;
                --yellow: #e2ba38;
                --yellow-light: #eed78c;
                --yellow-dark: #9b7804;
                --green: #049b41;
                --green-light: #8ceeb4;
            }

            html,
            body,
            [class*="css"] {
                font-family: Inter, -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif !important;
            }

            .stApp {
                background:
                    radial-gradient(circle at 15% 0%, rgba(255,255,255,0.58) 0%, rgba(255,255,255,0) 35%),
                    linear-gradient(145deg, #bde2f1 0%, #82c8e5 52%, #47aed9 100%) !important;
                color: var(--navy) !important;
                overflow-x: hidden !important;
            }

            header[data-testid="stHeader"] {
                height: 0 !important;
                min-height: 0 !important;
                background: transparent !important;
                visibility: hidden !important;
            }

            #MainMenu,
            footer,
            .stDeployButton {
                display: none !important;
                visibility: hidden !important;
            }

            .block-container {
                max-width: 930px !important;
                padding-top: 1.25rem !important;
                padding-left: 2.05rem !important;
                padding-right: 1.7rem !important;
                padding-bottom: 3rem !important;
            }

            h1, h2, h3, h4, h5, h6, p, label, span, div {
                color: var(--navy);
            }

            div[data-testid="stVerticalBlock"],
            div[data-testid="stHorizontalBlock"],
            div[data-testid="stBlock"],
            div.element-container,
            div[data-testid="stElementContainer"] {
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
            }

            section[data-testid="stSidebar"] {
                width: 285px !important;
                min-width: 285px !important;
                background: rgba(189, 226, 241, 0.62) !important;
                backdrop-filter: blur(22px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(22px) saturate(180%) !important;
                border-right: 1px solid rgba(255,255,255,0.38) !important;
                box-shadow: 8px 0 30px rgba(0, 49, 82, 0.06) !important;
            }

            section[data-testid="stSidebar"] > div {
                padding: 1.15rem 0.85rem 3.5rem 0.85rem !important;
            }

            .fm-brand {
                display: flex;
                align-items: center;
                gap: 10px;
                margin: 6px 0 74px 0;
            }

            .fm-brand-logo {
                font-size: 30px;
                line-height: 1;
                color: var(--navy);
            }

            .fm-brand-name {
                color: var(--navy);
                font-size: 30px;
                font-weight: 950;
                letter-spacing: -1.1px;
                line-height: 1;
            }

            div[role="radiogroup"] {
                display: flex !important;
                flex-direction: column !important;
                gap: 12px !important;
            }

            div[role="radiogroup"] label {
                min-height: 43px !important;
                padding: 8px 13px !important;
                border-radius: 7px !important;
                border: 1px solid transparent !important;
                background: transparent !important;
                color: var(--navy) !important;
                font-weight: 850 !important;
                transition: 0.2s ease !important;
            }

            div[role="radiogroup"] label:hover {
                background: rgba(255,255,255,0.42) !important;
                border-color: rgba(255,255,255,0.45) !important;
            }

            div[role="radiogroup"] label:has(input:checked) {
                background: rgba(250,250,250,0.94) !important;
                border-color: rgba(255,255,255,0.75) !important;
                box-shadow: 0 10px 24px rgba(0,49,82,0.08) !important;
            }

            .fm-footer-pill {
                position: fixed;
                left: 15px;
                bottom: 14px;
                width: fit-content;
                padding: 7px 13px;
                border-radius: 999px;
                background: rgba(255,255,255,0.22);
                border: 1px solid rgba(255,255,255,0.48);
                backdrop-filter: blur(18px) saturate(180%);
                -webkit-backdrop-filter: blur(18px) saturate(180%);
                color: var(--navy);
                font-size: 11px;
                font-weight: 950;
                box-shadow: 0 10px 26px rgba(0,49,82,0.06);
            }

            .fm-page-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 20px;
                margin: 0 0 20px 0;
                padding: 0;
            }

            .fm-page-title {
                margin: 0;
                color: var(--navy);
                font-size: 28px;
                line-height: 1.1;
                font-weight: 950;
                letter-spacing: -0.65px;
            }

            .fm-ai-badge {
                padding: 9px 16px;
                border-radius: 999px;
                background: rgba(250,250,250,0.95);
                border: 1px solid rgba(255,255,255,0.80);
                color: #75c8e7;
                font-size: 11px;
                font-weight: 950;
                text-transform: uppercase;
                box-shadow: 0 8px 22px rgba(0,49,82,0.08);
            }

            .fm-sim-main-card,
            .fm-result-card,
            .fm-action-panel,
            .fm-weather-card {
                width: 100%;
                border-radius: 16px;
                background: rgba(255,255,255,0.18);
                border: 1px solid rgba(255,255,255,0.42);
                backdrop-filter: blur(22px) saturate(185%);
                -webkit-backdrop-filter: blur(22px) saturate(185%);
                box-shadow: 0 12px 36px rgba(0,49,82,0.055);
            }

            .fm-sim-main-card {
                padding: 22px 22px 16px 22px;
            }

            .fm-card-title {
                margin: 0 0 14px 0;
                color: var(--navy);
                font-size: 21px;
                font-weight: 950;
                line-height: 1.1;
                letter-spacing: -0.25px;
            }

            .fm-card-desc {
                margin: 0 0 15px 0;
                color: var(--navy-soft);
                font-size: 13px;
                font-weight: 720;
                line-height: 1.62;
            }

            .fm-sim-section {
                margin: 0 0 11px 0;
                padding: 17px 22px 15px 22px;
                border-radius: 12px;
                background: rgba(255,255,255,0.26);
                border: 1px solid rgba(255,255,255,0.30);
                box-shadow: 0 8px 20px rgba(0,49,82,0.035);
            }

            .fm-sim-section:last-child {
                margin-bottom: 0;
            }

            .fm-section-title {
                margin: 0 0 22px 0;
                color: var(--navy);
                font-size: 18px;
                font-weight: 950;
                letter-spacing: -0.2px;
                line-height: 1.1;
            }

            .fm-control {
                margin: 0 0 25px 0;
            }

            .fm-control:last-child {
                margin-bottom: 0;
            }

            .fm-control-head {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 12px;
                margin-bottom: 8px;
            }

            .fm-control-label {
                color: var(--navy);
                font-size: 12px;
                font-weight: 900;
                line-height: 1.15;
            }

            .fm-chip {
                min-width: 52px;
                text-align: center;
                padding: 7px 10px;
                border-radius: 7px;
                font-size: 12px;
                font-weight: 950;
                line-height: 1;
            }

            .fm-chip-red {
                background: var(--red-light);
                color: var(--red);
            }

            .fm-chip-yellow {
                background: var(--yellow-light);
                color: var(--yellow-dark);
            }

            .fm-chip-green {
                background: var(--green-light);
                color: var(--green);
            }

            .fm-chip-white {
                background: rgba(250,250,250,0.88);
                color: rgba(0,49,82,0.48);
            }

            .fm-track {
                position: relative;
                height: 18px;
                margin: 0 0 1px 0;
            }

            .fm-track-bg {
                position: absolute;
                left: 0;
                right: 0;
                top: 7px;
                height: 4px;
                border-radius: 999px;
                background: rgba(255,255,255,0.88);
            }

            .fm-track-fill {
                position: absolute;
                left: 0;
                top: 7px;
                height: 4px;
                border-radius: 999px;
                background: var(--blue);
                box-shadow: 0 0 10px rgba(52,185,223,0.34);
            }

            .fm-knob {
                position: absolute;
                top: 0;
                width: 17px;
                height: 17px;
                border-radius: 999px;
                background: var(--navy);
                border: 2px solid rgba(255,255,255,0.55);
                box-shadow: 0 4px 14px rgba(0,49,82,0.24);
                transform: translateX(-50%);
            }

            .fm-ticks {
                display: flex;
                justify-content: space-between;
                gap: 8px;
                margin: 0;
            }

            .fm-ticks span {
                color: rgba(0,49,82,0.70);
                font-size: 10.5px;
                font-weight: 760;
                line-height: 1.22;
            }

            .fm-result-card {
                padding: 22px 28px 28px 28px;
                margin-bottom: 24px;
                border-radius: 16px;
                background: rgba(255, 255, 255, 0.18) !important;
                border: 1px solid rgba(255, 255, 255, 0.46) !important;
                backdrop-filter: blur(22px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(22px) saturate(180%) !important;
                box-shadow: 0 12px 36px rgba(0, 49, 82, 0.055) !important;
            }

            .fm-result-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 22px;
                align-items: center;
                margin-top: 16px;
            }

            .fm-gauge-wrap {
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .fm-gauge {
                width: 176px;
                height: 176px;
                border-radius: 50%;
                display: grid;
                place-items: center;
            }

            .fm-gauge-inner {
                width: 130px;
                height: 130px;
                border-radius: 50%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                background: rgba(189,226,241,0.94);
                border: 1px solid rgba(255,255,255,0.42);
                text-align: center;
            }

            .fm-gauge-value {
                font-size: 32px;
                font-weight: 950;
                line-height: 1;
            }

            .fm-gauge-label {
                margin-top: 10px;
                color: rgba(0,49,82,0.74);
                font-size: 11px;
                font-weight: 850;
            }

            .fm-risk-pill {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                min-width: 156px;
                margin-bottom: 18px;
                padding: 12px 16px;
                border-radius: 7px;
                font-size: 16px;
                font-weight: 950;
            }

            .fm-result-copy {
                color: rgba(0, 49, 82, 0.74);
                font-size: 13px;
                font-weight: 720;
                line-height: 1.62;
            }

            .fm-metric-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
                margin-top: 20px;
            }

            .fm-metric {
                min-height: 68px;
                padding: 13px 14px;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.30) !important;
                border: 1px solid rgba(255, 255, 255, 0.42) !important;
                box-shadow: 0 0 8px rgba(0, 49, 82, 0.035);
            }

            .fm-metric-label {
                color: rgba(0,49,82,0.78);
                font-size: 12px;
                font-weight: 900;
                margin-bottom: 8px;
            }

            .fm-metric-value {
                color: var(--navy);
                font-size: 20px;
                font-weight: 950;
                text-align: right;
            }

            .fm-action-panel {
                padding: 24px 28px 28px 28px;
                margin-bottom: 24px;
            }

            .fm-action-heading {
                color: var(--red);
                font-size: 21px;
                font-weight: 950;
                margin: 0 0 15px 0;
            }

            .fm-action-card {
                display: flex;
                gap: 14px;
                margin-bottom: 10px;
                padding: 14px;
                border-radius: 8px;
                background: rgba(255,255,255,0.32);
                border: 1px solid rgba(255,255,255,0.36);
            }

            .fm-action-card:last-child {
                margin-bottom: 0;
            }

            .fm-action-icon {
                font-size: 20px;
                line-height: 1.25;
            }

            .fm-action-title {
                color: var(--navy);
                font-size: 17px;
                font-weight: 950;
                margin-bottom: 4px;
            }

            .fm-action-text {
                color: rgba(0,49,82,0.78);
                font-size: 13px;
                font-weight: 700;
                line-height: 1.45;
            }

            .fm-weather-card {
                padding: 23px 28px;
                background:
                    linear-gradient(135deg, rgba(255,255,255,0.22), rgba(255,255,255,0.08)),
                    rgba(255,255,255,0.10) !important;
                border: 1px solid rgba(255,255,255,0.50) !important;
            }

            .fm-weather-title {
                color: #ffffff !important;
                font-size: 20px;
                font-weight: 950;
                margin-bottom: 20px;
                text-shadow: 0 2px 10px rgba(0,49,82,0.16);
            }

            .fm-weather-row {
                display: grid;
                grid-template-columns: 1fr auto;
                gap: 30px;
                align-items: end;
            }

            .fm-temp {
                color: #ffffff !important;
                font-size: 34px;
                font-weight: 950;
                line-height: 1;
                margin-bottom: 8px;
            }

            .fm-weather-copy {
                color: rgba(255,255,255,0.92) !important;
                font-size: 13px;
                font-weight: 780;
            }

            .fm-days {
                display: grid;
                grid-template-columns: repeat(4, 40px);
                gap: 12px;
                text-align: center;
            }

            .fm-day {
                color: #ffffff !important;
                font-size: 12px;
                font-weight: 850;
            }

            .fm-day span {
                display: block;
                color: #ffffff !important;
                font-size: 20px;
                margin-top: 5px;
            }

            .stButton > button {
                min-height: 43px;
                border-radius: 7px !important;
                border: 1px solid rgba(255,255,255,0.62) !important;
                background: rgba(250,250,250,0.90) !important;
                color: var(--navy) !important;
                font-weight: 850 !important;
                box-shadow: 0 8px 20px rgba(0,49,82,0.07) !important;
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

                .fm-page-header {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 10px;
                }

                .fm-result-grid,
                .fm-metric-grid,
                .fm-weather-row {
                    grid-template-columns: 1fr;
                }

                .fm-days {
                    grid-template-columns: repeat(4, minmax(36px, 1fr));
                }
            }

            @media (max-width: 768px) {
                section[data-testid="stSidebar"] {
                    width: 100% !important;
                    min-width: 100% !important;
                }

                .fm-brand {
                    margin-bottom: 24px;
                }

                .fm-footer-pill {
                    position: static;
                    margin-top: 20px;
                }
            }
            </style>
            """
        ).strip(),
        unsafe_allow_html=True,
    )

    