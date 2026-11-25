# ============================================================
#  can_data.py — Simulation CAN + point de branchement API
# ============================================================
#
#  TON COLLÈGUE branche son API ici :
#  Remplace le contenu de _fetch_from_api() par ses appels.
#  Le reste du visualiseur n'a pas besoin d'être modifié.
#
import socket
import threading
import time
import math
import random
from config import DEFAULT_VALUES

SERVER_IP   = "192.168.4.1"
SERVER_PORT = 8888
TIMEOUT     = 2.0  # secondes

class CANData:
    """
    Fournit les données CAN au visualiseur.
    Mode DEMO par défaut — prêt à recevoir l'API du collègue.
    """

    def __init__(self):
        self._data    = dict(DEFAULT_VALUES)
        self._lock    = threading.Lock()
        self._running = False
        self._thread  = None
        self._t       = 0.0           # temps interne simulation
        self._frames  = []            # trames brutes (optionnel)

    # ------------------------------------------------------------------
    # Interface publique (utilisée par le visualiseur)
    # ------------------------------------------------------------------

    def start(self):
        self._running = True
        self._thread  = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def get(self, key: str):
        with self._lock:
            return self._data.get(key, DEFAULT_VALUES.get(key))

    def get_all(self) -> dict:
        with self._lock:
            return dict(self._data)

    def get_frames(self) -> list:
        with self._lock:
            return list(self._frames[-50:])

    # ------------------------------------------------------------------
    # ⬇⬇⬇  TON COLLÈGUE MODIFIE UNIQUEMENT CE BLOC  ⬇⬇⬇
    # ------------------------------------------------------------------

    def send_udp_request(msg: str, timeout: float = TIMEOUT) -> str | None:
        """
        Envoie une commande à l'ESP32 et retourne la réponse sous forme de string.
        Retourne None en cas d'erreur ou de timeout.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(timeout)
            try:
                sock.sendto(msg.encode(), (SERVER_IP, SERVER_PORT))
                data, _ = sock.recvfrom(1024)
                return data.decode().strip()
            except socket.timeout:
                print(f"[TIMEOUT] Pas de réponse pour la commande '{msg}'")
                return None
            except OSError as e:
                print(f"[ERREUR] {e}")
                return None

    def _fetch_from_api(self) -> dict | None:
        """
        Retourne un dict avec les clés de DEFAULT_VALUES,
        ou None si pas de données dispo (→ bascule sur démo).

        Exemple d'intégration future :
            import requests
            r = requests.get("http://localhost:8080/api/can/signals", timeout=0.5)
            raw = r.json()
            return {
                "speed":       raw["VehicleSpeed"],
                "rpm":         raw["EngineRPM"],
                "engine_temp": raw["EngineCoolantTemp"],
                # ... etc.
            }
        """
        rpm = CANData.send_udp_request("GET_RPM")
        # gear = CANData.send_udp_request("GET_GEAR")
        turn = int(CANData.send_udp_request("GET_TURN_SIGNAL"))
        turn_left = False
        turn_right = False
        if turn > 0:
            turn_left = False
            turn_right = True

        if turn < 0:
            turn_left = True
            turn_right = False

        brake = (int(CANData.send_udp_request("GET_BRAKES")) == 1)
        door = int(CANData.send_udp_request("GET_DOOR"))

        door_open = (door == 1)
        print(door_open)

        return {
            "rpm": float(rpm),
            # "throttle":     round(throttle, 1),
            # "engine_temp":  round(e_temp, 1),
            # "fuel_level":   max(0.0, 75 - t * 0.02),
            # "battery":      12.4 + random.gauss(0, 0.05),
            # "gear":         gear,
            "turn_left": turn_left,
            "turn_right": turn_right,
            "brake": brake,
            # "handbrake":    speed < 1,
            # "abs":          False,
            # "esp":          False,
            "door_fl": door_open
            # "door_fr":      False,
            # "door_rl":      False,
            # "door_rr":      False,
            # "oil_pressure": 3.5 + speed * 0.005 + random.gauss(0, 0.05),
            # "outside_temp": 22.0 + random.gauss(0, 0.1),
            # "odometer":     42000.0 + t / 36.0,
        }

    # ------------------------------------------------------------------
    # ⬆⬆⬆  FIN DU BLOC À MODIFIER  ⬆⬆⬆
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Boucle interne
    # ------------------------------------------------------------------

    def _loop(self):
        while self._running:
            t0 = time.monotonic()

            api_data = self._fetch_from_api()
            if api_data:
                with self._lock:
                    self._data.update(api_data)
            else:
                self._run_demo()

            elapsed = time.monotonic() - t0
            time.sleep(max(0, 0.1 - elapsed))   # 10 Hz

    # ------------------------------------------------------------------
    # Simulation démo
    # ------------------------------------------------------------------

    def _run_demo(self):
        self._t  += 0.1
        t         = self._t
        cycle     = t % 60

        speed    = max(0.0, min(160.0, _demo_speed(cycle)))
        rpm      = max(800.0, 800 + speed * 18 + random.gauss(0, 30))
        throttle = max(0.0, min(100.0, _demo_throttle(cycle)))
        e_temp   = min(90.0, 20 + t * 0.5 + random.gauss(0, 0.2))
        gear     = _demo_gear(speed)
        blink_l  = (5  < cycle < 8)  or (38 < cycle < 41)
        blink_r  = (25 < cycle < 28) or (52 < cycle < 55)

        with self._lock:
            self._data.update({
                "speed":        round(speed, 1),
                "rpm":          round(rpm, 0),
                "throttle":     round(throttle, 1),
                "engine_temp":  round(e_temp, 1),
                "fuel_level":   max(0.0, 75 - t * 0.02),
                "battery":      12.4 + random.gauss(0, 0.05),
                "gear":         gear,
                "turn_left":    blink_l and (int(t * 4) % 2 == 0),
                "turn_right":   blink_r and (int(t * 4) % 2 == 0),
                "brake":        15 < cycle < 18,
                "handbrake":    speed < 1,
                "abs":          False,
                "esp":          False,
                "door_fl":      False,
                "door_fr":      False,
                "door_rl":      False,
                "door_rr":      False,
                "oil_pressure": 3.5 + speed * 0.005 + random.gauss(0, 0.05),
                "outside_temp": 22.0 + random.gauss(0, 0.1),
                "odometer":     42000.0 + t / 36.0,
            })
            # Trames simulées
            self._frames.append({
                "id":   hex(random.choice([0x100, 0x200, 0x300, 0x7DF])),
                "dlc":  8,
                "data": [random.randint(0, 255) for _ in range(8)],
                "ts":   round(t, 3),
            })


# ------------------------------------------------------------------
# Helpers simulation
# ------------------------------------------------------------------

def _demo_speed(cycle: float) -> float:
    if cycle < 5:   return 0
    if cycle < 15:  return (cycle - 5) * 11
    if cycle < 25:  return 110 + math.sin((cycle - 15) * 0.3) * 20
    if cycle < 35:  return max(0, 110 - (cycle - 25) * 11)
    if cycle < 40:  return 0
    if cycle < 50:  return (cycle - 40) * 8
    if cycle < 55:  return 80 + math.sin((cycle - 50) * 0.6) * 10
    return max(0, 80 - (cycle - 55) * 16)

def _demo_throttle(cycle: float) -> float:
    if cycle < 5:   return 0
    if cycle < 15:  return 60 + math.sin(cycle) * 10
    if cycle < 25:  return 30 + math.sin(cycle * 2) * 15
    if cycle < 35:  return max(0, 20 - (cycle - 25) * 5)
    if cycle < 40:  return 0
    if cycle < 50:  return 50 + math.sin(cycle) * 10
    if cycle < 55:  return 35
    return max(0, 10 - (cycle - 55) * 3)

def _demo_gear(speed: float) -> str:
    if speed < 1:   return "N"
    if speed < 20:  return "1"
    if speed < 40:  return "2"
    if speed < 65:  return "3"
    if speed < 90:  return "4"
    if speed < 120: return "5"
    return "6"