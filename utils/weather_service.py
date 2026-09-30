from __future__ import annotations

from datetime import datetime
from typing import Any

import requests
import streamlit as st

DEFAULT_LATITUDE = 19.7633
DEFAULT_LONGITUDE = 96.0785
DEFAULT_LOCATION_NAME = "Nay Pyi Taw"

WEATHER_CODE_MAP = {
    0: ("Clear sky", "☀️"), 1: ("Mainly clear", "🌤️"), 2: ("Partly cloudy", "⛅"),
    3: ("Cloudy", "☁️"), 45: ("Fog", "🌫️"), 48: ("Fog", "🌫️"),
    51: ("Light drizzle", "🌦️"), 53: ("Drizzle", "🌦️"), 55: ("Heavy drizzle", "🌧️"),
    61: ("Light rain", "🌦️"), 63: ("Rain", "🌧️"), 65: ("Heavy rain", "🌧️"),
    80: ("Rain showers", "🌦️"), 81: ("Heavy showers", "🌧️"), 82: ("Violent rain showers", "⛈️"),
    95: ("Thunderstorm", "⛈️"), 96: ("Thunderstorm with hail", "⛈️"), 99: ("Severe thunderstorm", "⛈️"),
}



_LOCATION_ALIASES = {
    "nay pyi taw": "Naypyidaw, Myanmar",
    "naypyitaw": "Naypyidaw, Myanmar",
    "nay pyi daw": "Naypyidaw, Myanmar",
    "naypyidaw": "Naypyidaw, Myanmar",
    "yangon": "Yangon, Myanmar",
    "rangoon": "Yangon, Myanmar",
    "mandalay": "Mandalay, Myanmar",
    "bago": "Bago, Myanmar",
    "pegu": "Bago, Myanmar",
}

def _normalized_query(query: str) -> str:
    clean = " ".join((query or "").strip().split())
    alias = _LOCATION_ALIASES.get(clean.casefold())
    if alias:
        return alias
    # Bias ordinary place searches toward Myanmar while still allowing users
    # to explicitly type another country.
    if clean and "," not in clean and "myanmar" not in clean.casefold():
        return f"{clean}, Myanmar"
    return clean

def _weather_label(code: int) -> tuple[str, str]:
    return WEATHER_CODE_MAP.get(int(code), ("Unknown", "☁️"))


@st.cache_data(ttl=3600, show_spinner=False)
def geocode_location(query: str) -> dict[str, Any] | None:
    """Resolve a user-entered place name with OpenStreetMap Nominatim."""
    query = _normalized_query(query)
    if len(query) < 2:
        return None
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": query, "format": "jsonv2", "limit": 1, "addressdetails": 1},
            headers={"User-Agent": "Mekhala-AI-Flood-Assistant/1.0"},
            timeout=8,
        )
        response.raise_for_status()
        rows = response.json()
        if not rows:
            return None
        row = rows[0]
        address = row.get("address", {}) or {}
        short_name = (address.get("city") or address.get("town") or address.get("municipality")
                      or address.get("county") or address.get("state") or row.get("name") or query.split(",")[0])
        return {
            "name": row.get("display_name", query),
            "short_name": short_name,
            "latitude": float(row["lat"]),
            "longitude": float(row["lon"]),
        }
    except Exception:
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def reverse_geocode_location(latitude: float, longitude: float) -> dict[str, Any]:
    """Resolve a clicked coordinate to the best readable locality/region available."""
    lat, lon = float(latitude), float(longitude)

    def pack(address: dict[str, Any], display_name: str = "") -> dict[str, Any]:
        city = (address.get("city") or address.get("town") or address.get("village")
                or address.get("municipality") or address.get("city_district")
                or address.get("township") or address.get("county"))
        region = (address.get("state") or address.get("region") or address.get("state_district")
                  or address.get("county"))
        country = address.get("country") or "Myanmar"
        short = city or region or country or "Selected area"
        parts = []
        for value in (city, region, country):
            if value and value not in parts:
                parts.append(value)
        readable = ", ".join(parts) or display_name or "Selected area"
        return {"name": readable, "short_name": short, "city": city or "",
                "region": region or "", "state": region or "", "country": country,
                "latitude": lat, "longitude": lon}

    # Primary: OpenStreetMap Nominatim. zoom=18 gives the nearest named locality.
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "jsonv2", "zoom": 18,
                    "addressdetails": 1, "accept-language": "en"},
            headers={"User-Agent": "Mekhala-AI-Flood-Assistant/1.0 (university project)"},
            timeout=10,
        )
        r.raise_for_status()
        row = r.json() or {}
        address = row.get("address") or {}
        if address:
            return pack(address, row.get("display_name", ""))
    except Exception:
        pass

    # Fallback: BigDataCloud's public reverse-geocode endpoint (no API key).
    try:
        r = requests.get(
            "https://api.bigdatacloud.net/data/reverse-geocode-client",
            params={"latitude": lat, "longitude": lon, "localityLanguage": "en"},
            timeout=10,
        )
        r.raise_for_status()
        row = r.json() or {}
        locality = row.get("locality") or row.get("city") or row.get("principalSubdivision")
        region = row.get("principalSubdivision") or ""
        country = row.get("countryName") or "Myanmar"
        address = {"city": locality, "state": region, "country": country}
        if locality or region:
            return pack(address)
    except Exception:
        pass

    # Never expose raw coordinates as the main UI label.
    return {"name": "Selected area", "short_name": "Selected area", "city": "",
            "region": "", "state": "", "country": "Myanmar",
            "latitude": lat, "longitude": lon}


@st.cache_data(ttl=600, show_spinner=False)
def get_realtime_weather(
    latitude: float = DEFAULT_LATITUDE,
    longitude: float = DEFAULT_LONGITUDE,
    location_name: str = DEFAULT_LOCATION_NAME,
    forecast_days: int = 4,
) -> dict[str, Any]:
    """Get current conditions and up to 14 forecast days from Open-Meteo."""
    forecast_days = max(1, min(14, int(forecast_days)))
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,precipitation,rain,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max",
        "forecast_days": forecast_days,
        "timezone": "auto",
    }
    try:
        response = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=8)
        response.raise_for_status()
        payload = response.json()
        current, daily = payload.get("current", {}), payload.get("daily", {})
        condition, icon = _weather_label(int(current.get("weather_code", 3)))
        days = []
        times = daily.get("time", [])
        codes = daily.get("weather_code", [])
        probs = daily.get("precipitation_probability_max", [])
        sums = daily.get("precipitation_sum", [])
        maxs = daily.get("temperature_2m_max", [])
        mins = daily.get("temperature_2m_min", [])
        for i, date_text in enumerate(times[:forecast_days]):
            code = int(codes[i]) if i < len(codes) else 3
            day_condition, day_icon = _weather_label(code)
            days.append({
                "date": date_text,
                "day": datetime.fromisoformat(date_text).strftime("%a"),
                "icon": day_icon,
                "condition": day_condition,
                "rain_probability": int(probs[i] or 0) if i < len(probs) else 0,
                "rain_mm": round(float(sums[i] or 0), 1) if i < len(sums) else 0.0,
                "temp_max": round(float(maxs[i] or 0)) if i < len(maxs) else 0,
                "temp_min": round(float(mins[i] or 0)) if i < len(mins) else 0,
            })
        rain_now = float(current.get("rain", 0) or 0)
        today_prob = days[0]["rain_probability"] if days else 0
        if rain_now > 10 or today_prob >= 80:
            status = "Heavy rain expected"
        elif rain_now > 2 or today_prob >= 55:
            status = "Rain possible"
        elif float(current.get("precipitation", 0) or 0) > 0:
            status = "Light rain nearby"
        else:
            status = condition
        return {
            "ok": True, "location": location_name,
            "temperature": round(float(current.get("temperature_2m", 0) or 0)),
            "humidity": int(current.get("relative_humidity_2m", 0) or 0),
            "wind_speed": round(float(current.get("wind_speed_10m", 0) or 0), 1),
            "condition": condition, "icon": icon, "status": status, "days": days,
        }
    except Exception as error:
        return {"ok": False, "location": location_name, "temperature": 0, "humidity": 0,
                "wind_speed": 0, "condition": "Weather unavailable", "icon": "☁️",
                "status": "Weather data unavailable", "days": [], "error": str(error)}
