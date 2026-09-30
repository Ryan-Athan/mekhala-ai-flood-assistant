from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from utils.weather_service import get_realtime_weather

RISK_PALETTE = {
    "Low Risk": {"strong": "#168A55", "soft": "#E8F7EF", "text": "#116C43"},
    "Medium Risk": {"strong": "#D69216", "soft": "#FFF4DA", "text": "#8A5A00"},
    "High Risk": {"strong": "#E76F28", "soft": "#FFF0E6", "text": "#A44713"},
    "Severe Risk": {"strong": "#C83C46", "soft": "#FDEBED", "text": "#9D2530"},
}

DEFAULT_INPUTS = {"rainfall": 2, "weather_worse": 1, "area_type": 2, "coast_distance": 3,
                  "river_control": 3, "dam_condition": 1, "drainage_quality": 2}
CONTROL_CONFIG = {
    "rainfall": {"label":"Rainfall Level","ticks":["Light","Medium","Heavy","Extreme"],"chips":["Light","Medium","High","Extreme"],"classes":["fm-chip-green","fm-chip-yellow","fm-chip-red","fm-chip-red"],"percents":[8,34,75,100],"risk_scores":[20,48,75,95]},
    "weather_worse": {"label":"Weather getting worse?","ticks":["Less<br>worse","Same","Worse","Not sure"],"chips":["Less","Same","Worse","Not Sure"],"classes":["fm-chip-green","fm-chip-yellow","fm-chip-red","fm-chip-white"],"percents":[8,34,68,100],"risk_scores":[25,50,78,58]},
    "area_type": {"label":"Area Type","ticks":["Low land","Slightly<br>elevated","Hilly","Not sure"],"chips":["Low land","Slightly","Hilly","Not Sure"],"classes":["fm-chip-red","fm-chip-yellow","fm-chip-green","fm-chip-white"],"percents":[8,34,67,100],"risk_scores":[85,60,42,58]},
    "coast_distance": {"label":"Distance to coast","ticks":["Inland","Near","Coastal","Not sure"],"chips":["Inland","Near","Coastal","Not Sure"],"classes":["fm-chip-green","fm-chip-yellow","fm-chip-red","fm-chip-white"],"percents":[8,34,68,100],"risk_scores":[28,52,76,58]},
    "river_control": {"label":"River control","ticks":["Poor","Average","Strong","Not Sure"],"chips":["Poor","Average","Strong","Not Sure"],"classes":["fm-chip-red","fm-chip-yellow","fm-chip-green","fm-chip-white"],"percents":[8,34,68,94],"risk_scores":[82,55,28,58]},
    "dam_condition": {"label":"Dam condition","ticks":["Poor","Average","Strong","Not sure"],"chips":["Poor","Average","Strong","Not Sure"],"classes":["fm-chip-red","fm-chip-yellow","fm-chip-green","fm-chip-white"],"percents":[8,34,68,100],"risk_scores":[82,55,30,58]},
    "drainage_quality": {"label":"Drainage quality","ticks":["Poor","Average","Strong","Not sure"],"chips":["Poor","Average","Strong","Not Sure"],"classes":["fm-chip-red","fm-chip-yellow","fm-chip-green","fm-chip-white"],"percents":[8,34,68,100],"risk_scores":[82,55,30,58]},
}
COMPONENT_DIR = Path(__file__).resolve().parents[1] / "components" / "fm_risk_controls"
_fm_risk_controls = components.declare_component("fm_risk_controls", path=str(COMPONENT_DIR))


def _safe(v: object) -> str: return escape(str(v))
def _html(v: str) -> None: st.markdown(v.strip(), unsafe_allow_html=True)

REGIONAL_PICKER_DIR = Path(__file__).resolve().parents[1] / "components" / "regional_location_picker"
_regional_location_picker = components.declare_component("regional_location_picker", path=str(REGIONAL_PICKER_DIR))


def _render_location_picker(current: dict | None, key: str) -> dict | None:
    """Professional map/search/voice picker. Returns only confirmed selections."""
    value = _regional_location_picker(
        current=current or {},
        key=key,
        default=None,
    )
    return value if isinstance(value, dict) else None


def _inject_css() -> None:
    _html("""
<style>
/* Flood Intelligence mode switch: always a compact horizontal segmented control. */
.st-key-fi_mode div[role="radiogroup"]{display:flex!important;flex-direction:row!important;align-items:center!important;gap:8px!important;flex-wrap:nowrap!important;width:max-content!important;}
.st-key-fi_mode label[data-baseweb="radio"]{width:auto!important;min-width:170px!important;min-height:44px!important;margin:0!important;padding:8px 18px!important;border-radius:12px!important;background:rgba(255,255,255,.20)!important;border:1px solid rgba(255,255,255,.38)!important;}
.st-key-fi_mode label[data-baseweb="radio"]:has(input:checked){background:rgba(255,255,255,.82)!important;border-color:rgba(255,255,255,.92)!important;box-shadow:0 8px 20px rgba(0,49,82,.08)!important;}
@media(max-width:700px){.st-key-fi_mode div[role="radiogroup"]{width:100%!important}.st-key-fi_mode label[data-baseweb="radio"]{min-width:0!important;flex:1 1 0!important;justify-content:center!important;padding:8px 10px!important;}}
.fi-header{margin:0 0 12px}.fi-title{font-size:30px;font-weight:900;letter-spacing:-.65px;color:#003152;margin:0;line-height:1.08}.fi-sub{font-size:13px;color:rgba(0,49,82,.70);margin-top:4px}
.fi-tabs div[role="radiogroup"]{flex-direction:row!important;gap:6px!important;background:rgba(255,255,255,.22)!important;padding:5px!important;border-radius:12px!important;width:max-content!important}
.fi-tabs label{min-height:38px!important;padding:7px 18px!important;border-radius:9px!important;font-weight:800!important}.fi-tabs label:has(input:checked){background:white!important;box-shadow:0 2px 10px rgba(8,47,73,.08)!important}
.fi-card{background:rgba(255,255,255,.28);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.45);border-radius:16px;padding:20px;box-shadow:0 8px 28px rgba(8,47,73,.055);margin-bottom:16px}.fi-card-title{font-size:17px;font-weight:850;color:#003152;margin-bottom:5px}.fi-muted{font-size:12px;color:rgba(0,49,82,.68)}.fi-risk{padding:24px;border-radius:16px;border:1px solid rgba(255,255,255,.45);background:rgba(255,255,255,.30);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);box-shadow:0 8px 28px rgba(8,47,73,.055)}
.fi-risk-top{display:flex;align-items:flex-start;justify-content:space-between;gap:14px}.fi-risk-label{font-size:12px;font-weight:800;color:rgba(0,49,82,.68);text-transform:uppercase;letter-spacing:.7px}.fi-risk-value{font-size:30px;font-weight:950;margin-top:5px}.fi-prob{font-size:42px;font-weight:950;letter-spacing:-1.5px}.fi-pill{display:inline-flex;padding:7px 11px;border-radius:999px;font-size:12px;font-weight:850}.fi-bar{height:9px;border-radius:999px;background:rgba(255,255,255,.36);overflow:hidden;margin:18px 0 12px}.fi-bar>span{display:block;height:100%;border-radius:999px}.fi-explain{font-size:13px;line-height:1.55;color:rgba(0,49,82,.78)}
.fi-kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:12px 0 18px}.fi-kpi{background:rgba(255,255,255,.25);border:1px solid rgba(255,255,255,.36);border-radius:12px;padding:13px}.fi-kpi-l{font-size:11px;color:rgba(0,49,82,.62);font-weight:750}.fi-kpi-v{font-size:18px;color:#003152;font-weight:900;margin-top:4px}
.fi-factor{display:grid;grid-template-columns:125px 1fr 62px;gap:10px;align-items:center;margin:11px 0;font-size:12px;font-weight:750}.fi-factor-track{height:7px;background:rgba(255,255,255,.36);border-radius:999px;overflow:hidden}.fi-factor-track span{display:block;height:100%;background:#34b9df;border-radius:999px}
.fi-map-hint{text-align:center;padding:8px 0 2px;color:rgba(0,49,82,.68);font-size:12px}.fi-location{display:flex;justify-content:space-between;align-items:flex-start;gap:16px}.fi-location-name{font-size:20px;font-weight:900;color:#003152}.fi-location-coords{font-size:11px;color:rgba(0,49,82,.62);margin-top:5px}
.fi-scroll{display:flex;gap:10px;overflow-x:auto;padding:2px 2px 10px;scroll-snap-type:x proximity}.fi-day{min-width:132px;scroll-snap-align:start;background:rgba(255,255,255,.28);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.45);border-radius:14px;padding:14px;box-shadow:0 5px 16px rgba(8,47,73,.04)}.fi-day-date{font-size:11px;color:rgba(0,49,82,.62);font-weight:750}.fi-day-icon{font-size:25px;margin:9px 0}.fi-day-mm{font-size:18px;font-weight:900;color:#003152}.fi-day-risk{margin-top:10px;font-size:11px;font-weight:850}.fi-section{font-size:16px;font-weight:900;color:#003152;margin:24px 0 10px}.fi-empty{padding:34px 22px;text-align:center;background:rgba(255,255,255,.25);border:1px dashed rgba(255,255,255,.58);border-radius:16px}.fi-empty-title{font-size:18px;font-weight:900;color:#003152}.fi-empty-copy{font-size:13px;color:rgba(0,49,82,.68);margin-top:7px;line-height:1.5}
.fi-ops{margin-top:16px;background:rgba(255,255,255,.22);border:1px solid rgba(255,255,255,.40);border-radius:14px;padding:16px 18px;box-shadow:0 6px 20px rgba(8,47,73,.035)}.fi-ops-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:12px}.fi-ops-title{font-size:13px;font-weight:900;color:#003152}.fi-ops-badge{font-size:10px;font-weight:850;letter-spacing:.35px;text-transform:uppercase;padding:5px 8px;border-radius:999px;background:rgba(255,255,255,.50);color:rgba(0,49,82,.70)}.fi-ops-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.fi-ops-item{padding:11px 12px;border-radius:10px;background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.30)}.fi-ops-label{font-size:9px;font-weight:850;letter-spacing:.5px;text-transform:uppercase;color:rgba(0,49,82,.50)}.fi-ops-value{font-size:12px;font-weight:900;color:#003152;margin-top:4px}.fi-ops-note{margin-top:11px;font-size:10.5px;line-height:1.45;color:rgba(0,49,82,.62)}
.fi-local-after{margin-top:18px}.fi-context-panel{background:rgba(255,255,255,.24);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.42);border-radius:14px;padding:0 18px 14px;box-shadow:0 7px 22px rgba(8,47,73,.045);overflow:hidden}.fi-context-weather{display:grid;grid-template-columns:1.35fr repeat(3,minmax(0,1fr));align-items:center;min-height:82px}.fi-context-head{padding-right:18px}.fi-context-eyebrow{font-size:10px;font-weight:850;letter-spacing:.65px;text-transform:uppercase;color:rgba(0,49,82,.55)}.fi-context-status{font-size:12px;color:rgba(0,49,82,.70);margin-top:5px}.fi-context-metric{padding:3px 18px;border-left:1px solid rgba(255,255,255,.45)}.fi-context-value{font-size:19px;font-weight:950;color:#003152;line-height:1.1}.fi-context-label{font-size:10px;font-weight:750;color:rgba(0,49,82,.58);margin-top:4px}.fi-context-divider{height:1px;background:rgba(255,255,255,.42);margin:0 0 12px}.fi-ai-inline{display:flex;align-items:center;min-height:48px;padding:0}.fi-ai-kicker{font-size:12px;font-weight:900;color:#003152}.fi-ai-copy{font-size:11px;color:rgba(0,49,82,.64);margin-top:2px}.st-key-ask_local{margin-top:10px!important}.st-key-ask_local button{min-height:42px!important;border-radius:10px!important;background:rgba(255,255,255,.76)!important;color:#003152!important;border:1px solid rgba(255,255,255,.78)!important;font-weight:800!important;box-shadow:0 4px 12px rgba(0,49,82,.04)!important}.st-key-ask_local button:hover{background:#fff!important;transform:translateY(-1px)}.fi-local-label{display:none}
.fi-actions{background:rgba(255,255,255,.28);border:1px solid rgba(255,255,255,.45);border-radius:16px;padding:8px 12px 8px 18px;box-shadow:0 8px 28px rgba(8,47,73,.045);max-height:360px;overflow-y:auto;overscroll-behavior:contain;scrollbar-width:thin;scrollbar-color:rgba(0,49,82,.28) transparent}.fi-actions::-webkit-scrollbar{width:6px}.fi-actions::-webkit-scrollbar-track{background:transparent}.fi-actions::-webkit-scrollbar-thumb{background:rgba(0,49,82,.24);border-radius:999px}.fi-actions::-webkit-scrollbar-thumb:hover{background:rgba(0,49,82,.38)}.fi-action{display:grid;grid-template-columns:32px 1fr auto;gap:12px;align-items:start;padding:14px 0;border-bottom:1px solid rgba(255,255,255,.38)}.fi-action:last-child{border-bottom:0}.fi-action-num{width:28px;height:28px;border-radius:8px;background:rgba(255,255,255,.42);display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:900;color:rgba(0,49,82,.62)}.fi-action-title{font-size:13px;font-weight:900;color:#003152}.fi-action-copy{font-size:11px;line-height:1.45;color:rgba(0,49,82,.66);margin-top:3px}.fi-action-priority{font-size:9px;font-weight:900;letter-spacing:.45px;padding:5px 8px;border-radius:999px;text-transform:uppercase;white-space:nowrap}.fi-priority-high{background:#FDEBED;color:#9D2530}.fi-priority-medium{background:#FFF4DA;color:#8A5A00}.fi-priority-routine{background:#E8F7EF;color:#116C43}.fi-actions-note{font-size:10px;color:rgba(0,49,82,.55);padding:10px 0 4px;line-height:1.45}@media(max-width:760px){.fi-title{font-size:25px}.fi-kpis{grid-template-columns:1fr}.fi-risk-top{flex-direction:column}.fi-factor{grid-template-columns:105px 1fr 52px}.fi-card{padding:16px}.fi-day{min-width:122px}.fi-context-weather{grid-template-columns:1fr 1fr;gap:10px;padding:12px 0}.fi-context-head{grid-column:1/-1;padding-right:0}.fi-context-metric{border-left:0;padding:7px 0}.fi-ai-inline{min-height:auto;padding:4px 0}.fi-ops-grid{grid-template-columns:1fr}}
</style>""")


def _ensure_state() -> None:
    st.session_state.setdefault("frp_inputs", DEFAULT_INPUTS.copy())
    st.session_state.setdefault("frp_component_version", 0)
    st.session_state.setdefault("frp_last_component_event", None)
    st.session_state.setdefault("prediction_result", None)
    st.session_state.setdefault("regional_location", None)
    st.session_state.setdefault("regional_weather", None)
    st.session_state.setdefault("regional_confirmed", False)
    st.session_state.setdefault("regional_map_nonce", 0)


def _sanitize(raw: Any) -> dict:
    out = DEFAULT_INPUTS.copy()
    if isinstance(raw, dict):
        for k, default in out.items():
            try: out[k] = max(0, min(3, int(raw.get(k, default))))
            except (TypeError, ValueError): pass
    return out


def _calculate() -> None:
    try:
        from utils.flood_risk_model_service import predict_flood_risk_from_ui
        st.session_state.prediction_result = predict_flood_risk_from_ui(st.session_state.frp_inputs)
    except Exception:
        weights = {"rainfall":.24,"weather_worse":.12,"area_type":.14,"coast_distance":.10,"river_control":.14,"dam_condition":.13,"drainage_quality":.13}
        score = sum(CONTROL_CONFIG[k]["risk_scores"][st.session_state.frp_inputs[k]] * w for k,w in weights.items())
        p = int(round(score))
        label = "Low Risk" if p < 40 else "Medium Risk" if p < 70 else "High Risk"
        st.session_state.prediction_result = {"probability":p,"risk_label":label,"confidence":88,"predicted_peak":"Monitor conditions","explanation":f"Estimated flood risk is {p}% based on the selected local conditions.","actions":[]}


def _factor_rows() -> str:
    names = {"rainfall":"Rainfall","weather_worse":"Weather trend","area_type":"Terrain","coast_distance":"Coast exposure","river_control":"River control","dam_condition":"Dam condition","drainage_quality":"Drainage"}
    rows=[]
    for key,name in names.items():
        score=CONTROL_CONFIG[key]["risk_scores"][st.session_state.frp_inputs[key]]
        level="High" if score>=70 else "Moderate" if score>=45 else "Low"
        rows.append(f'<div class="fi-factor"><span>{name}</span><div class="fi-factor-track"><span style="width:{score}%"></span></div><span>{level}</span></div>')
    return "".join(rows)


def _recommended_actions(result: dict) -> list[dict]:
    """Build contextual decision-support actions from the prediction and selected factors."""
    p = max(0, min(100, int(result.get("probability", 0))))
    scores = {k: CONTROL_CONFIG[k]["risk_scores"][st.session_state.frp_inputs[k]] for k in CONTROL_CONFIG}
    actions: list[dict] = []

    def add(title: str, text: str, priority: str) -> None:
        if title not in {a["title"] for a in actions}:
            actions.append({"title": title, "text": text, "priority": priority})

    if scores["drainage_quality"] >= 70:
        add("Inspect drainage and low-lying areas", "Poor drainage is a major contributor in this assessment. Check known collection points and clear safe-to-remove blockages.", "High")
    if scores["river_control"] >= 70:
        add("Increase river and water-level monitoring", "River-control conditions are increasing risk. Shorten monitoring intervals and watch for rapid rises.", "High")
    if scores["dam_condition"] >= 70:
        add("Verify dam and flood-control conditions", "Dam condition is contributing to the assessment. Confirm current operating status and escalation contacts.", "High")
    if scores["rainfall"] >= 70 or scores["weather_worse"] >= 70:
        add("Track rainfall and weather escalation", "Heavy or worsening weather is driving risk. Review updates frequently and reassess if rainfall intensifies.", "High" if p >= 70 else "Medium")
    if scores["area_type"] >= 70 or scores["coast_distance"] >= 70:
        add("Prioritize exposed locations", "Low-lying or exposed areas have elevated vulnerability. Check access routes and vulnerable buildings first.", "Medium")

    if p >= 70:
        add("Prepare flood barriers and critical equipment", "Stage barriers, pumps or other available protection near vulnerable entrances and essential assets.", "High")
        add("Prepare public warning and evacuation readiness", "Confirm warning channels, response contacts and usable routes before conditions deteriorate.", "High")
        add("Stand by response teams", "Keep response personnel and essential equipment ready for rapid deployment if observed conditions worsen.", "Medium")
    elif p >= 40:
        add("Prepare protective resources", "Check barriers, pumps and response equipment so they can be deployed quickly if the risk increases.", "Medium")
        add("Review warning and response contacts", "Confirm who should be notified and which routes or facilities need attention if conditions worsen.", "Medium")
    else:
        add("Continue routine monitoring", "Current modeled risk is lower. Continue observing rainfall, water levels and local advisories for meaningful changes.", "Routine")
        add("Keep drainage paths clear", "Maintain normal drainage checks so local accumulation does not increase avoidable flood exposure.", "Routine")

    # Preserve useful model-provided actions when they add something not already represented.
    for item in result.get("actions", []) or []:
        title = str(item.get("title", "")).strip()
        text = str(item.get("text", "")).strip()
        if title and text and len(actions) < 6:
            add(title, text, "Medium" if p >= 40 else "Routine")

    return actions[:6]


def _render_local() -> None:
    left, right = st.columns([1.02, 1], gap="large")
    with left:
        value = _fm_risk_controls(
            controls=CONTROL_CONFIG,
            values=st.session_state.frp_inputs,
            default=DEFAULT_INPUTS,
            key=f"fm_risk_controls_{st.session_state.frp_component_version}",
        )
        if isinstance(value, dict):
            action = value.get("action")
            event = value.get("event_id")
            raw = value.get("values", value)
            st.session_state.frp_inputs = _sanitize(raw)
            if event and event != st.session_state.frp_last_component_event:
                st.session_state.frp_last_component_event = event
                if action == "reset":
                    st.session_state.frp_inputs = DEFAULT_INPUTS.copy()
                    st.session_state.prediction_result = None
                    st.session_state.frp_component_version += 1
                    st.rerun()
                if action in {"calculate", "predict"}:
                    _calculate()
                    st.rerun()

    result = st.session_state.prediction_result
    with right:
        if not result:
            _html(
                '<div class="fi-empty"><div class="fi-empty-title">Ready to predict local flood risk</div>'
                '<div class="fi-empty-copy">Set the local conditions, then select <b>Predict Flood Risk</b>. '
                'The prediction, risk factors and recommended actions will appear here.</div></div>'
            )
        else:
            label = result.get("risk_label", "Medium Risk")
            p = max(0, min(100, int(result.get("probability", 0))))
            pal = RISK_PALETTE.get(label, RISK_PALETTE["Medium Risk"])
            _html(
                f'<div class="fi-risk"><div class="fi-risk-top"><div>'
                f'<div class="fi-risk-label">Flood risk prediction</div>'
                f'<div class="fi-risk-value" style="color:{pal["strong"]}">{_safe(label)}</div>'
                f'<span class="fi-pill" style="background:{pal["soft"]};color:{pal["text"]}">● {_safe(label.replace(" Risk", ""))}</span>'
                f'</div><div class="fi-prob" style="color:{pal["strong"]}">{p}%</div></div>'
                f'<div class="fi-bar"><span style="width:{p}%;background:{pal["strong"]}"></span></div>'
                f'<div class="fi-explain">{_safe(result.get("explanation", ""))}</div></div>'
            )
            _html('<div class="fi-section">Risk factors</div><div class="fi-card">' + _factor_rows() + '</div>')
            actions = _recommended_actions(result)
            if actions:
                rows = []
                for i, a in enumerate(actions, 1):
                    priority = a.get("priority", "Medium")
                    priority_class = "fi-priority-high" if priority == "High" else "fi-priority-routine" if priority == "Routine" else "fi-priority-medium"
                    rows.append(
                        f'<div class="fi-action"><div class="fi-action-num">{i:02d}</div><div>'
                        f'<div class="fi-action-title">{_safe(a.get("title", "Action"))}</div>'
                        f'<div class="fi-action-copy">{_safe(a.get("text", ""))}</div></div>'
                        f'<span class="fi-action-priority {priority_class}">{_safe(priority)}</span></div>'
                    )
                _html('<div class="fi-section">Recommended actions</div><div class="fi-actions">' + ''.join(rows) +
                      '<div class="fi-actions-note">Actions are prioritized from the current prediction and selected risk factors. Reassess when local conditions change.</div></div>')



    # Compact context panel shown only after a prediction. It deliberately has less
    # visual weight than the main prediction card.
    if result:
        weather = get_realtime_weather()
        if weather.get("ok"):
            _html(
                f'<div class="fi-local-after"><div class="fi-context-panel">'
                f'<div class="fi-context-weather"><div class="fi-context-head">'
                f'<div class="fi-context-eyebrow">Live local context</div>'
                f'<div class="fi-context-status">{_safe(weather["status"])}</div></div>'
                f'<div class="fi-context-metric"><div class="fi-context-value">{weather["temperature"]}°C</div><div class="fi-context-label">Temperature</div></div>'
                f'<div class="fi-context-metric"><div class="fi-context-value">{weather["humidity"]}%</div><div class="fi-context-label">Humidity</div></div>'
                f'<div class="fi-context-metric"><div class="fi-context-value">{weather["wind_speed"]} km/h</div><div class="fi-context-label">Wind</div></div>'
                f'</div><div class="fi-context-divider"></div>'
                f'<div class="fi-ai-inline"><div><div class="fi-ai-kicker">Need help understanding this prediction?</div><div class="fi-ai-copy">Ask Mekhala for a concise explanation and recommended next actions.</div></div></div>'
                f'</div></div>'
            )
        else:
            _html('<div class="fi-local-after"><div class="fi-context-panel"><div class="fi-ai-inline"><div><div class="fi-ai-kicker">Need help understanding this prediction?</div><div class="fi-ai-copy">Ask Mekhala for a concise explanation and recommended next actions.</div></div></div></div></div>')

        ai_spacer, ai_button = st.columns([4.7, 1.3], gap="small", vertical_alignment="center")
        with ai_button:
            if st.button("Ask Mekhala →", use_container_width=True, key="ask_local"):
                label = result.get("risk_label", "Medium Risk")
                p = max(0, min(100, int(result.get("probability", 0))))
                st.session_state.assistant_context = (
                    f"Local flood assessment: {label}, probability {p}%. {result.get('explanation', '')}"
                )
                st.session_state.active_page = "AI Flood Assistant"
                st.query_params["page"] = "AI Flood Assistant"
                st.rerun()


def _forecast_risk(day: dict, rolling_mm: float) -> tuple[int,str]:
    mm=float(day.get("rain_mm",0)); prob=float(day.get("rain_probability",0))
    score=min(96, round(12 + min(mm,80)*0.72 + prob*0.22 + min(rolling_mm,120)*0.16))
    label="Low" if score<35 else "Moderate" if score<60 else "High" if score<80 else "Severe"
    return score,label


def _render_regional() -> None:
    # RESULT STATE: once confirmed, hide the large map and show the forecast.
    if st.session_state.regional_confirmed and st.session_state.regional_location:
        loc = st.session_state.regional_location
        place = loc.get("short_name") or loc.get("city") or loc.get("town") or loc.get("region") or "Selected area"
        region = loc.get("region") or loc.get("state") or ""
        country = loc.get("country") or "Myanmar"
        detail = " · ".join(x for x in [region, country] if x and x != place)
        left, right = st.columns([5, 1.25], vertical_alignment="center")
        with left:
            _html(
                f'<div class="fi-regional-toolbar"><div class="fi-regional-place">'
                f'<div class="fi-regional-name">📍 {_safe(place)}</div>'
                f'<div class="fi-regional-detail">{_safe(detail or loc.get("name", ""))}</div>'
                f'</div></div>'
            )
        with right:
            if st.button("Change location", use_container_width=True, key="change_regional_location"):
                st.session_state.regional_confirmed = False
                st.session_state.regional_weather = None
                st.session_state.regional_map_nonce += 1
                st.rerun()

        if st.session_state.regional_weather is None:
            with st.spinner("Loading regional forecast..."):
                st.session_state.regional_weather = get_realtime_weather(
                    loc["latitude"], loc["longitude"], loc["name"], 14
                )

        weather = st.session_state.regional_weather
        if not weather or not weather.get("ok"):
            st.error("Forecast service is temporarily unavailable. Please try again.")
            return

        horizon = st.radio(
            "Forecast horizon", ["7 Days", "14 Days"], horizontal=True,
            key="forecast_horizon", label_visibility="collapsed"
        )
        days = weather["days"][: 7 if horizon == "7 Days" else 14]
        rolling = 0.0
        enriched = []
        for d in days:
            rolling += float(d.get("rain_mm", 0))
            score, label = _forecast_risk(d, rolling)
            enriched.append((d, score, label))

        peak = max(enriched, key=lambda x: x[1]) if enriched else ({}, 0, "Low")
        avg = round(sum(x[1] for x in enriched) / len(enriched)) if enriched else 0
        avg_label = "Low Risk" if avg < 35 else "Medium Risk" if avg < 60 else "High Risk" if avg < 80 else "Severe Risk"
        pal = RISK_PALETTE[avg_label]
        total = sum(float(x[0].get("rain_mm", 0)) for x in enriched)

        _html(
            f'<div class="fi-section">Regional outlook</div><div class="fi-risk">'
            f'<div class="fi-risk-top"><div><div class="fi-risk-label">{horizon} flood outlook</div>'
            f'<div class="fi-risk-value" style="color:{pal["strong"]}">{avg_label}</div></div>'
            f'<div class="fi-prob" style="color:{pal["strong"]}">{avg}%</div></div>'
            f'<div class="fi-kpis"><div class="fi-kpi"><div class="fi-kpi-l">Forecast rainfall</div><div class="fi-kpi-v">{total:.1f} mm</div></div>'
            f'<div class="fi-kpi"><div class="fi-kpi-l">Highest-risk day</div><div class="fi-kpi-v">{_safe(peak[0].get("day","—"))}</div></div>'
            f'<div class="fi-kpi"><div class="fi-kpi-l">Peak risk</div><div class="fi-kpi-v">{peak[1]}%</div></div></div>'
            '<div class="fi-explain">This weather-based outlook uses forecast rainfall and precipitation probability. Local river, drainage and ground conditions can change actual flood risk.</div></div>'
        )

        cards = []
        for d, score, label in enriched:
            color = "#168A55" if label == "Low" else "#D69216" if label == "Moderate" else "#E76F28" if label == "High" else "#C83C46"
            cards.append(
                f'<div class="fi-day"><div class="fi-day-date">{_safe(d.get("date",""))}</div>'
                f'<div class="fi-day-icon">{_safe(d.get("icon","☁️"))}</div>'
                f'<div class="fi-day-mm">{d.get("rain_mm",0)} mm</div>'
                f'<div class="fi-muted">Rain chance {d.get("rain_probability",0)}%</div>'
                f'<div class="fi-day-risk" style="color:{color}">● {label} · {score}%</div></div>'
            )
        _html('<div class="fi-section">Daily forecast</div><div class="fi-scroll">' + ''.join(cards) + '</div>')

        chart = pd.DataFrame({
            "Date": [x[0]["date"] for x in enriched],
            "Flood risk": [x[1] for x in enriched],
            "Rainfall (mm)": [x[0]["rain_mm"] for x in enriched],
        }).set_index("Date")
        _html('<div class="fi-section">Flood risk trend</div>')
        st.line_chart(chart[["Flood risk"]], height=220, use_container_width=True)
        _html('<div class="fi-section">Rainfall forecast</div>')
        st.bar_chart(chart[["Rainfall (mm)"]], height=220, use_container_width=True)

        if st.button("Ask Mekhala about this forecast", use_container_width=True, key="ask_regional"):
            st.session_state.assistant_context = (
                f"Regional forecast for {loc['name']}: {avg_label}, outlook score {avg}%, "
                f"forecast rainfall {total:.1f} mm, highest-risk day {peak[0].get('date','')} at {peak[1]}%."
            )
            st.session_state.active_page = "AI Flood Assistant"
            st.query_params["page"] = "AI Flood Assistant"
            st.rerun()
        return

    # SELECTION STATE — search, voice and map click are handled inside one
    # lightweight component so there are no slow Streamlit reruns while exploring.
    selection = _render_location_picker(
        st.session_state.regional_location,
        key=f"regional_location_picker_{st.session_state.regional_map_nonce}",
    )
    if selection and selection.get("action") == "confirm":
        loc = {
            "name": selection.get("name") or selection.get("short_name") or "Selected area",
            "short_name": selection.get("short_name") or selection.get("name") or "Selected area",
            "city": selection.get("city") or "",
            "region": selection.get("region") or "",
            "state": selection.get("region") or "",
            "country": selection.get("country") or "Myanmar",
            "latitude": float(selection["latitude"]),
            "longitude": float(selection["longitude"]),
        }
        st.session_state.regional_location = loc
        st.session_state.regional_weather = None
        st.session_state.regional_confirmed = True
        st.rerun()


def render_flood_risk_predictor() -> None:
    _ensure_state(); _inject_css()
    _html('<div class="fi-header"><h1 class="fi-title">Flood Intelligence</h1><div class="fi-sub">Understand local conditions and upcoming regional flood risk.</div></div>')
    st.markdown('<div class="fi-tabs">',unsafe_allow_html=True)
    mode=st.radio("View",["Local Prediction","Regional Forecast"],horizontal=True,label_visibility="collapsed",key="fi_mode")
    st.markdown('</div>',unsafe_allow_html=True)
    _render_local() if mode=="Local Prediction" else _render_regional()
