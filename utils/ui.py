from html import escape

import streamlit as st

from utils.constants import RISK_PALETTE


def render_page_title(title: str, subtitle: str | None = None, badge: str | None = None) -> None:
    subtitle_html = f'<div class="page-subtitle">{escape(subtitle)}</div>' if subtitle else ""
    badge_html = f'<div class="ai-badge">{escape(badge)}</div>' if badge else ""

    st.markdown(
        f"""
        <div class="page-title-row">
            <div>
                <h1 class="page-title">{escape(title)}</h1>
                {subtitle_html}
            </div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{escape(label)}</div>
            <div class="metric-value">{escape(value)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_risk_pill(risk_label: str) -> None:
    palette = RISK_PALETTE[risk_label]
    warning_icon = "⚠️" if risk_label != "Low Risk" else "✅"

    st.markdown(
        f"""
        <div class="risk-pill" style="background:{palette['soft']}; color:{palette['text']};">
            {escape(risk_label)} {warning_icon}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_gauge(probability: int, risk_label: str) -> None:
    probability = max(0, min(100, int(probability)))
    palette = RISK_PALETTE[risk_label]
    degrees = probability * 3.6

    st.markdown(
        f"""
        <div class="gauge-wrap">
            <div class="gauge"
                 style="background: conic-gradient({palette['strong']} 0deg {degrees}deg,
                                                    rgba(250,250,250,0.86) {degrees}deg 360deg);">
                <div class="gauge-inner">
                    <div class="gauge-value" style="color:{palette['strong']};">{probability}%</div>
                    <div class="gauge-caption">Flood Probability</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_action_card(icon: str, title: str, text: str) -> None:
    st.markdown(
        f"""
        <div class="action-card">
            <div class="action-icon">{escape(icon)}</div>
            <div>
                <div class="action-title">{escape(title)}</div>
                <div class="action-text">{escape(text)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_forecast_card() -> None:
    st.markdown(
        """
        <div class="forecast-card">
            <div class="forecast-title">Local Weather Forecast</div>
            <div style="display:flex; justify-content:space-between; gap:24px; align-items:end;">
                <div>
                    <div class="forecast-temp">24°C</div>
                    <div class="forecast-copy">Heavy Rain Expected</div>
                </div>
                <div class="forecast-days">
                    <div>Fri<br/>☁️</div>
                    <div>Sat<br/>🌦️</div>
                    <div>Sun<br/>☀️</div>
                    <div>Mon<br/>🌧️</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sample_card(risk_label: str, icon: str) -> None:
    palette = RISK_PALETTE[risk_label]

    st.markdown(
        f"""
        <div class="sample-card">
            <div class="sample-visual">{escape(icon)}</div>
            <div class="sample-risk" style="color:{palette['strong']};">{escape(risk_label)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )