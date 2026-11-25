# ============================================================
#  can_visualizer.py — Visualiseur CAN Bus PyGame
#  Opel Corsa — Vue du dessus, layout épuré
# ============================================================
import sys
import math
import pygame

from config import *
from can_data     import CANData
from car_renderer import OpelCorsaRenderer
from gauges       import ArcGauge, BarGauge, WarningLight, GearDisplay


# ================================================================
#  Panneau signaux (droite) — liste clé/valeur
# ================================================================
class SignalListPanel:
    def __init__(self, surface, rect):
        self.surface = surface
        self.rect    = rect
        self._font   = pygame.font.SysFont("monospace", 13)
        self._fhdr   = pygame.font.SysFont("monospace", 13, bold=True)

    def draw(self, signals: dict):
        pygame.draw.rect(self.surface, COLOR_PANEL, self.rect, border_radius=10)
        pygame.draw.rect(self.surface, (0, 180, 90), self.rect, 1, border_radius=10)

        hdr = self._fhdr.render("SIGNAUX CAN", True, COLOR_ACCENT)
        self.surface.blit(hdr, (self.rect.x + self.rect.width//2 - hdr.get_width()//2,
                                 self.rect.y + 8))
        pygame.draw.line(self.surface, (0,100,50),
                         (self.rect.x+10, self.rect.y+28),
                         (self.rect.right-10, self.rect.y+28), 1)

        y  = self.rect.y + 36
        lh = 19
        for key, val in signals.items():
            if y + lh > self.rect.bottom - 4:
                break
            # Clé
            k = self._font.render(key, True, COLOR_TEXT_DIM)
            self.surface.blit(k, (self.rect.x + 10, y))
            # Valeur
            if isinstance(val, bool):
                vs    = "ON" if val else "—"
                vcol  = COLOR_ACCENT if val else (60, 60, 80)
            elif isinstance(val, float):
                vs   = f"{val:.1f}"
                vcol = COLOR_TEXT
            else:
                vs   = str(val)
                vcol = COLOR_TEXT
            v = self._font.render(vs, True, vcol)
            self.surface.blit(v, (self.rect.right - v.get_width() - 10, y))
            # Séparateur léger
            pygame.draw.line(self.surface, (35, 35, 50),
                             (self.rect.x+10, y+lh-1),
                             (self.rect.right-10, y+lh-1), 1)
            y += lh


# ================================================================
#  Application principale
# ================================================================
class CANVisualizer:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)
        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        self.clock  = pygame.time.Clock()

        self.api = CANData()
        self.api.start()

        W, H = WINDOW_WIDTH, WINDOW_HEIGHT

        # ── Zones de layout ──────────────────────────────────────
        #  |  GAUCHE 200px  |  CENTRE 780px  |  DROITE 220px  |  SIGNAUX 200px  |
        LEFT_W   = 200
        RIGHT_W  = 200
        SIG_W    = 200
        CAR_X    = LEFT_W + (W - LEFT_W - RIGHT_W - SIG_W) // 2
        CAR_Y    = H // 2 + 20

        # ── Voiture (grande) ────────────────────────────────────
        self.car = OpelCorsaRenderer(self.screen,
                                     x=CAR_X, y=CAR_Y, scale=2.1)

        # ── Jauges arc (gauche : RPM / droite : Vitesse) ────────
        r = 88
        self.gauge_rpm   = ArcGauge(self.screen, LEFT_W//2, 130, r,
                                    "RÉGIME", 0, 7000, 6000, "tr/min",
                                    color_ok=(220, 80, 60), color_warn=COLOR_WARN)
        self.gauge_speed = ArcGauge(self.screen,
                                    W - RIGHT_W - SIG_W + RIGHT_W//2, 130, r,
                                    "VITESSE", 0, 220, 180, "km/h")

        # ── Jauges barres (gauche) ───────────────────────────────
        bw, bh = LEFT_W - 24, 20
        bx = 12
        self.bar_throttle = BarGauge(self.screen, bx, 280, bw, bh,
                                     "ACCÉLÉRATEUR", 0, 100, 90, "%")
        self.bar_temp     = BarGauge(self.screen, bx, 330, bw, bh,
                                     "TEMP MOTEUR",  40, 130, 105, "°C",
                                     color_ok=COLOR_ACCENT)
        self.bar_fuel     = BarGauge(self.screen, bx, 380, bw, bh,
                                     "CARBURANT",    0,  100, 15, "%",
                                     invert_warn=True)

        # ── Jauges barres (droite) ───────────────────────────────
        bx_r = W - RIGHT_W - SIG_W + 12
        self.bar_oil      = BarGauge(self.screen, bx_r, 280, bw, bh,
                                     "HUILE",     0,   8, 1.0, "bar",
                                     invert_warn=True)
        self.bar_battery  = BarGauge(self.screen, bx_r, 330, bw, bh,
                                     "BATTERIE",  10,  15, 11.5, "V",
                                     invert_warn=True)
        self.bar_otemp    = BarGauge(self.screen, bx_r, 380, bw, bh,
                                     "TEMP EXT.", -20, 50, 40, "°C",
                                     color_ok=(80, 160, 255))

        # ── Rapport de boîte (centre bas) ───────────────────────
        self.gear_disp = GearDisplay(self.screen, CAR_X, H - 55)

        # ── Voyants (rangée basse centre) ───────────────────────
        lights_y  = H - 130
        lights_cx = CAR_X
        gap       = 58
        offsets   = [-3, -2, -1, 0, 1, 2, 3]
        keys      = ["turn_left","turn_right","brake","handbrake","abs","esp","door_fl"]
        labels    = ["◀ LEFT","RIGHT ▶","BRAKE","HBRK","ABS","ESP","DOOR"]
        colors    = [(255,140,0),(255,140,0),(220,30,30),(220,30,30),
                     COLOR_WARN, COLOR_WARN,(255,200,0)]
        blinks    = [True, True, False, False, False, False, False]

        self.lights = {}
        for i, (key, lbl, col, blk) in enumerate(zip(keys, labels, colors, blinks)):
            lx = lights_cx + offsets[i] * gap - 20
            self.lights[key] = WarningLight(self.screen, lx, lights_y,
                                            lbl, color_on=col, blink=blk)

        # ── Panneau signaux (colonne droite) ────────────────────
        self.signal_panel = SignalListPanel(
            self.screen,
            pygame.Rect(W - SIG_W, 30, SIG_W - 4, H - 60))

        # ── Police statut ────────────────────────────────────────
        self._font_status = pygame.font.SysFont("monospace", 12)
        self._font_title  = pygame.font.SysFont("sans-serif", 17, bold=True)

    # ------------------------------------------------------------------
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._quit()

            signals = self.api.get_all()
            self._update(signals, dt)
            self._draw(signals, dt)
            pygame.display.flip()

    # ------------------------------------------------------------------
    def _update(self, signals: dict, dt: float):
        self.car.update(dt)

        self.gauge_rpm.set_value(signals.get("rpm", 0));    self.gauge_rpm.update()
        self.gauge_speed.set_value(signals.get("speed", 0)); self.gauge_speed.update()

        self.bar_throttle.set_value(signals.get("throttle", 0));    self.bar_throttle.update()
        self.bar_temp.set_value(signals.get("engine_temp", 40));    self.bar_temp.update()
        self.bar_fuel.set_value(signals.get("fuel_level", 0));      self.bar_fuel.update()
        self.bar_oil.set_value(signals.get("oil_pressure", 0));     self.bar_oil.update()
        self.bar_battery.set_value(signals.get("battery", 12));     self.bar_battery.update()
        self.bar_otemp.set_value(signals.get("outside_temp", 20));  self.bar_otemp.update()

        self.gear_disp.set_gear(signals.get("gear", "N"))

        for key, light in self.lights.items():
            light.set_state(signals.get(key, False))
            light.update(dt)

    # ------------------------------------------------------------------
    def _draw(self, signals: dict, dt: float):
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        self.screen.fill(COLOR_BG)

        self._draw_grid()
        self._draw_separators()

        # Voiture
        self.car.draw(signals)

        # Jauges arc
        self.gauge_rpm.draw()
        self.gauge_speed.draw()

        # Barres gauche
        self.bar_throttle.draw()
        self.bar_temp.draw()
        self.bar_fuel.draw()

        # Barres droite
        self.bar_oil.draw()
        self.bar_battery.draw()
        self.bar_otemp.draw()

        # Rapport
        self.gear_disp.draw()

        # Voyants
        for light in self.lights.values():
            light.draw()

        # Signaux
        self.signal_panel.draw(signals)

        # Titre + statut
        self._draw_header()
        self._draw_status(signals)

    # ------------------------------------------------------------------
    def _draw_grid(self):
        """Grille de fond subtile style blueprint."""
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        grid_col = (22, 32, 26)
        step = 30
        for x in range(0, W, step):
            pygame.draw.line(self.screen, grid_col, (x, 0), (x, H), 1)
        for y in range(0, H, step):
            pygame.draw.line(self.screen, grid_col, (0, y), (W, y), 1)

    def _draw_separators(self):
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        col  = (40, 60, 48)
        lw   = 1
        LEFT_W = 200
        SIG_W  = 200
        RIGHT_W= 200
        # Colonnes
        pygame.draw.line(self.screen, col, (LEFT_W, 10), (LEFT_W, H-30), lw)
        pygame.draw.line(self.screen, col, (W-RIGHT_W-SIG_W, 10), (W-RIGHT_W-SIG_W, H-30), lw)
        pygame.draw.line(self.screen, col, (W-SIG_W, 10), (W-SIG_W, H-30), lw)
        # Horizontaux gauche/droite (sous jauges arc)
        pygame.draw.line(self.screen, col, (10, 238), (LEFT_W-10, 238), lw)
        pygame.draw.line(self.screen, col, (W-RIGHT_W-SIG_W+10, 238), (W-SIG_W-10, 238), lw)

    def _draw_header(self):
        W = WINDOW_WIDTH
        t = self._font_title.render("OPEL CORSA  ·  CAN BUS VISUALIZER", True, COLOR_ACCENT)
        pygame.draw.rect(self.screen, (14, 22, 18),
                         pygame.Rect(0, 0, W, 26))
        self.screen.blit(t, (W//2 - t.get_width()//2, 4))

    def _draw_status(self, signals):
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        pygame.draw.rect(self.screen, (14, 22, 18), pygame.Rect(0, H-22, W, 22))
        pygame.draw.line(self.screen, (40,60,48), (0, H-22), (W, H-22), 1)
        f = self._font_status
        items = [
            (f"● DEMO", COLOR_WARN, 8),
            (f"SPD {signals.get('speed',0):.0f} km/h", COLOR_TEXT_DIM, 100),
            (f"RPM {signals.get('rpm',0):.0f}", COLOR_TEXT_DIM, 220),
            (f"T° {signals.get('engine_temp',0):.0f}°C", COLOR_TEXT_DIM, 330),
            (f"FUEL {signals.get('fuel_level',0):.0f}%", COLOR_TEXT_DIM, 430),
            (f"ESC: quitter", (50,70,55), W-130),
            (f"FPS {self.clock.get_fps():.0f}", COLOR_TEXT_DIM, W-50),
        ]
        for txt, col, x in items:
            s = f.render(txt, True, col)
            self.screen.blit(s, (x, H-18))

    # ------------------------------------------------------------------
    def _quit(self):
        self.api.stop()
        pygame.quit()
        sys.exit()


# ================================================================
if __name__ == "__main__":
    app = CANVisualizer()
    app.run()