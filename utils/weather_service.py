from __future__ import annotations

from datetime import datetime
from typing import Any

import requests
import streamlit as st


# Change this to your project location.
# Nay Pyi Taw default:
DEFAULT_LATITUDE = 19.7633
DEFAULT_LONGITUDE = 96.0785
DEFAULT_LOCATION_NAME = "Nay Pyi Taw"


WEATHER_CODE_MAP = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Cloudy", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Drizzle", "🌦️"),
    55: ("Heavy drizzle", "🌧️"),
    61: ("Light rain", "🌦️"),
    63: ("Rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    80: ("Rain showers", "🌦️"),
    81: ("Heavy showers", "🌧️"),
    82: ("Violent rain showers", "⛈️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with hail", "⛈️"),
    99: ("Severe thunderstorm", "⛈️"),
}


def _weather_label(code: int) -> tuple[str, str]:
    return WEATHER_CODE_MAP.get(int(code), ("Unknown", "☁️"))


@st.cache_data(ttl=600, show_spinner=False)
def get_realtime_weather(
    latitude: float = DEFAULT_LATITUDE,
    longitude: float = DEFAULT_LONGITUDE,
    location_name: str = DEFAULT_LOCATION_NAME,
) -> dict[str, Any]:
    """
    Gets real-time forecast data from Open-Meteo.
    Cached for 10 minutes to avoid slow reloads.
    """
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,precipitation,rain,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max",
        "forecast_days": 4,
        "timezone": "auto",
    }

    try:
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        payload = response.json()

        current = payload.get("current", {})
        daily = payload.get("daily", {})

        current_code = int(current.get("weather_code", 3))
        condition, icon = _weather_label(current_code)

        days = []
        times = daily.get("time", [])
        codes = daily.get("weather_code", [])
        rain_probs = daily.get("precipitation_probability_max", [])
        rain_sums = daily.get("precipitation_sum", [])

        for index, date_text in enumerate(times[:4]):
            day_name = datetime.fromisoformat(date_text).strftime("%a")
            day_code = int(codes[index]) if index < len(codes) else 3
            day_condition, day_icon = _weather_label(day_code)

            days.append(
                {
                    "day": day_name,
                    "icon": day_icon,
                    "condition": day_condition,
                    "rain_probability": int(rain_probs[index]) if index < len(rain_probs) and rain_probs[index] is not None else 0,
                    "rain_mm": float(rain_sums[index]) if index < len(rain_sums) and rain_sums[index] is not None else 0.0,
                }
            )

        rain_now = float(current.get("rain", 0) or 0)
        precipitation_now = float(current.get("precipitation", 0) or 0)
        rain_probability_today = days[0]["rain_probability"] if days else 0

        if rain_now > 10 or rain_probability_today >= 80:
            flood_weather_status = "Heavy Rain Expected"
        elif rain_now > 2 or rain_probability_today >= 55:
            flood_weather_status = "Rain Possible"
        elif precipitation_now > 0:
            flood_weather_status = "Light Rain Nearby"
        else:
            flood_weather_status = condition

        return {
            "ok": True,
            "location": location_name,
            "temperature": round(float(current.get("temperature_2m", 0))),
            "humidity": int(current.get("relative_humidity_2m", 0) or 0),
            "wind_speed": round(float(current.get("wind_speed_10m", 0) or 0), 1),
            "condition": condition,
            "icon": icon,
            "status": flood_weather_status,
            "days": days,
        }

    except Exception as error:
        return {
            "ok": False,
            "location": location_name,
            "temperature": 24,
            "humidity": 0,
            "wind_speed": 0,
            "condition": "Weather unavailable",
            "icon": "☁️",
            "status": "Weather data unavailable",
            "days": [
                {"day": "Fri", "icon": "☁️", "condition": "Cloudy", "rain_probability": 0, "rain_mm": 0},
                {"day": "Sat", "icon": "🌦️", "condition": "Showers", "rain_probability": 0, "rain_mm": 0},
                {"day": "Sun", "icon": "☀️", "condition": "Sunny", "rain_probability": 0, "rain_mm": 0},
                {"day": "Mon", "icon": "🌧️", "condition": "Rain", "rain_probability": 0, "rain_mm": 0},
            ],
            "error": str(error),
        }