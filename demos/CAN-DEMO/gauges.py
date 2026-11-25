# ============================================================
#  gauges.py — Jauges animées PyGame
# ============================================================
import pygame
import math
from config import *


class ArcGauge:
    """
    Jauge circulaire (tachymètre / vitesse).
    Affiche : arc coloré, aiguille, valeur numérique, label.
    """
    def __init__(self, surface: pygame.Surface, cx: int, cy: int,
                 radius: int, label: str,
                 min_val: float, max_val: float,
                 warn_val: float, unit: str,
                 start_angle: float = 225, sweep: float = 270,
                 color_ok = COLOR_GAUGE_FG,
                 color_warn = COLOR_WARN,
                 color_danger = COLOR_DANGER):
        self.surface     = surface
        self.cx, self.cy = cx, cy
        self.radius      = radius
        self.label       = label
        self.min_val     = min_val
        self.max_val     = max_val
        self.warn_val    = warn_val
        self.unit        = unit
        self.start_angle = start_angle   # degrés (0 = droite)
        self.sweep       = sweep         # degrés total
        self.color_ok    = color_ok
        self.color_warn  = color_warn
        self.color_danger= color_danger
        self._current    = min_val
        self._target     = min_val
        self._smoothing  = 0.15

        self._font_val   = pygame.font.SysFont("monospace", radius // 3, bold=True)
        self._font_label = pygame.font.SysFont("sans-serif", radius // 5)
        self._font_unit  = pygame.font.SysFont("sans-serif", radius // 6)

    def set_value(self, value: float):
        self._target = max(self.min_val, min(self.max_val, float(value)))

    def update(self):
        self._current += (self._target - self._current) * self._smoothing

    def draw(self):
        r      = self.radius
        val    = self._current
        ratio  = (val - self.min_val) / max(1, self.max_val - self.min_val)
        ratio  = max(0.0, min(1.0, ratio))

        # Fond
        pygame.draw.circle(self.surface, COLOR_GAUGE_BG, (self.cx, self.cy), r)
        pygame.draw.circle(self.surface, (50,50,70),     (self.cx, self.cy), r, 3)

        # Arc de fond
        self._draw_arc((60, 60, 80), 0.0, 1.0, r - 8, 16)

        # Arc coloré
        warn_r = (self.warn_val - self.min_val) / max(1, self.max_val - self.min_val)
        if ratio <= warn_r:
            self._draw_arc(self.color_ok, 0.0, ratio, r - 8, 16)
        else:
            self._draw_arc(self.color_ok,   0.0,    warn_r, r - 8, 16)
            self._draw_arc(self.color_warn, warn_r,  ratio,  r - 8, 16)
        if ratio > 0.95:
            self._draw_arc(self.color_danger, 0.95, ratio, r - 8, 16)

        # Graduation
        self._draw_ticks(r)

        # Aiguille
        needle_angle = math.radians(self.start_angle - ratio * self.sweep)
        nx = self.cx + (r - 22) * math.cos(needle_angle)
        ny = self.cy - (r - 22) * math.sin(needle_angle)
        pygame.draw.line(self.surface, (230, 80, 80),
                         (self.cx, self.cy), (int(nx), int(ny)), 3)
        pygame.draw.circle(self.surface, (200, 60, 60), (self.cx, self.cy), 7)

        # Valeur numérique
        txt = self._font_val.render(f"{val:.0f}", True, COLOR_TEXT)
        self.surface.blit(txt, (self.cx - txt.get_width()//2,
                                 self.cy + r//5))
        # Unité
        utxt = self._font_unit.render(self.unit, True, COLOR_TEXT_DIM)
        self.surface.blit(utxt, (self.cx - utxt.get_width()//2,
                                  self.cy + r//5 + txt.get_height()))
        # Label
        ltxt = self._font_label.render(self.label, True, COLOR_TEXT_DIM)
        self.surface.blit(ltxt, (self.cx - ltxt.get_width()//2,
                                  self.cy - r - ltxt.get_height() - 4))

    def _draw_arc(self, color, ratio_start, ratio_end, r, thickness):
        if ratio_end <= ratio_start:
            return
        a_start = self.start_angle - ratio_start * self.sweep
        a_end   = self.start_angle - ratio_end   * self.sweep
        # pygame.draw.arc : angles en radians, sens antihoraire
        rect = pygame.Rect(self.cx - r, self.cy - r, r*2, r*2)
        pygame.draw.arc(self.surface, color, rect,
                        math.radians(a_end),
                        math.radians(a_start), thickness)

    def _draw_ticks(self, r):
        n_major = 10
        n_minor = 5
        for i in range(n_major * n_minor + 1):
            ratio_t = i / (n_major * n_minor)
            angle   = math.radians(self.start_angle - ratio_t * self.sweep)
            is_major = (i % n_minor == 0)
            r_outer = r - 4
            r_inner = r_outer - (10 if is_major else 5)
            x1 = self.cx + r_outer * math.cos(angle)
            y1 = self.cy - r_outer * math.sin(angle)
            x2 = self.cx + r_inner * math.cos(angle)
            y2 = self.cy - r_inner * math.sin(angle)
            color = COLOR_TEXT if is_major else COLOR_TEXT_DIM
            pygame.draw.line(self.surface, color,
                             (int(x1), int(y1)), (int(x2), int(y2)),
                             2 if is_major else 1)
            if is_major:
                val_t = self.min_val + ratio_t * (self.max_val - self.min_val)
                f = pygame.font.SysFont("monospace", r//9)
                t = f.render(f"{val_t:.0f}", True, COLOR_TEXT_DIM)
                rx = self.cx + (r_inner - 14) * math.cos(angle) - t.get_width()//2
                ry = self.cy - (r_inner - 14) * math.sin(angle) - t.get_height()//2
                self.surface.blit(t, (int(rx), int(ry)))


class BarGauge:
    """Barre de progression horizontale ou verticale."""
    def __init__(self, surface: pygame.Surface,
                 x: int, y: int, width: int, height: int,
                 label: str, min_val: float, max_val: float,
                 warn_val: float, unit: str,
                 vertical: bool = False,
                 color_ok = COLOR_GAUGE_FG,
                 invert_warn: bool = False):
        self.surface    = surface
        self.rect       = pygame.Rect(x, y, width, height)
        self.label      = label
        self.min_val    = min_val
        self.max_val    = max_val
        self.warn_val   = warn_val
        self.unit       = unit
        self.vertical   = vertical
        self.color_ok   = color_ok
        self.invert_warn= invert_warn   # True = warn si EN DESSOUS de warn_val
        self._current   = min_val
        self._target    = min_val
        self._font      = pygame.font.SysFont("monospace", 14, bold=True)
        self._font_lbl  = pygame.font.SysFont("sans-serif", 12)

    def set_value(self, value: float):
        self._target = max(self.min_val, min(self.max_val, float(value)))

    def update(self):
        self._current += (self._target - self._current) * 0.12

    def draw(self):
        val    = self._current
        ratio  = (val - self.min_val) / max(1, self.max_val - self.min_val)
        ratio  = max(0.0, min(1.0, ratio))

        # Fond
        pygame.draw.rect(self.surface, COLOR_GAUGE_BG, self.rect, border_radius=6)
        pygame.draw.rect(self.surface, (50,50,70), self.rect, 2, border_radius=6)

        # Remplissage
        warn_r = (self.warn_val - self.min_val) / max(1, self.max_val - self.min_val)
        is_warn = (ratio <= warn_r) if self.invert_warn else (ratio >= warn_r)
        fill_color = COLOR_WARN if is_warn else self.color_ok

        if self.vertical:
            fill_h = int(self.rect.height * ratio)
            fill_rect = pygame.Rect(self.rect.x,
                                    self.rect.bottom - fill_h,
                                    self.rect.width, fill_h)
        else:
            fill_w = int(self.rect.width * ratio)
            fill_rect = pygame.Rect(self.rect.x, self.rect.y,
                                    fill_w, self.rect.height)

        if fill_rect.width > 0 and fill_rect.height > 0:
            pygame.draw.rect(self.surface, fill_color, fill_rect, border_radius=5)

        # Label + valeur
        lbl = self._font_lbl.render(self.label, True, COLOR_TEXT_DIM)
        val_txt = self._font.render(f"{val:.1f}{self.unit}", True, COLOR_TEXT)
        self.surface.blit(lbl,     (self.rect.x, self.rect.y - 18))
        self.surface.blit(val_txt, (self.rect.right - val_txt.get_width() - 4,
                                    self.rect.y - 18))


class DigitalDisplay:
    """
    Afficheur numérique style tableau de bord.
    Utilisé pour la vitesse (grand affichage), le compteur, etc.
    """
    def __init__(self, surface: pygame.Surface,
                 x: int, y: int, label: str, unit: str,
                 font_size: int = 48):
        self.surface = surface
        self.x, self.y = x, y
        self.label   = label
        self.unit    = unit
        self._font   = pygame.font.SysFont("monospace", font_size, bold=True)
        self._flbl   = pygame.font.SysFont("sans-serif", 14)
        self._funit  = pygame.font.SysFont("sans-serif", 18)
        self._current= 0.0
        self._target = 0.0

    def set_value(self, value: float):
        self._target = float(value)

    def update(self):
        self._current += (self._target - self._current) * 0.2

    def draw(self):
        lbl  = self._flbl.render(self.label, True, COLOR_TEXT_DIM)
        val  = self._font.render(f"{self._current:6.1f}", True, COLOR_ACCENT)
        unit = self._funit.render(self.unit, True, COLOR_TEXT_DIM)
        self.surface.blit(lbl,  (self.x, self.y))
        self.surface.blit(val,  (self.x, self.y + 16))
        self.surface.blit(unit, (self.x + val.get_width() + 4,
                                  self.y + 16 + val.get_height() - unit.get_height()))


class WarningLight:
    """Voyant lumineux (booléen) style tableau de bord."""
    def __init__(self, surface: pygame.Surface,
                 x: int, y: int, label: str,
                 color_on = COLOR_WARN,
                 color_off = (40, 40, 55),
                 blink: bool = False):
        self.surface   = surface
        self.x, self.y = x, y
        self.label     = label
        self.color_on  = color_on
        self.color_off = color_off
        self.blink     = blink
        self._state    = False
        self._font     = pygame.font.SysFont("sans-serif", 11)
        self._t        = 0.0

    def set_state(self, state: bool):
        self._state = bool(state)

    def update(self, dt: float):
        self._t += dt

    def draw(self):
        visible = self._state
        if self.blink and self._state:
            visible = (int(self._t * 2) % 2 == 0)

        color = self.color_on if visible else self.color_off
        pygame.draw.rect(self.surface, color,
                         (self.x, self.y, 40, 22), border_radius=4)
        pygame.draw.rect(self.surface, (60,60,80),
                         (self.x, self.y, 40, 22), 1, border_radius=4)
        if visible:
            glow = pygame.Surface((44, 26), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*color, 80), (0,0,44,26), border_radius=5)
            self.surface.blit(glow, (self.x-2, self.y-2))

        lbl = self._font.render(self.label, True, COLOR_TEXT_DIM)
        self.surface.blit(lbl, (self.x + 20 - lbl.get_width()//2,
                                 self.y + 24))


class GearDisplay:
    """Afficheur de rapport de boîte."""
    def __init__(self, surface: pygame.Surface, cx: int, cy: int):
        self.surface  = surface
        self.cx, self.cy = cx, cy
        self._font    = pygame.font.SysFont("monospace", 52, bold=True)
        self._font_lbl= pygame.font.SysFont("sans-serif", 13)
        self._gear    = "N"

    def set_gear(self, gear):
        self._gear = str(gear)

    def draw(self):
        color = COLOR_TEXT if self._gear not in ("N","R") else COLOR_WARN
        bg    = pygame.Rect(self.cx - 30, self.cy - 35, 60, 65)
        pygame.draw.rect(self.surface, COLOR_GAUGE_BG, bg, border_radius=10)
        pygame.draw.rect(self.surface, COLOR_ACCENT,   bg, 2, border_radius=10)
        t   = self._font.render(self._gear, True, color)
        lbl = self._font_lbl.render("GEAR", True, COLOR_TEXT_DIM)
        self.surface.blit(t,   (self.cx - t.get_width()//2,
                                 self.cy - t.get_height()//2 + 5))
        self.surface.blit(lbl, (self.cx - lbl.get_width()//2, self.cy + 33))