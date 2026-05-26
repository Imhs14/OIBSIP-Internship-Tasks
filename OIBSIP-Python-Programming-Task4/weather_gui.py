"""
weather_gui.py  –  Advanced GUI Weather App
=============================================
Advanced version: Tkinter-based GUI with:
  • Current conditions with weather icons (Unicode emoji)
  • Hourly & 5-day forecast (via OpenWeatherMap free-tier /forecast endpoint)
  • Wind speed, humidity, pressure, visibility
  • Celsius / Fahrenheit toggle
  • Location auto-detect via ip-api.com (no GPS hardware required)
  • Input validation & detailed error messages
  • Clean, modern dark-theme UI

Usage:
    python weather_gui.py

Requirements:
    pip install requests

API Key:
    Sign up free at https://openweathermap.org/api
    Replace API_KEY below with your key.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import json
from datetime import datetime
from collections import defaultdict

# ── Configuration ────────────────────────────────────────────────────────────
API_KEY          = "c757f20d5d6b504ff4ba642d4255cf5e"
WEATHER_URL      = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL     = "https://api.openweathermap.org/data/2.5/forecast"
GEO_URL          = "http://ip-api.com/json/"          # free, no key needed

# ── Theme ─────────────────────────────────────────────────────────────────────
COLORS = {
    "bg":          "#0f1923",
    "card":        "#1a2636",
    "card2":       "#1e2d3d",
    "accent":      "#4fc3f7",
    "accent2":     "#81d4fa",
    "text":        "#e8f4f8",
    "subtext":     "#90a4ae",
    "border":      "#263545",
    "danger":      "#ef5350",
    "success":     "#66bb6a",
    "warn":        "#ffa726",
}

FONTS = {
    "title":   ("Helvetica", 28, "bold"),
    "big":     ("Helvetica", 48, "bold"),
    "medium":  ("Helvetica", 16),
    "small":   ("Helvetica", 11),
    "tiny":    ("Helvetica", 9),
    "label":   ("Helvetica", 12, "bold"),
}

CONDITION_ICONS = {
    "Clear":        "☀️", "Clouds": "☁️", "Rain": "🌧️",
    "Drizzle":      "🌦️", "Thunderstorm": "⛈️", "Snow": "❄️",
    "Mist":         "🌫️", "Fog": "🌫️", "Haze": "🌫️",
    "Smoke":        "💨", "Dust": "🌪️", "Sand": "🌪️",
    "Ash":          "🌋", "Squall": "💨", "Tornado": "🌪️",
}

WIND_DIRS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


# ── Utility ───────────────────────────────────────────────────────────────────

def c_to_f(c): return c * 9 / 5 + 32
def ms_to_mph(ms): return ms * 2.237
def wind_dir(deg): return WIND_DIRS[round(deg / 45) % 8]


# ── API helpers ───────────────────────────────────────────────────────────────

def get_current_weather(location: str, metric: bool) -> dict:
    units = "metric" if metric else "imperial"
    r = requests.get(WEATHER_URL, params={"q": location, "appid": API_KEY, "units": units}, timeout=10)
    r.raise_for_status()
    return r.json()


def get_forecast(location: str, metric: bool) -> dict:
    units = "metric" if metric else "imperial"
    r = requests.get(FORECAST_URL, params={"q": location, "appid": API_KEY, "units": units, "cnt": 40}, timeout=10)
    r.raise_for_status()
    return r.json()


def detect_location() -> str:
    r = requests.get(GEO_URL, timeout=8)
    data = r.json()
    if data.get("status") == "success":
        return data.get("city", "")
    return ""


# ── Demo data (shown when no API key is set) ──────────────────────────────────

def get_demo_current():
    return {
        "name": "Chennai", "sys": {"country": "IN", "sunrise": 1700000000, "sunset": 1700043600},
        "main": {"temp": 34.5, "feels_like": 38.2, "temp_min": 31.0, "temp_max": 36.0,
                 "humidity": 72, "pressure": 1006},
        "visibility": 6000,
        "wind": {"speed": 4.5, "deg": 200},
        "weather": [{"main": "Clouds", "description": "Partly Cloudy"}],
    }


def get_demo_forecast():
    import time
    items = []
    conditions = ["Clear", "Rain", "Clouds", "Clear", "Thunderstorm",
                  "Clear", "Clouds", "Rain", "Clear", "Clear"]
    for i in range(40):
        ts = int(time.time()) + i * 10800
        cond = conditions[i % len(conditions)]
        items.append({
            "dt": ts,
            "dt_txt": datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"),
            "main": {"temp": 30 + (i % 8) - 3, "humidity": 60 + (i % 20)},
            "weather": [{"main": cond, "description": cond}],
            "wind": {"speed": 3 + (i % 5), "deg": 180},
        })
    return {"list": items}


# ══════════════════════════════════════════════════════════════════════════════
#  GUI Application
# ══════════════════════════════════════════════════════════════════════════════

class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Weather App")
        self.geometry("900x700")
        self.minsize(800, 600)
        self.configure(bg=COLORS["bg"])
        self.resizable(True, True)

        self.metric = tk.BooleanVar(value=True)     # True = Celsius
        self.loading = False

        self._build_ui()

    # ── Build UI ───────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header bar
        header = tk.Frame(self, bg=COLORS["card"], pady=10)
        header.pack(fill="x")

        tk.Label(header, text="🌤  Weather App", font=FONTS["title"],
                 bg=COLORS["card"], fg=COLORS["accent"]).pack(side="left", padx=20)

        # Unit toggle
        right = tk.Frame(header, bg=COLORS["card"])
        right.pack(side="right", padx=20)
        tk.Label(right, text="°F", font=FONTS["medium"], bg=COLORS["card"],
                 fg=COLORS["subtext"]).pack(side="left")
        self.toggle = tk.Checkbutton(right, variable=self.metric, bg=COLORS["card"],
                                     activebackground=COLORS["card"],
                                     selectcolor=COLORS["accent"],
                                     command=self._on_unit_toggle)
        self.toggle.pack(side="left")
        tk.Label(right, text="°C", font=FONTS["medium"], bg=COLORS["card"],
                 fg=COLORS["subtext"]).pack(side="left")

        # ── Search bar
        search_frame = tk.Frame(self, bg=COLORS["bg"], pady=15)
        search_frame.pack(fill="x", padx=30)

        self.entry = tk.Entry(search_frame, font=FONTS["medium"], width=32,
                              bg=COLORS["card2"], fg=COLORS["text"],
                              insertbackground=COLORS["text"],
                              relief="flat", bd=8)
        self.entry.pack(side="left", padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self._search())
        self.entry.insert(0, "Enter city or ZIP…")
        self.entry.bind("<FocusIn>",  self._clear_placeholder)
        self.entry.bind("<FocusOut>", self._restore_placeholder)

        btn_style = dict(font=FONTS["label"], relief="flat", bd=0,
                         cursor="hand2", padx=14, pady=6)

        tk.Button(search_frame, text="Search", bg=COLORS["accent"], fg=COLORS["bg"],
                  command=self._search, **btn_style).pack(side="left", padx=(0, 8))

        tk.Button(search_frame, text="📍 Auto-Detect", bg=COLORS["card2"],
                  fg=COLORS["accent2"], command=self._auto_detect, **btn_style).pack(side="left")

        # ── Status / spinner label
        self.status_var = tk.StringVar(value="Enter a city or ZIP code to get started.")
        self.status_lbl = tk.Label(self, textvariable=self.status_var,
                                   font=FONTS["small"], bg=COLORS["bg"],
                                   fg=COLORS["subtext"])
        self.status_lbl.pack()

        # ── Scrollable content area
        canvas = tk.Canvas(self, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.content = tk.Frame(canvas, bg=COLORS["bg"])

        self.content.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self.content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=(30, 0), pady=10)
        scrollbar.pack(side="right", fill="y")

        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        if API_KEY == "YOUR_API_KEY_HERE":
            self._show_demo()

    # ── Placeholder handling ───────────────────────────────────────────────────

    def _clear_placeholder(self, _):
        if self.entry.get() == "Enter city or ZIP…":
            self.entry.delete(0, "end")
            self.entry.config(fg=COLORS["text"])

    def _restore_placeholder(self, _):
        if not self.entry.get():
            self.entry.insert(0, "Enter city or ZIP…")
            self.entry.config(fg=COLORS["subtext"])

    # ── Search flow ────────────────────────────────────────────────────────────

    def _search(self):
        loc = self.entry.get().strip()
        if not loc or loc == "Enter city or ZIP…":
            messagebox.showwarning("No Location", "Please enter a city name or ZIP code.")
            return
        if len(loc) < 2:
            messagebox.showwarning("Too short", "Enter at least 2 characters.")
            return
        self._fetch(loc)

    def _auto_detect(self):
        self.status_var.set("📍 Detecting your location…")
        threading.Thread(target=self._detect_thread, daemon=True).start()

    def _detect_thread(self):
        try:
            city = detect_location()
            if city:
                self.entry.delete(0, "end")
                self.entry.insert(0, city)
                self.entry.config(fg=COLORS["text"])
                self._fetch(city)
            else:
                self.after(0, lambda: self.status_var.set("❌ Could not detect location."))
        except Exception as e:
            self.after(0, lambda: self.status_var.set(f"❌ {e}"))

    def _fetch(self, location: str):
        if self.loading:
            return
        self.loading = True
        self.status_var.set("⏳ Fetching weather data…")
        threading.Thread(target=self._fetch_thread, args=(location,), daemon=True).start()

    def _fetch_thread(self, location: str):
        try:
            if API_KEY == "YOUR_API_KEY_HERE":
                import time; time.sleep(0.6)
                current  = get_demo_current()
                forecast = get_demo_forecast()
            else:
                current  = get_current_weather(location, self.metric.get())
                forecast = get_forecast(location, self.metric.get())

            self.after(0, lambda: self._render(current, forecast))
        except requests.exceptions.ConnectionError:
            self.after(0, lambda: self._show_error("No internet connection."))
        except requests.exceptions.Timeout:
            self.after(0, lambda: self._show_error("Request timed out."))
        except requests.exceptions.HTTPError as e:
            code = e.response.status_code
            msg = {
                401: "Invalid API key. Set API_KEY in the script.",
                404: f"Location '{location}' not found.",
            }.get(code, f"HTTP error {code}.")
            self.after(0, lambda: self._show_error(msg))
        except Exception as e:
            self.after(0, lambda: self._show_error(str(e)))
        finally:
            self.loading = False

    def _on_unit_toggle(self):
        loc = self.entry.get().strip()
        if loc and loc != "Enter city or ZIP…":
            self._fetch(loc)

    # ── Error display ──────────────────────────────────────────────────────────

    def _show_error(self, msg: str):
        self.status_var.set(f"❌ {msg}")
        for w in self.content.winfo_children():
            w.destroy()
        tk.Label(self.content, text=f"⚠️  {msg}", font=FONTS["medium"],
                 bg=COLORS["bg"], fg=COLORS["danger"],
                 wraplength=700).pack(pady=40)

    # ── Demo banner ────────────────────────────────────────────────────────────

    def _show_demo(self):
        banner = tk.Frame(self.content, bg=COLORS["warn"], pady=6)
        banner.pack(fill="x", pady=(0, 10))
        tk.Label(banner,
                 text="⚠️  DEMO MODE — set API_KEY to use real data  |  "
                      "Get a free key at openweathermap.org/api",
                 font=FONTS["small"], bg=COLORS["warn"], fg="#000").pack()

        current  = get_demo_current()
        forecast = get_demo_forecast()
        self._render(current, forecast)

    # ── Render everything ──────────────────────────────────────────────────────

    def _render(self, current: dict, forecast: dict):
        for w in self.content.winfo_children():
            if isinstance(w, tk.Frame) and w.cget("bg") == COLORS["warn"]:
                continue            # keep demo banner
            w.destroy()

        self.status_var.set("")
        unit   = "°C" if self.metric.get() else "°F"
        wspeed = "m/s" if self.metric.get() else "mph"

        # ── Current weather card ───────────────────────────────────────────────
        card = tk.Frame(self.content, bg=COLORS["card"], bd=0, pady=20, padx=24)
        card.pack(fill="x", pady=(8, 6))

        city    = current["name"]
        country = current["sys"]["country"]
        temp    = current["main"]["temp"]
        feels   = current["main"]["feels_like"]
        t_min   = current["main"]["temp_min"]
        t_max   = current["main"]["temp_max"]
        hum     = current["main"]["humidity"]
        pres    = current["main"]["pressure"]
        vis     = current.get("visibility", None)
        ws      = current["wind"]["speed"]
        wd      = wind_dir(current["wind"].get("deg", 0))
        cond    = current["weather"][0]["main"]
        desc    = current["weather"][0]["description"].title()
        icon    = CONDITION_ICONS.get(cond, "🌡️")

        # Left: city + icon + temp
        left = tk.Frame(card, bg=COLORS["card"])
        left.pack(side="left", fill="y")

        tk.Label(left, text=f"{city}, {country}", font=FONTS["title"],
                 bg=COLORS["card"], fg=COLORS["text"]).pack(anchor="w")
        tk.Label(left, text=desc, font=FONTS["medium"],
                 bg=COLORS["card"], fg=COLORS["subtext"]).pack(anchor="w")

        temp_row = tk.Frame(left, bg=COLORS["card"])
        temp_row.pack(anchor="w", pady=(8, 0))
        tk.Label(temp_row, text=icon, font=("Helvetica", 40),
                 bg=COLORS["card"]).pack(side="left")
        tk.Label(temp_row, text=f"  {temp:.1f}{unit}", font=FONTS["big"],
                 bg=COLORS["card"], fg=COLORS["accent"]).pack(side="left")

        tk.Label(left, text=f"Feels like {feels:.1f}{unit}   "
                             f"↓ {t_min:.1f}{unit}  ↑ {t_max:.1f}{unit}",
                 font=FONTS["small"], bg=COLORS["card"], fg=COLORS["subtext"]).pack(anchor="w")

        # Right: detail stats
        right = tk.Frame(card, bg=COLORS["card"])
        right.pack(side="right", padx=20)

        vis_str = f"{vis / 1000:.1f} km" if vis else "N/A"
        stats = [
            ("💧 Humidity",    f"{hum}%"),
            ("🌀 Pressure",    f"{pres} hPa"),
            ("👁 Visibility",  vis_str),
            ("💨 Wind",        f"{ws} {wspeed} {wd}"),
        ]
        for label, val in stats:
            row = tk.Frame(right, bg=COLORS["card"])
            row.pack(anchor="w", pady=2)
            tk.Label(row, text=label, font=FONTS["small"], width=16,
                     bg=COLORS["card"], fg=COLORS["subtext"], anchor="w").pack(side="left")
            tk.Label(row, text=val, font=FONTS["label"],
                     bg=COLORS["card"], fg=COLORS["text"]).pack(side="left")

        # ── Hourly forecast (next 24 h) ───────────────────────────────────────
        self._section("⏱  Hourly Forecast (next 24 h)")

        hourly_frame = tk.Frame(self.content, bg=COLORS["bg"])
        hourly_frame.pack(fill="x", pady=(0, 6))

        for item in forecast["list"][:8]:
            t    = datetime.fromtimestamp(item["dt"]).strftime("%H:%M")
            tmp  = item["main"]["temp"]
            ic   = CONDITION_ICONS.get(item["weather"][0]["main"], "🌡️")
            h    = item["main"]["humidity"]

            col = tk.Frame(hourly_frame, bg=COLORS["card2"], padx=12, pady=10)
            col.pack(side="left", padx=4, pady=4)

            tk.Label(col, text=t,  font=FONTS["tiny"],   bg=COLORS["card2"], fg=COLORS["subtext"]).pack()
            tk.Label(col, text=ic, font=("Helvetica", 20), bg=COLORS["card2"]).pack()
            tk.Label(col, text=f"{tmp:.0f}{unit}", font=FONTS["label"],
                     bg=COLORS["card2"], fg=COLORS["accent"]).pack()
            tk.Label(col, text=f"{h}%", font=FONTS["tiny"],
                     bg=COLORS["card2"], fg=COLORS["subtext"]).pack()

        # ── 5-day daily forecast ──────────────────────────────────────────────
        self._section("📅  5-Day Forecast")

        # Group by date, take noon reading (or first available)
        days: dict = defaultdict(list)
        for item in forecast["list"]:
            date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
            days[date].append(item)

        daily_frame = tk.Frame(self.content, bg=COLORS["bg"])
        daily_frame.pack(fill="x", pady=(0, 20))

        for date, items in list(days.items())[:5]:
            noon = min(items, key=lambda x:
                       abs(datetime.fromtimestamp(x["dt"]).hour - 12))
            day_name = datetime.strptime(date, "%Y-%m-%d").strftime("%a %d %b")
            t_hi   = max(i["main"]["temp"] for i in items)
            t_lo   = min(i["main"]["temp"] for i in items)
            ic     = CONDITION_ICONS.get(noon["weather"][0]["main"], "🌡️")
            desc_d = noon["weather"][0]["description"].title()
            ws_d   = noon["wind"]["speed"]
            wd_d   = wind_dir(noon["wind"].get("deg", 0))

            row = tk.Frame(daily_frame, bg=COLORS["card2"], pady=10, padx=16)
            row.pack(fill="x", pady=3)

            tk.Label(row, text=day_name, font=FONTS["label"], width=12,
                     bg=COLORS["card2"], fg=COLORS["text"], anchor="w").pack(side="left")
            tk.Label(row, text=ic, font=("Helvetica", 18),
                     bg=COLORS["card2"]).pack(side="left", padx=8)
            tk.Label(row, text=desc_d, font=FONTS["small"], width=18,
                     bg=COLORS["card2"], fg=COLORS["subtext"], anchor="w").pack(side="left")
            tk.Label(row, text=f"↑ {t_hi:.1f}{unit}  ↓ {t_lo:.1f}{unit}",
                     font=FONTS["medium"],
                     bg=COLORS["card2"], fg=COLORS["accent"]).pack(side="left", padx=16)
            tk.Label(row, text=f"💨 {ws_d} {wspeed} {wd_d}", font=FONTS["small"],
                     bg=COLORS["card2"], fg=COLORS["subtext"]).pack(side="right", padx=8)

    def _section(self, title: str):
        tk.Label(self.content, text=title, font=FONTS["label"],
                 bg=COLORS["bg"], fg=COLORS["accent2"],
                 anchor="w").pack(fill="x", pady=(14, 2))
        tk.Frame(self.content, bg=COLORS["border"], height=1).pack(fill="x", pady=(0, 6))


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
