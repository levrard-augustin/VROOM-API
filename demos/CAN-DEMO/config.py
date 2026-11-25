# ============================================================
#  config.py — Configuration API CAN & signaux
# ============================================================

# ---------- API C++ ----------
API_HOST = "localhost"
API_PORT = 8080
API_BASE_URL = f"http://{API_HOST}:{API_PORT}"

# Endpoints (à adapter selon votre API C++)
ENDPOINTS = {
    "all_signals":   "/api/can/signals",       # GET  → tous les signaux
    "signal":        "/api/can/signal/{name}",  # GET  → un signal précis
    "frames":        "/api/can/frames",         # GET  → trames brutes
    "live_stream":   "/api/can/stream",         # GET  → SSE ou long-poll
    "status":        "/api/status",             # GET  → état du bus CAN
}

POLL_INTERVAL_MS = 100   # ms entre deux appels API (10 Hz)
REQUEST_TIMEOUT  = 0.5   # secondes

# ---------- Signaux CAN attendus ----------
# Clé = nom interne PyGame, Valeur = nom du signal dans votre API
SIGNAL_MAP = {
    "speed":          "VehicleSpeed",          # km/h
    "rpm":            "EngineRPM",             # tr/min
    "throttle":       "ThrottlePosition",      # %
    "engine_temp":    "EngineCoolantTemp",      # °C
    "fuel_level":     "FuelLevel",             # %
    "battery":        "BatteryVoltage",        # V
    "gear":           "CurrentGear",           # 1-8 / N / R
    "turn_left":      "TurnSignalLeft",        # bool
    "turn_right":     "TurnSignalRight",       # bool
    "brake":          "BrakePedal",            # bool / %
    "handbrake":      "ParkingBrake",          # bool
    "abs":            "ABSActive",             # bool
    "esp":            "ESPActive",             # bool
    "door_fl":        "DoorFrontLeft",         # bool ouvert
    "door_fr":        "DoorFrontRight",
    "door_rl":        "DoorRearLeft",
    "door_rr":        "DoorRearRight",
    "oil_pressure":   "OilPressure",           # bar
    "outside_temp":   "ExternalTemperature",   # °C
    "odometer":       "Odometer",              # km
}

# ---------- Valeurs par défaut (mode démo / API hors ligne) ----------
DEFAULT_VALUES = {
    "speed":       0.0,
    "rpm":         800.0,
    "throttle":    0.0,
    "engine_temp": 20.0,
    "fuel_level":  75.0,
    "battery":     12.4,
    "gear":        "N",
    "turn_left":   False,
    "turn_right":  False,
    "brake":       False,
    "handbrake":   True,
    "abs":         False,
    "esp":         False,
    "door_fl":     False,
    "door_fr":     False,
    "door_rl":     False,
    "door_rr":     False,
    "oil_pressure":3.5,
    "outside_temp":20.0,
    "odometer":    42000.0,
}

# ---------- Limites pour jauges ----------
GAUGE_LIMITS = {
    "speed":       {"min": 0,   "max": 220,  "warn": 180,  "unit": "km/h"},
    "rpm":         {"min": 0,   "max": 7000, "warn": 6000, "unit": "tr/min"},
    "throttle":    {"min": 0,   "max": 100,  "warn": 95,   "unit": "%"},
    "engine_temp": {"min": 40,  "max": 130,  "warn": 110,  "unit": "°C"},
    "fuel_level":  {"min": 0,   "max": 100,  "warn": 15,   "unit": "%"},
    "battery":     {"min": 10,  "max": 15,   "warn": 11.5, "unit": "V"},
    "oil_pressure":{"min": 0,   "max": 8,    "warn": 1.0,  "unit": "bar"},
}

# ---------- Fenêtre ----------
WINDOW_WIDTH  = 1400
WINDOW_HEIGHT = 800
WINDOW_TITLE  = "CAN Bus Visualizer — Opel Corsa"
FPS           = 60

# ---------- Palette Opel Corsa ----------
COLOR_CORSA_GREEN   = (34,  139, 34)
COLOR_CORSA_GREEN_D = (20,  100, 20)
COLOR_WHITE_STRIPE  = (240, 240, 240)
COLOR_GLASS         = (120, 180, 210)
COLOR_BODY_SHADOW   = (15,  80,  15)
COLOR_WHEEL         = (30,  30,  30)
COLOR_HUBCAP        = (180, 180, 190)
COLOR_HEADLIGHT     = (255, 255, 200)
COLOR_TAILLIGHT     = (200, 0,   0)

# ---------- UI ----------
COLOR_BG            = (18,  18,  25)
COLOR_PANEL         = (28,  28,  38)
COLOR_ACCENT        = (0,   200, 100)
COLOR_WARN          = (255, 160, 0)
COLOR_DANGER        = (220, 40,  40)
COLOR_TEXT          = (220, 220, 230)
COLOR_TEXT_DIM      = (120, 120, 140)
COLOR_GAUGE_BG      = (40,  40,  55)
COLOR_GAUGE_FG      = (0,   200, 100)