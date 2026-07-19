from __future__ import annotations
from utils.weather_service import get_realtime_weather

from html import escape
from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v1 as components


RISK_PALETTE = {
    "Low Risk": {
        "soft": "#8ceeb4",
        "strong": "#049b41",
        "text": "#049b41",
    },
    "Medium Risk": {
        "soft": "#eed78c",
        "strong": "#e2ba38",
        "text": "#9b7804",
    },
    "High Risk": {
        "soft": "#ee8c8e",
        "strong": "#b42f31",
        "text": "#b42f31",
    },
}


# These values match the UI you showed in the screenshot.
# Reset Values returns to these values, not 0.
DEFAULT_INPUTS = {
    "rainfall": 2,          # High, 75%
    "weather_worse": 1,    # Same, 34%
    "area_type": 2,        # Hilly, 67%
    "coast_distance": 3,   # Not Sure, 100%
    "river_control": 3,    # Not Sure, 94%
    "dam_condition": 1,    # Average, 34%
    "drainage_quality": 2, # Strong, 68%
}


CONTROL_CONFIG = {
    "rainfall": {
        "label": "Rainfall Level",
        "ticks": ["Light", "Medium", "Heavy", "Extreme"],
        "chips": ["Light", "Medium", "High", "Extreme"],
        "classes": ["fm-chip-green", "fm-chip-yellow", "fm-chip-red", "fm-chip-red"],
        "percents": [8, 34, 75, 100],
        "risk_scores": [20, 48, 75, 95],
    },
    "weather_worse": {
        "label": "Weather getting worse?",
        "ticks": ["Less<br>worse", "Same", "Worse", "Not sure"],
        "chips": ["Less", "Same", "Worse", "Not Sure"],
        "classes": ["fm-chip-green", "fm-chip-yellow", "fm-chip-red", "fm-chip-white"],
        "percents": [8, 34, 68, 100],
        "risk_scores": [25, 50, 78, 58],
    },
    "area_type": {
        "label": "Area Type",
        "ticks": ["Low land", "Slightly<br>elevated", "Hilly", "Not sure"],
        "chips": ["Low land", "Slightly", "Hilly", "Not Sure"],
        "classes": ["fm-chip-red", "fm-chip-yellow", "fm-chip-green", "fm-chip-white"],
        "percents": [8, 34, 67, 100],
        "risk_scores": [85, 60, 42, 58],
    },
    "coast_distance": {
        "label": "Distance to coast",
        "ticks": ["Inland", "Near", "Coastal", "Not sure"],
        "chips": ["Inland", "Near", "Coastal", "Not Sure"],
        "classes": ["fm-chip-green", "fm-chip-yellow", "fm-chip-red", "fm-chip-white"],
        "percents": [8, 34, 68, 100],
        "risk_scores": [28, 52, 76, 58],
    },
    "river_control": {
        "label": "River control",
        "ticks": ["Poor", "Average", "Strong", "Not Sure"],
        "chips": ["Poor", "Average", "Strong", "Not Sure"],
        "classes": ["fm-chip-red", "fm-chip-yellow", "fm-chip-green", "fm-chip-white"],
        "percents": [8, 34, 68, 94],
        "risk_scores": [82, 55, 28, 58],
    },
    "dam_condition": {
        "label": "Dam condition",
        "ticks": ["Poor", "Average", "Strong", "Not sure"],
        "chips": ["Poor", "Average", "Strong", "Not Sure"],
        "classes": ["fm-chip-red", "fm-chip-yellow", "fm-chip-green", "fm-chip-white"],
        "percents": [8, 34, 68, 100],
        "risk_scores": [82, 55, 30, 58],
    },
    "drainage_quality": {
        "label": "Drainage quality",
        "ticks": ["Poor", "Average", "Strong", "Not sure"],
        "chips": ["Poor", "Average", "Strong", "Not Sure"],
        "classes": ["fm-chip-red", "fm-chip-yellow", "fm-chip-green", "fm-chip-white"],
        "percents": [8, 34, 68, 100],
        "risk_scores": [82, 55, 30, 58],
    },
}


WEIGHTS = {
    "rainfall": 0.24,
    "weather_worse": 0.12,
    "area_type": 0.14,
    "coast_distance": 0.10,
    "river_control": 0.14,
    "dam_condition": 0.13,
    "drainage_quality": 0.13,
}


COMPONENT_DIR = Path(__file__).resolve().parents[1] / "components" / "fm_risk_controls"
_fm_risk_controls = components.declare_component("fm_risk_controls", path=str(COMPONENT_DIR))


def _safe(value: object) -> str:
    return escape(str(value))


def _html(markup: str) -> None:
    st.markdown(markup.strip(), unsafe_allow_html=True)


def _default_prediction_result() -> dict:
    return {
        "probability": 58,
        "risk_label": "Medium Risk",
        "confidence": 94,
        "predicted_peak": "04:30 AM",
        "explanation": "Flood risk is currently moderate at 58%. Conditions suggest flooding is possible if rainfall continues.",
        "actions": [
            {
                "icon": "📢",
                "title": "Notify Residents",
                "text": "Send early warning notifications to residents in Flood Risk Zone to stay alert and monitor updates.",
            },
            {
                "icon": "🛡️",
                "title": "Prepare Flood Barriers",
                "text": "Check and prepare flood gates and barriers in case water levels rise.",
            },
            {
                "icon": "⛑️",
                "title": "Standby Emergency Teams",
                "text": "Keep response teams ready for quick deployment.",
            },
        ],
    }


def _ensure_defaults() -> None:
    if "frp_inputs" not in st.session_state or not isinstance(st.session_state.frp_inputs, dict):
        st.session_state.frp_inputs = DEFAULT_INPUTS.copy()

    st.session_state.frp_inputs = _sanitize_inputs(st.session_state.frp_inputs)

    if "frp_component_version" not in st.session_state:
        st.session_state.frp_component_version = 0

    if "frp_last_component_event" not in st.session_state:
        st.session_state.frp_last_component_event = None

    if "prediction_result" not in st.session_state or st.session_state.prediction_result is None:
        st.session_state.prediction_result = _default_prediction_result()


def _sanitize_inputs(raw_inputs: Any) -> dict:
    sanitized = DEFAULT_INPUTS.copy()

    if not isinstance(raw_inputs, dict):
        return sanitized

    for key, default_value in DEFAULT_INPUTS.items():
        try:
            value = int(raw_inputs.get(key, default_value))
        except (TypeError, ValueError):
            value = default_value
        sanitized[key] = max(0, min(3, value))

    return sanitized


def _reset_values() -> None:
    st.session_state.frp_inputs = DEFAULT_INPUTS.copy()
    st.session_state.prediction_result = _default_prediction_result()
    st.session_state.frp_component_version = st.session_state.get("frp_component_version", 0) + 1


def _build_model_input_payload() -> dict:
    """Clean payload for replacing the mock calculation with a real AI model later."""
    payload = {}

    for key, config in CONTROL_CONFIG.items():
        selected_index = int(st.session_state.frp_inputs.get(key, DEFAULT_INPUTS[key]))
        selected_index = max(0, min(3, selected_index))
        payload[key] = {
            "index": selected_index,
            "label": config["chips"][selected_index],
            "risk_score": config["risk_scores"][selected_index],
        }

    return payload


def _predict_with_mock_model(model_payload: dict) -> dict:
    score = 0.0

    for key, weight in WEIGHTS.items():
        score += model_payload[key]["risk_score"] * weight

    probability = int(round(score + 3))
    probability = max(5, min(98, probability))

    if probability < 40:
        risk_label = "Low Risk"
        actions = [
            {
                "icon": "✅",
                "title": "Continue Monitoring",
                "text": "Current flood risk is low, but keep checking weather and water-level updates.",
            },
            {
                "icon": "📍",
                "title": "Review Safe Routes",
                "text": "Confirm evacuation routes and avoid low-lying roads during heavy rain.",
            },
            {
                "icon": "🎒",
                "title": "Keep Essentials Ready",
                "text": "Keep basic emergency supplies ready in case rainfall increases.",
            },
        ]
        explanation = f"Flood risk is currently low at {probability}%. Conditions are stable, but monitoring should continue."
    elif probability < 70:
        risk_label = "Medium Risk"
        actions = [
            {
                "icon": "📢",
                "title": "Notify Residents",
                "text": "Send early warning notifications to residents in Flood Risk Zone to stay alert and monitor updates.",
            },
            {
                "icon": "🛡️",
                "title": "Prepare Flood Barriers",
                "text": "Check and prepare flood gates and barriers in case water levels rise.",
            },
            {
                "icon": "⛑️",
                "title": "Standby Emergency Teams",
                "text": "Keep response teams ready for quick deployment.",
            },
        ]
        explanation = f"Flood risk is currently moderate at {probability}%. Conditions suggest flooding is possible if rainfall continues."
    else:
        risk_label = "High Risk"
        actions = [
            {
                "icon": "🚨",
                "title": "Issue Flood Warning",
                "text": "Alert residents immediately and prepare evacuation support for high-risk areas.",
            },
            {
                "icon": "🛑",
                "title": "Close Unsafe Roads",
                "text": "Block flooded roads and low bridges before vehicles enter dangerous water.",
            },
            {
                "icon": "⛑️",
                "title": "Deploy Emergency Teams",
                "text": "Move rescue and medical teams closer to affected zones for fast response.",
            },
        ]
        explanation = f"Flood risk is high at {probability}%. Immediate preparation is recommended because flooding may occur soon."

    confidence = max(82, min(97, 88 + int(abs(probability - 50) / 3)))

    if probability >= 70:
        predicted_peak = "02:15 AM"
    elif probability >= 45:
        predicted_peak = "04:30 AM"
    else:
        predicted_peak = "06:45 AM"

    return {
        "probability": probability,
        "risk_label": risk_label,
        "confidence": confidence,
        "predicted_peak": predicted_peak,
        "explanation": explanation,
        "actions": actions,
    }


def _calculate_result() -> None:
    """Run the trained Flood Risk Predictor AI model.

    The UI sliders stay unchanged. The selected slider values are converted to
    the model feature format inside utils/flood_risk_model_service.py.
    Local Weather Forecast is not used in this prediction and remains separate.
    """
    try:
        from utils.flood_risk_model_service import predict_flood_risk_from_ui

        st.session_state.prediction_result = predict_flood_risk_from_ui(st.session_state.frp_inputs)
    except Exception as error:
        # Safety fallback: keep app running if model files are missing or need local retraining.
        model_payload = _build_model_input_payload()
        fallback_result = _predict_with_mock_model(model_payload)
        fallback_result["explanation"] = (
            f"AI model could not be loaded, so FloodMind used the fallback scoring result. "
            f"Model error: {error}"
        )
        fallback_result["model_source"] = "fallback_rule_based_scoring"
        st.session_state.prediction_result = fallback_result


def _render_header() -> None:
    _html(
        '<div class="fm-page-header">'
        '<h1 class="fm-page-title">Flood Risk Predictor</h1>'
        # '<div class="fm-ai-badge">Powered by AI</div>'
        '</div>'
    )


def _render_simulation_parameters() -> None:
    component_value = _fm_risk_controls(
        controls=CONTROL_CONFIG,
        values=st.session_state.frp_inputs,
        default=DEFAULT_INPUTS,
        key=f"fm_risk_controls_{st.session_state.frp_component_version}",
    )

    if not isinstance(component_value, dict):
        return

    # New component format:
    # {"action": "calculate" | "reset", "values": {...}, "event_id": "..."}
    action = component_value.get("action")
    event_id = component_value.get("event_id")
    raw_values = component_value.get("values", component_value)

    new_inputs = _sanitize_inputs(raw_values)

    input_changed = new_inputs != st.session_state.frp_inputs

    if input_changed:
        # Keep exactly the values selected by the user inside the custom slider
        # component. The model prediction must never rewrite user inputs.
        st.session_state.frp_inputs = new_inputs

    # Handle button clicks from inside the custom component only once.
    if event_id and event_id != st.session_state.get("frp_last_component_event"):
        st.session_state.frp_last_component_event = event_id

        if action == "reset":
            _reset_values()
            # Force one clean rerun so the component receives DEFAULT_INPUTS.
            st.rerun()

        elif action == "calculate":
            _calculate_result()
            # Force one clean rerun so the component receives the same user
            # selected inputs instead of repainting from stale pre-click values.
            st.rerun()


def _render_prediction(result: dict) -> None:
    risk_label = result["risk_label"]
    probability = max(0, min(100, int(result["probability"])))
    degrees = probability * 3.6
    palette = RISK_PALETTE[risk_label]
    gauge_color = palette["strong"]

    markup = (
        '<div class="fm-result-card">'
        '<div class="fm-card-title">AI Prediction Result</div>'
        '<div class="fm-result-grid">'
        '<div class="fm-gauge-wrap">'
        f'<div class="fm-gauge" style="background:conic-gradient({gauge_color} 0deg {degrees}deg, rgba(250,250,250,0.88) {degrees}deg 360deg);">'
        '<div class="fm-gauge-inner">'
        f'<div class="fm-gauge-value" style="color:{gauge_color};">{probability}%</div>'
        '<div class="fm-gauge-label">Flood Probability</div>'
        '</div>'
        '</div>'
        '</div>'
        '<div>'
        f'<div class="fm-risk-pill" style="background:{palette["soft"]}; color:{palette["text"]};">'
        f'<span>{_safe(risk_label)}</span><span>⚠️</span>'
        '</div>'
        f'<div class="fm-result-copy">{_safe(result["explanation"])}</div>'
        '</div>'
        '</div>'
        '<div class="fm-metric-grid">'
        '<div class="fm-metric">'
        '<div class="fm-metric-label">Confidence Score</div>'
        f'<div class="fm-metric-value">{_safe(result["confidence"])}%</div>'
        '</div>'
        '<div class="fm-metric">'
        '<div class="fm-metric-label">Predicted Peak</div>'
        f'<div class="fm-metric-value">{_safe(result["predicted_peak"])}</div>'
        '</div>'
        '</div>'
        '</div>'
    )

    _html(markup)


def _render_actions(result: dict) -> None:
    action_html = ""

    for action in result["actions"]:
        action_html += (
            '<div class="fm-action-card">'
            f'<div class="fm-action-icon">{_safe(action["icon"])}</div>'
            '<div>'
            f'<div class="fm-action-title">{_safe(action["title"])}</div>'
            f'<div class="fm-action-text">{_safe(action["text"])}</div>'
            '</div>'
            '</div>'
        )

    markup = (
        '<div class="fm-action-panel">'
        '<div class="fm-action-heading">Emergency Actions</div>'
        + action_html
        + '</div>'
    )

    _html(markup)


def _render_weather() -> None:
    from datetime import datetime

    try:
        from utils.weather_service import get_realtime_weather

        weather = get_realtime_weather()
    except Exception:
        weather = {
            "temperature": 24,
            "status": "Heavy Rain Expected",
            "days": [
                {"day": "Fri", "icon": "☁️"},
                {"day": "Sat", "icon": "🌦️"},
                {"day": "Sun", "icon": "☀️"},
                {"day": "Mon", "icon": "🌧️"},
            ],
        }

    today_name = datetime.now().strftime("%a")
    day_html = ""

    for index, day in enumerate(weather.get("days", [])[:4]):
        day_name = day.get("day", "")
        is_today = index == 0 or day_name == today_name

        day_class = "fm-day fm-day-today" if is_today else "fm-day"

        day_html += (
            f'<div class="{day_class}">'
            f'{_safe(day_name)}'
            f'<span>{_safe(day.get("icon", "☁️"))}</span>'
            '</div>'
        )

    markup = (
        '<style>'
        '.fm-days {'
        'align-items: center !important;'
        '}'
        '.fm-day {'
        'position: relative !important;'
        'white-space: nowrap !important;'
        '}'
        '.fm-day-today {'
        'background: rgba(255, 255, 255, 0.16) !important;'
        'border: 1px solid rgba(255, 255, 255, 0.42) !important;'
        'border-radius: 13px !important;'
        'padding: 7px 9px !important;'
        'box-shadow: 0 10px 22px rgba(0, 49, 82, 0.07) !important;'
        '}'
        '.fm-day-today::before {'
        'content: "" !important;'
        'position: absolute !important;'
        'top: -6px !important;'
        'left: 50% !important;'
        'transform: translateX(-50%) !important;'
        'width: 7px !important;'
        'height: 7px !important;'
        'border-radius: 999px !important;'
        'background: #ffffff !important;'
        'box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.22), 0 5px 12px rgba(0, 49, 82, 0.12) !important;'
        '}'
        '</style>'
        '<div class="fm-weather-card">'
        '<div class="fm-weather-title">Local Weather Forecast</div>'
        '<div class="fm-weather-row">'
        '<div>'
        f'<div class="fm-temp">{_safe(weather.get("temperature", 24))}°C</div>'
        f'<div class="fm-weather-copy">{_safe(weather.get("status", "Heavy Rain Expected"))}</div>'
        '</div>'
        f'<div class="fm-days">{day_html}</div>'
        '</div>'
        '</div>'
    )

    _html(markup)


def render_flood_risk_predictor() -> None:
    _ensure_defaults()
    _render_header()

    left_col, right_col = st.columns([1.03, 1], gap="large")

    with left_col:
        _render_simulation_parameters()

    with right_col:
        result = st.session_state.prediction_result
        _render_prediction(result)
        _render_actions(result)
        _render_weather()
