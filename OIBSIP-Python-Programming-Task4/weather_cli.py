"""
weather_cli.py  –  Basic Command-Line Weather App
===================================================
Beginner version: fetches current weather from OpenWeatherMap API
and displays temperature, humidity, and conditions.

Usage:
    python weather_cli.py

Requirements:
    pip install requests

API Key:
    Sign up free at https://openweathermap.org/api
    Replace API_KEY below with your key.
"""

import requests
import json
import sys

# ── Configuration ────────────────────────────────────────────────────────────
API_KEY  = 'c757f20d5d6b504ff4ba642d4255cf5e'       # Replace with your OpenWeatherMap key
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Weather condition emojis for a nicer CLI experience
CONDITION_ICONS = {
    "Clear":        "☀️",
    "Clouds":       "☁️",
    "Rain":         "🌧️",
    "Drizzle":      "🌦️",
    "Thunderstorm": "⛈️",
    "Snow":         "❄️",
    "Mist":         "🌫️",
    "Fog":          "🌫️",
    "Haze":         "🌫️",
    "Smoke":        "💨",
    "Dust":         "🌪️",
    "Sand":         "🌪️",
    "Ash":          "🌋",
    "Squall":       "💨",
    "Tornado":      "🌪️",
}

# ── Helper functions ─────────────────────────────────────────────────────────

def celsius_to_fahrenheit(c: float) -> float:
    return c * 9 / 5 + 32


def fetch_weather(location: str, units: str = "metric") -> dict:
    """
    Fetch weather data from OpenWeatherMap.
    location – city name (e.g. 'London') or ZIP,countrycode (e.g. '10001,US')
    units    – 'metric' (°C) | 'imperial' (°F) | 'standard' (K)
    """
    params = {
        "q":       location,
        "appid":   API_KEY,
        "units":   units,
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()          # raises HTTPError for 4xx/5xx
        return response.json()
    except requests.exceptions.ConnectionError:
        print("\n❌  No internet connection. Please check your network.\n")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("\n❌  Request timed out. The API server may be down.\n")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        if status == 401:
            print("\n❌  Invalid API key. Set your key in API_KEY at the top of the file.\n")
        elif status == 404:
            print(f"\n❌  Location '{location}' not found. Try a different city name or ZIP.\n")
        else:
            print(f"\n❌  HTTP error {status}: {e}\n")
        sys.exit(1)


def display_weather(data: dict, unit_label: str) -> None:
    """Pretty-print weather data to the terminal."""

    city        = data["name"]
    country     = data["sys"]["country"]
    temp        = data["main"]["temp"]
    feels_like  = data["main"]["feels_like"]
    temp_min    = data["main"]["temp_min"]
    temp_max    = data["main"]["temp_max"]
    humidity    = data["main"]["humidity"]
    pressure    = data["main"]["pressure"]
    visibility  = data.get("visibility", "N/A")
    wind_speed  = data["wind"]["speed"]
    wind_deg    = data["wind"].get("deg", 0)
    condition   = data["weather"][0]["main"]
    description = data["weather"][0]["description"].title()
    icon        = CONDITION_ICONS.get(condition, "🌡️")

    # Wind direction from degrees
    dirs = ["N","NE","E","SE","S","SW","W","NW"]
    wind_dir = dirs[round(wind_deg / 45) % 8]

    # Visibility in km
    vis_str = f"{visibility / 1000:.1f} km" if isinstance(visibility, int) else "N/A"

    speed_unit = "m/s" if unit_label == "°C" else "mph"

    print("\n" + "═" * 50)
    print(f"  {icon}  Weather for {city}, {country}")
    print("═" * 50)
    print(f"  Condition   : {description}")
    print(f"  Temperature : {temp:.1f}{unit_label}  (feels like {feels_like:.1f}{unit_label})")
    print(f"  Range       : {temp_min:.1f}{unit_label} – {temp_max:.1f}{unit_label}")
    print(f"  Humidity    : {humidity}%")
    print(f"  Pressure    : {pressure} hPa")
    print(f"  Visibility  : {vis_str}")
    print(f"  Wind        : {wind_speed} {speed_unit}  {wind_dir}")
    print("═" * 50 + "\n")


def get_location_input() -> str:
    """Prompt the user for a city name or ZIP code with validation."""
    while True:
        location = input("Enter city name or ZIP code (e.g. 'London' or '10001,US'): ").strip()
        if len(location) >= 2:
            return location
        print("  ⚠️  Please enter a valid location (at least 2 characters).\n")


def get_unit_choice() -> tuple[str, str]:
    """Ask user for preferred temperature unit."""
    print("\nTemperature unit:")
    print("  1. Celsius  (°C)   [default]")
    print("  2. Fahrenheit (°F)")
    choice = input("Choose (1/2): ").strip()
    if choice == "2":
        return "imperial", "°F"
    return "metric", "°C"


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("\n╔══════════════════════════════════╗")
    print("║    🌤️  CLI Weather App  🌤️         ║")
    print("╚══════════════════════════════════╝\n")

    if API_KEY == "YOUR_API_KEY_HERE":
        print("⚠️  Demo mode: No API key set.")
        print("   Get a free key at https://openweathermap.org/api")
        print("   Replace API_KEY in the script, then re-run.\n")
        # Show sample output so the user can see the format
        demo_data = {
            "name": "Chennai",
            "sys": {"country": "IN"},
            "main": {
                "temp": 34.5, "feels_like": 38.2,
                "temp_min": 31.0, "temp_max": 36.0,
                "humidity": 72, "pressure": 1006,
            },
            "visibility": 6000,
            "wind": {"speed": 4.5, "deg": 200},
            "weather": [{"main": "Clouds", "description": "partly cloudy"}],
        }
        display_weather(demo_data, "°C")
        return

    location          = get_location_input()
    units, unit_label = get_unit_choice()

    print("\n⏳  Fetching weather data…")
    data = fetch_weather(location, units)
    display_weather(data, unit_label)

    # Allow the user to search again
    while True:
        again = input("Search another location? (y/n): ").strip().lower()
        if again == "y":
            location = get_location_input()
            print("\n⏳  Fetching weather data…")
            data = fetch_weather(location, units)
            display_weather(data, unit_label)
        else:
            print("\nGoodbye! ☀️\n")
            break


if __name__ == "__main__":
    main()
