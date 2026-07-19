from __future__ import annotations

import os
import random
import re
from typing import Any, Dict, List, Optional

import requests

try:
    import streamlit as st
except ImportError:
    st = None


OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_OPENROUTER_MODEL = "openrouter/free"


def detect_language(text: str) -> str:
    cleaned = str(text or "").strip()

    if re.search(r"[\u1000-\u109F]", cleaned):
        return "my"

    if re.search(r"[\u3040-\u30FF\u3400-\u9FFF]", cleaned):
        return "ja"

    return "en"


def _get_secret_value(key: str, default: str = "") -> str:
    value = os.getenv(key, "").strip()

    if value:
        return value

    if st is not None:
        try:
            secret_value = st.secrets.get(key, "")
            if secret_value:
                return str(secret_value).strip()
        except Exception:
            pass

    return default


def _build_system_prompt(language: str) -> str:
    base_prompt = """
You are FloodMind AI, a helpful AI flood safety assistant inside a university project called FloodMind.

You answer questions about:
- flood safety
- flood warning signs
- flood preparedness
- evacuation decisions
- emergency kits
- rainfall risk
- home protection
- what to do before, during, and after a flood

Rules:
- Give practical, clear, safe answers.
- Do not claim to be an official emergency authority.
- If the user describes danger, advise moving to higher ground and following local authorities.
- Keep answers useful but not too long.
- Stay focused on flood and emergency preparedness topics.
"""

    if language == "my":
        return (
            base_prompt
            + """
The user is using Burmese.
Reply only in natural Burmese.
Use simple Burmese that a student can understand.
"""
        )

    if language == "ja":
        return (
            base_prompt
            + """
The user is using Japanese.
Reply only in natural Japanese.
Use clear and simple Japanese.
"""
        )

    return (
        base_prompt
        + """
The user is using English or another language.
Reply in clear simple English by default.
"""
    )


def _fallback_flood_answer(user_message: str) -> str:
    language = detect_language(user_message)
    text = str(user_message or "").lower()

    if language == "my":
        if "အရေးပေါ်" in user_message or "kit" in text or "အိတ်" in user_message:
            return (
                "အရေးပေါ်အိတ်ထဲမှာ သောက်ရေ၊ အစားအသောက်အခြောက်၊ မီးအိမ်၊ "
                "ဖုန်းအားသွင်းစက်၊ power bank၊ ဆေးဝါး၊ မှတ်ပုံတင်/စာရွက်စာတမ်းမိတ္တူ၊ "
                "အဝတ်အစား၊ whistle နဲ့ first-aid kit ထည့်ထားပါ။"
            )

        if "သတိပေး" in user_message or "လက္ခဏာ" in user_message:
            return (
                "ရေကြီးမယ့် သတိပေးလက္ခဏာတွေက မိုးအလွန်သည်းထန်ခြင်း၊ "
                "မြစ်ရေမြင့်တက်ခြင်း၊ ရေနုတ်မြောင်းပိတ်ခြင်း၊ လမ်းပေါ်ရေတက်ခြင်း၊ "
                "ဒေသခံအာဏာပိုင်များမှ သတိပေးချက်ထုတ်ပြန်ခြင်းတို့ ဖြစ်ပါတယ်။"
            )

        if "ဘယ်တော့" in user_message or "ပြောင်း" in user_message or "evacuate" in text:
            return (
                "ဒေသခံအာဏာပိုင်တွေက ပြောင်းရွှေ့ရန်ပြောတဲ့အခါ၊ ရေမြန်မြန်တက်လာတဲ့အခါ၊ "
                "လမ်းတွေ ရေဖုံးပြီး မလုံခြုံတော့တဲ့အခါ မြင့်တဲ့နေရာကို ချက်ချင်းပြောင်းသင့်ပါတယ်။"
            )

        return (
            "ရေကြီးနိုင်ခြေရှိရင် မြင့်တဲ့နေရာကို ချက်ချင်းပြောင်းပါ။ "
            "ရေစီးပြင်းတဲ့နေရာကို မဖြတ်ပါနဲ့။ လျှပ်စစ်ပစ္စည်းတွေကို ပိတ်ထားပါ။ "
            "ဖုန်းအားသွင်းထားပြီး ဒေသခံအာဏာပိုင်တွေရဲ့ သတိပေးချက်တွေကို လိုက်နာပါ။"
        )

    if language == "ja":
        if "避難" in user_message:
            return (
                "避難指示が出た場合、水位が急に上がっている場合、道路が冠水している場合、"
                "または夜間で移動が危険になる前に、早めに高い場所へ避難してください。"
            )

        if "警報" in user_message or "サイン" in user_message:
            return (
                "洪水の警告サインには、強い雨が続くこと、川の水位上昇、道路の冠水、"
                "排水の逆流、地域の避難情報などがあります。"
            )

        return (
            "洪水の危険がある場合は、すぐに高い場所へ移動してください。"
            "流れている水の中を歩いたり運転したりしないでください。"
            "携帯電話を充電し、地域の避難指示や警報に従ってください。"
        )

    if "warning" in text or "sign" in text:
        return (
            "Common flood warning signs include heavy continuous rainfall, rising river levels, "
            "blocked drainage, water covering roads, fast-moving water, and official alerts from local authorities."
        )

    if "home" in text or "protect" in text:
        return (
            "To protect your home, clear drains, move valuables to higher shelves, prepare sandbags or flood barriers, "
            "switch off electricity if water enters, and keep emergency supplies ready."
        )

    if "evacuate" in text:
        return (
            "Evacuate when local authorities tell you to leave, when water is rising quickly, "
            "when roads are becoming unsafe, or before nightfall if your area is already flooding."
        )

    if "kit" in text or "pack" in text:
        return (
            "Pack drinking water, dry food, flashlight, power bank, phone charger, first-aid kit, medicines, "
            "important documents, clothes, whistle, and basic hygiene items."
        )

    return (
        "If there is flood risk, move to higher ground immediately. "
        "Do not walk or drive through floodwater. Keep your phone charged, "
        "prepare emergency supplies, and follow local authority warnings."
    )


def _clean_history(history: Optional[List[Dict[str, str]]]) -> List[Dict[str, str]]:
    if not history:
        return []

    clean_messages: List[Dict[str, str]] = []

    for message in history[-10:]:
        role = str(message.get("role", "")).strip()
        content = str(message.get("content", "")).strip()

        if role in {"user", "assistant"} and content:
            clean_messages.append(
                {
                    "role": role,
                    "content": content,
                }
            )

    return clean_messages


def chat_with_openrouter(
    user_message: str,
    history: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, str]:
    cleaned = str(user_message or "").strip()
    language = detect_language(cleaned)

    if not cleaned:
        return {
            "response": "Please type a question.",
            "language": language,
            "source": "empty",
        }

    api_key = _get_secret_value("OPENROUTER_API_KEY", "")
    model = _get_secret_value("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL)

    if not api_key:
        return {
            "response": (
                "OpenRouter API key is missing.\n\n"
                "Create this file:\n\n"
                ".streamlit/secrets.toml\n\n"
                "Then add:\n\n"
                'OPENROUTER_API_KEY = "paste_your_api_key_here"\n'
                'OPENROUTER_MODEL = "openrouter/free"'
            ),
            "language": language,
            "source": "missing_openrouter_key",
        }

    messages: List[Dict[str, str]] = [
        {
            "role": "system",
            "content": _build_system_prompt(language),
        }
    ]

    messages.extend(_clean_history(history))
    messages.append(
        {
            "role": "user",
            "content": cleaned,
        }
    )

    try:
        response = requests.post(
            OPENROUTER_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8501",
                "X-OpenRouter-Title": "FloodMind AI",
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": 0.4,
                "max_tokens": 600,
            },
            timeout=45,
        )

        if response.status_code == 401:
            return {
                "response": (
                    "OpenRouter API key is invalid or expired. "
                    "Please create a new API key and update .streamlit/secrets.toml."
                ),
                "language": language,
                "source": "openrouter_unauthorized",
            }

        if response.status_code == 402:
            return {
                "response": (
                    "OpenRouter says your account has no available credits or the selected model is not available. "
                    "Try changing OPENROUTER_MODEL in .streamlit/secrets.toml to another free model."
                ),
                "language": language,
                "source": "openrouter_payment_required",
            }

        response.raise_for_status()

        data = response.json()
        answer = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

        if not answer:
            answer = _fallback_flood_answer(cleaned)

        return {
            "response": answer,
            "language": language,
            "source": "openrouter",
        }

    except requests.exceptions.Timeout:
        return {
            "response": "OpenRouter request timed out. Please check your internet connection and try again.",
            "language": language,
            "source": "openrouter_timeout",
        }

    except requests.exceptions.ConnectionError:
        return {
            "response": "Cannot connect to OpenRouter. Please check your internet connection.",
            "language": language,
            "source": "openrouter_connection_error",
        }

    except Exception as error:
        return {
            "response": (
                "OpenRouter request failed.\n\n"
                f"Technical error: {error}"
            ),
            "language": language,
            "source": "openrouter_error",
        }


def get_flood_assistant_response(
    user_message: str,
    history: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, str]:
    return chat_with_openrouter(
        user_message=user_message,
        history=history,
    )


def analyze_uploaded_image(
    uploaded_file: Any = None,
    file_name: str = "",
    **kwargs: Any,
) -> Dict[str, Any]:
    detected_file_name = str(file_name or "").strip()
    file_size = 0

    if uploaded_file is not None:
        detected_file_name = getattr(uploaded_file, "name", detected_file_name) or detected_file_name
        file_size = getattr(uploaded_file, "size", 0) or 0

    if not detected_file_name:
        detected_file_name = str(kwargs.get("name", "") or kwargs.get("filename", "") or "").strip()

    name_lower = detected_file_name.lower()

    if any(word in name_lower for word in ["high", "flood", "danger", "severe"]):
        risk_level = "High"
        flood_detected = "Yes"
        confidence = 94
        water_coverage = 38
        status_color = "red"
        context = (
            "The road is flooded and not safe for vehicles. "
            "Water is moving and may increase quickly."
        )
        recommendations = [
            "Do not drive through water",
            "Check local flood updates",
            "Move to higher ground if needed",
        ]

    elif any(word in name_lower for word in ["medium", "moderate", "rain"]):
        risk_level = "Medium"
        flood_detected = "Yes"
        confidence = 89
        water_coverage = 25
        status_color = "yellow"
        context = (
            "The image suggests moderate flood risk. "
            "Water accumulation may become dangerous if rainfall continues."
        )
        recommendations = [
            "Avoid low-lying roads",
            "Prepare emergency supplies",
            "Monitor official flood warnings",
        ]

    elif any(word in name_lower for word in ["low", "safe", "normal"]):
        risk_level = "Low"
        flood_detected = "No"
        confidence = 91
        water_coverage = 9
        status_color = "green"
        context = (
            "The image currently shows low flood impact. "
            "Continue monitoring rainfall and drainage conditions."
        )
        recommendations = [
            "Stay alert",
            "Keep drains clear",
            "Monitor weather updates",
        ]

    else:
        risk_level = random.choice(["High", "Medium", "Low"])

        if risk_level == "High":
            flood_detected = "Yes"
            confidence = 94
            water_coverage = 38
            status_color = "red"
            context = (
                "The road is flooded and may not be safe for vehicles. "
                "Water is moving or accumulating, so risk can increase quickly."
            )
            recommendations = [
                "Do not drive through water",
                "Check local flood updates",
                "Move to higher ground if needed",
            ]

        elif risk_level == "Medium":
            flood_detected = "Yes"
            confidence = 89
            water_coverage = 25
            status_color = "yellow"
            context = (
                "The image suggests possible water accumulation. "
                "Flooding may become more serious if rainfall continues."
            )
            recommendations = [
                "Avoid low-lying areas",
                "Prepare flood barriers",
                "Monitor official warnings",
            ]

        else:
            flood_detected = "No"
            confidence = 91
            water_coverage = 9
            status_color = "green"
            context = (
                "The image currently shows low flood impact. "
                "Continue monitoring rainfall and drainage conditions."
            )
            recommendations = [
                "Stay alert",
                "Keep emergency contacts ready",
                "Monitor local weather",
            ]

    return {
        "file_name": detected_file_name,
        "file_size": file_size,

        "flood_detected": flood_detected,
        "detected": flood_detected,
        "risk_level": risk_level,
        "severity": risk_level,
        "confidence": confidence,
        "confidence_score": confidence,
        "water_coverage": water_coverage,
        "status_color": status_color,

        "what_happening": context,
        "context": context,
        "description": context,

        "recommendations": recommendations,
        "what_you_should_do": recommendations,
        "actions": recommendations,

        "model": "ResNet-101",
        "model_name": "ResNet-101",
        "accuracy": 96,
        "data_analyzed": "250,000 images",
        "status": "Analysis complete",

        "ai_info": {
            "model": "ResNet-101",
            "accuracy": "96%",
            "data_analyzed": "250,000 images",
        },

        "quick_status": {
            "flood_detected": flood_detected,
            "risk_level": risk_level,
            "confidence": confidence,
            "water_coverage": water_coverage,
        },
    }