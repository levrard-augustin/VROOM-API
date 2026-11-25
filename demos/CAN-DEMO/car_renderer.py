# ============================================================
#  car_renderer.py — Opel Corsa vue du dessus (style plan technique)
# ============================================================
import pygame
import math
from config import *

# Palette plan technique
_LINE     = (0, 220, 120)      # vert néon — contours principaux
_LINE_DIM = (0, 120, 70)       # vert sombre — détails intérieurs
_FILL     = (10, 32, 20)       # fond carrosserie
_FILL_CAB = (8,  26, 16)       # fond habitacle (légèrement différent)
_GLASS    = (20, 55, 45)       # vitres
_WHEEL_F  = (5,  18, 12)       # pneu rempli
_WHITE    = (220, 220, 220)    # bandes blanches
_ORANGE   = (255, 140, 0)      # clignotants allumés
_ORANGE_D = (60,  35,  0)      # clignotants éteints
_RED_ON   = (255,  30, 30)     # freins / feux allumés
_RED_OFF  = (80,   0,  0)      # feux éteints
_AMBER    = (255, 200,  0)     # phares
_DOOR_OPEN= (255, 160,  0)     # porte ouverte


class OpelCorsaRenderer:
    """
    Vue du dessus façon blueprint / plan technique.
    Rendu vectoriel pur PyGame — traits propres, remplissages sombres.
    Voiture orientée vers le HAUT (avant = haut de l'écran).
    """

    def __init__(self, surface: pygame.Surface, x: int, y: int,
                 scale: float = 1.0):
        self.surface  = surface
        self.x        = x        # centre X
        self.y        = y        # centre Y
        self.scale    = scale
        self._anim_t  = 0.0

    def update(self, dt: float):
        self._anim_t += dt

    def draw(self, signals: dict):
        s  = self.scale
        cx = self.x
        cy = self.y

        self._draw_body(cx, cy, s)
        self._draw_stripes(cx, cy, s)
        self._draw_windows(cx, cy, s)
        self._draw_wheels(cx, cy, s, signals)
        self._draw_lights(cx, cy, s, signals)
        self._draw_details(cx, cy, s)
        self._draw_doors(cx, cy, s, signals)
        self._draw_annotations(cx, cy, s, signals)

    # ------------------------------------------------------------------
    # Carrosserie — silhouette Corsa 3 portes vue du dessus
    # ------------------------------------------------------------------
    def _draw_body(self, cx, cy, s):
        # Silhouette extérieure (avant en haut)
        # x = gauche/droite, y = avant(−)/arrière(+)
        body = _pts(cx, cy, s, [
            # avant gauche arrondi
            (-40,  -95),
            (-18, -105),   # museau avant gauche
            (  0, -108),   # pointe capot
            ( 18, -108),
            ( 40,  -95),
            # flanc droit avant → arrière
            ( 52,  -80),
            ( 56,  -40),
            ( 56,   55),
            ( 50,   80),
            ( 38,   95),   # coin arrière droit
            # hayon arrière
            ( 20,  100),
            (  0,  102),
            (-20,  100),
            (-38,   95),
            (-50,   80),
            (-56,   55),
            (-56,  -40),
            (-52,  -80),
        ])
        pygame.draw.polygon(self.surface, _FILL, body)
        pygame.draw.polygon(self.surface, _LINE, body, _lw(s, 2))

    # ------------------------------------------------------------------
    # Bandes blanches (2 traits longitudinaux)
    # ------------------------------------------------------------------
    def _draw_stripes(self, cx, cy, s):
        lw = _lw(s, 3)
        for dx in (-14, 14):
            p1 = (int(cx + dx*s), int(cy - 90*s))
            p2 = (int(cx + dx*s), int(cy + 90*s))
            pygame.draw.line(self.surface, _WHITE, p1, p2, lw)

    # ------------------------------------------------------------------
    # Vitres
    # ------------------------------------------------------------------
    def _draw_windows(self, cx, cy, s):
        # Pare-brise avant
        pw = _pts(cx, cy, s, [
            (-34, -62), ( 34, -62),
            ( 30, -85), (-30, -85),
        ])
        pygame.draw.polygon(self.surface, _GLASS, pw)
        pygame.draw.polygon(self.surface, _LINE_DIM, pw, _lw(s, 1))

        # Lunette arrière
        rw = _pts(cx, cy, s, [
            (-30,  65), ( 30,  65),
            ( 26,  88), (-26,  88),
        ])
        pygame.draw.polygon(self.surface, _GLASS, rw)
        pygame.draw.polygon(self.surface, _LINE_DIM, rw, _lw(s, 1))

        # Vitres latérales avant
        for sign in (-1, 1):
            wl = _pts(cx, cy, s, [
                (sign*36, -62), (sign*52, -55),
                (sign*52, -20), (sign*36, -20),
            ])
            pygame.draw.polygon(self.surface, _GLASS, wl)
            pygame.draw.polygon(self.surface, _LINE_DIM, wl, _lw(s, 1))

        # Vitres latérales arrière
        for sign in (-1, 1):
            wl = _pts(cx, cy, s, [
                (sign*36,  20), (sign*52,  20),
                (sign*52,  55), (sign*36,  55),
            ])
            pygame.draw.polygon(self.surface, _GLASS, wl)
            pygame.draw.polygon(self.surface, _LINE_DIM, wl, _lw(s, 1))

        # Ligne de toit (contour habitacle)
        cab = _pts(cx, cy, s, [
            (-34, -62), ( 34, -62),
            ( 36,  65), (-36,  65),
        ])
        pygame.draw.polygon(self.surface, (0,0,0,0), cab, 0)
        pygame.draw.polygon(self.surface, _LINE_DIM, cab, _lw(s, 1))

    # ------------------------------------------------------------------
    # Roues (4 roues, animation rotation)
    # ------------------------------------------------------------------
    def _draw_wheels(self, cx, cy, s, signals):
        speed     = signals.get("speed", 0)
        angle     = self._anim_t * speed * 3.0   # rotation visuelle

        positions = [
            (-52, -72),   # avant gauche
            ( 52, -72),   # avant droit
            (-52,  72),   # arrière gauche
            ( 52,  72),   # arrière droit
        ]
        for (dx, dy) in positions:
            wx = int(cx + dx*s)
            wy = int(cy + dy*s)
            rw = int(11*s)   # demi-largeur pneu
            rh = int(22*s)   # demi-hauteur pneu

            # Pneu (rectangle arrondi)
            tire_rect = pygame.Rect(wx - rw, wy - rh, rw*2, rh*2)
            pygame.draw.rect(self.surface, _WHEEL_F,  tire_rect, border_radius=int(4*s))
            pygame.draw.rect(self.surface, _LINE,     tire_rect, _lw(s, 1), border_radius=int(4*s))

            # Jante (ellipse)
            pygame.draw.ellipse(self.surface, (30,30,40),
                                (wx - int(7*s), wy - int(14*s),
                                 int(14*s), int(28*s)))
            pygame.draw.ellipse(self.surface, _LINE_DIM,
                                (wx - int(7*s), wy - int(14*s),
                                 int(14*s), int(28*s)), _lw(s, 1))

            # Rayon central (animé)
            a_rad = math.radians(angle)
            for i in range(4):
                ai = a_rad + i * math.pi / 2
                x1 = int(wx + math.cos(ai) * 3*s)
                y1 = int(wy + math.sin(ai) * 3*s)
                x2 = int(wx + math.cos(ai) * 11*s)
                y2 = int(wy + math.sin(ai) * 11*s)
                pygame.draw.line(self.surface, _LINE_DIM, (x1,y1), (x2,y2), 1)

    # ------------------------------------------------------------------
    # Phares, feux arrière, clignotants
    # ------------------------------------------------------------------
    def _draw_lights(self, cx, cy, s, signals):
        brake = signals.get("brake", False)
        tl    = signals.get("turn_left",  False)
        tr    = signals.get("turn_right", False)

        # ── Phares avant (gauche & droit) ──
        for sign in (-1, 1):
            lx = int(cx + sign*30*s)
            ly = int(cy - 103*s)
            pygame.draw.ellipse(self.surface, _AMBER,
                                (lx - int(10*s), ly - int(5*s),
                                 int(20*s), int(10*s)))
            pygame.draw.ellipse(self.surface, _LINE,
                                (lx - int(10*s), ly - int(5*s),
                                 int(20*s), int(10*s)), _lw(s, 1))

        # ── Feux arrière ──
        for sign in (-1, 1):
            lx = int(cx + sign*28*s)
            ly = int(cy + 97*s)
            col = _RED_ON if brake else _RED_OFF
            pygame.draw.ellipse(self.surface, col,
                                (lx - int(10*s), ly - int(5*s),
                                 int(20*s), int(10*s)))
            pygame.draw.ellipse(self.surface, _LINE,
                                (lx - int(10*s), ly - int(5*s),
                                 int(20*s), int(10*s)), _lw(s, 1))

        # ── Clignotant avant gauche ──
        col = _ORANGE if tl else _ORANGE_D
        pygame.draw.rect(self.surface, col,
                         (int(cx - 48*s), int(cy - 100*s),
                          int(10*s), int(8*s)), border_radius=2)

        # ── Clignotant avant droit ──
        col = _ORANGE if tr else _ORANGE_D
        pygame.draw.rect(self.surface, col,
                         (int(cx + 38*s), int(cy - 100*s),
                          int(10*s), int(8*s)), border_radius=2)

        # ── Clignotant arrière gauche ──
        col = _ORANGE if tl else _ORANGE_D
        pygame.draw.rect(self.surface, col,
                         (int(cx - 48*s), int(cy + 93*s),
                          int(10*s), int(8*s)), border_radius=2)

        # ── Clignotant arrière droit ──
        col = _ORANGE if tr else _ORANGE_D
        pygame.draw.rect(self.surface, col,
                         (int(cx + 38*s), int(cy + 93*s),
                          int(10*s), int(8*s)), border_radius=2)

    # ------------------------------------------------------------------
    # Détails intérieurs (sièges, volant, ligne centrale)
    # ------------------------------------------------------------------
    def _draw_details(self, cx, cy, s):
        lw1 = _lw(s, 1)

        # Ligne centrale longitudinale (axe)
        pygame.draw.line(self.surface, _LINE_DIM,
                         (int(cx), int(cy - 100*s)),
                         (int(cx), int(cy +  98*s)), lw1)

        # Ligne centrale latérale (milieu habitacle)
        pygame.draw.line(self.surface, _LINE_DIM,
                         (int(cx - 54*s), int(cy)),
                         (int(cx + 54*s), int(cy)), lw1)

        # Volant
        vx, vy = int(cx - 14*s), int(cy - 28*s)
        r_vol = int(10*s)
        pygame.draw.circle(self.surface, _FILL,     (vx, vy), r_vol)
        pygame.draw.circle(self.surface, _LINE_DIM, (vx, vy), r_vol, lw1)
        pygame.draw.circle(self.surface, _LINE_DIM, (vx, vy), int(4*s), lw1)
        # rayons volant
        for a in (0, 90, 180, 270):
            a_r = math.radians(a)
            pygame.draw.line(self.surface, _LINE_DIM,
                             (int(vx + math.cos(a_r)*4*s), int(vy + math.sin(a_r)*4*s)),
                             (int(vx + math.cos(a_r)*9*s), int(vy + math.sin(a_r)*9*s)), lw1)

        # Sièges (4 rectangles arrondis)
        seat_defs = [
            (-18, -35, 16, 22),   # conducteur avant
            ( 2,  -35, 16, 22),   # passager avant
            (-22,  20, 14, 22),   # arrière gauche
            (  8,  20, 14, 22),   # arrière droit
        ]
        for (sdx, sdy, sw, sh) in seat_defs:
            r = pygame.Rect(int(cx + sdx*s), int(cy + sdy*s),
                            int(sw*s), int(sh*s))
            pygame.draw.rect(self.surface, (14, 40, 28), r, border_radius=int(3*s))
            pygame.draw.rect(self.surface, _LINE_DIM, r, lw1, border_radius=int(3*s))

        # Rétroviseurs extérieurs
        for sign in (-1, 1):
            mir = _pts(cx, cy, s, [
                (sign*52, -52), (sign*64, -48),
                (sign*64, -38), (sign*52, -38),
            ])
            pygame.draw.polygon(self.surface, _FILL, mir)
            pygame.draw.polygon(self.surface, _LINE, mir, lw1)

        # Calandre avant
        pygame.draw.rect(self.surface, _LINE_DIM,
                         (int(cx - 22*s), int(cy - 107*s),
                          int(44*s), int(5*s)), border_radius=2)

        # Séparation portes avant/arrière
        for sign in (-1, 1):
            pygame.draw.line(self.surface, _LINE_DIM,
                             (int(cx + sign*56*s), int(cy - 18*s)),
                             (int(cx + sign*36*s), int(cy - 18*s)), lw1)

    # ------------------------------------------------------------------
    # Portes ouvertes
    # ------------------------------------------------------------------
    def _draw_doors(self, cx, cy, s, signals):
        doors = {
            "door_fl": (-56, -40, -1),   # x, y, côté (-1=gauche)
            "door_fr": ( 56, -40,  1),
            "door_rl": (-56,  20, -1),
            "door_rr": ( 56,  20,  1),
        }
        for key, (dx, dy, side) in doors.items():
            if signals.get(key, False):
                # Arc représentant la porte ouverte (~45°)
                px = int(cx + dx*s)
                py = int(cy + dy*s)
                r  = int(30*s)
                start_a = math.radians(90) if side < 0 else math.radians(90)
                pygame.draw.arc(self.surface, _DOOR_OPEN,
                                (px - r, py - r, r*2, r*2),
                                math.radians(90), math.radians(135), _lw(s, 2))
                # Petite étiquette
                f = pygame.font.SysFont("monospace", int(max(8, 9*s)), bold=True)
                t = f.render("!", True, _DOOR_OPEN)
                self.surface.blit(t, (px + int(side*18*s), py - int(8*s)))

    # ------------------------------------------------------------------
    # Annotations : vitesse sur le plan
    # ------------------------------------------------------------------
    def _draw_annotations(self, cx, cy, s, signals):
        speed = signals.get("speed", 0)
        # Flèche de direction (si en mouvement)
        if speed > 2:
            arrow_len = int(min(40, 10 + speed * 0.2) * s)
            ax = int(cx)
            ay = int(cy - 108*s)
            # trait
            pygame.draw.line(self.surface, (0, 255, 140),
                             (ax, ay), (ax, ay - arrow_len), _lw(s, 2))
            # tête de flèche
            pygame.draw.polygon(self.surface, (0, 255, 140), [
                (ax,          ay - arrow_len - int(8*s)),
                (ax - int(5*s), ay - arrow_len),
                (ax + int(5*s), ay - arrow_len),
            ])


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _pts(cx, cy, s, coords):
    """Convertit une liste de (dx, dy) en points absolus scalés."""
    return [(int(cx + dx*s), int(cy + dy*s)) for dx, dy in coords]

def _lw(s, base):
    """Épaisseur de ligne minimale 1px."""
    return max(1, int(base * s))