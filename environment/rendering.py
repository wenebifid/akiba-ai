import os, sys
import pygame
import numpy as np

BG     = (12, 18, 30)
CARD   = (20, 30, 50)
GOLD   = (255, 193, 7)
GREEN  = (56, 196, 128)
RED    = (220, 80, 80)
BLUE   = (64, 148, 255)
ORANGE = (255, 140, 60)
TEAL   = (0, 200, 180)
WHITE  = (235, 240, 255)
GRAY   = (100, 115, 140)
LIGHT  = (160, 175, 200)
PURPLE = (160, 100, 240)

ACTION_COLORS = [BLUE, GREEN, ORANGE, RED, TEAL, PURPLE, GOLD, GRAY]
ACTION_NAMES  = [
    "Conservative Save", "Balanced Allocate", "Aggressive Invest",
    "Debt Repayment", "Emergency Fund", "Education & Skills",
    "Mobile Money Save", "Survival Mode",
]


class FinanceRenderer:
    W, H = 1100, 720

    def __init__(self, headless=False):
        self.headless = headless
        if not pygame.get_init():
            pygame.init()
        if headless:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            self.screen = pygame.Surface((self.W, self.H))
        else:
            self.screen = pygame.display.set_mode((self.W, self.H))
            pygame.display.set_caption("Akiba AI — Financial Stability Simulation")
        self.clock   = pygame.time.Clock()
        self.history = []
        self.actions = []
        try:
            self.fn = pygame.font.SysFont("dejavusans", 14)
            self.fb = pygame.font.SysFont("dejavusans", 18, bold=True)
            self.fs = pygame.font.SysFont("dejavusans", 11)
        except Exception:
            self.fn = pygame.font.Font(None, 16)
            self.fb = pygame.font.Font(None, 20)
            self.fs = pygame.font.Font(None, 13)

    def _txt(self, s, text, pos, font, color=WHITE, center=False):
        surf = font.render(str(text), True, color)
        r    = surf.get_rect()
        if center:
            r.center = pos
        else:
            r.topleft = pos
        s.blit(surf, r)

    def _bar(self, s, x, y, w, h, ratio, color):
        pygame.draw.rect(s, (30, 40, 60), (x, y, w, h), border_radius=4)
        fw = int(np.clip(ratio, 0, 1) * w)
        if fw > 0:
            pygame.draw.rect(s, color, (x, y, fw, h), border_radius=4)

    def _spark(self, s, hist, x, y, w, h, color):
        if len(hist) < 2:
            return
        mn, mx = min(hist), max(hist)
        rng    = max(mx - mn, 1)
        pts    = [
            (x + int(i * w / len(hist[-w:])), y + h - int((v - mn) / rng * h))
            for i, v in enumerate(hist[-w:])
        ]
        if len(pts) >= 2:
            pygame.draw.lines(s, color, False, pts, 2)

    def render(self, info, step, allocs, action=None, reward=None):
        self.history.append(info.get("net_worth", 0))
        if action is not None:
            self.actions.append(action)

        s = self.screen
        s.fill(BG)

        # Header
        pygame.draw.rect(s, CARD, (0, 0, self.W, 65))
        self._txt(s, "Akiba AI — East Africa Financial Stability Agent", (20, 12), self.fb, GOLD)
        self._txt(s, f"Month {step}/60  |  Net Worth: ${info.get('net_worth', 0):,.0f}  |  Income: ${info.get('income', 0):.0f}/mo",
                  (20, 38), self.fn, LIGHT)
        if info.get("economic_shock"):
            pygame.draw.rect(s, (180, 20, 20), (self.W // 2 - 140, 8, 280, 48), border_radius=8)
            self._txt(s, "ECONOMIC SHOCK ACTIVE", (self.W // 2, 32), self.fb, WHITE, center=True)

        # Left panel — financial bars
        px, py, pw = 15, 80, 330
        pygame.draw.rect(s, CARD, (px, py, pw, 580), border_radius=10)
        self._txt(s, "FINANCIAL STATUS", (px + 12, py + 12), self.fb, GOLD)

        items = [
            ("Income",     info.get("income", 0) / 120,      GREEN,  f"${info.get('income', 0):.0f}"),
            ("Savings",    info.get("savings", 0) / 500,     BLUE,   f"${info.get('savings', 0):.0f}"),
            ("Investment", info.get("investment_value", 0) / 1500, ORANGE, f"${info.get('investment_value', 0):.0f}"),
            ("Emergency",  info.get("emergency_fund", 0) / 200,    TEAL,   f"${info.get('emergency_fund', 0):.0f}"),
            ("Debt",       info.get("debt", 0) / 500,        RED,    f"${info.get('debt', 0):.0f}"),
        ]
        for i, (lbl, ratio, col, val) in enumerate(items):
            bx, by = px + 14, py + 50 + i * 72
            self._txt(s, lbl, (bx, by), self.fs, LIGHT)
            self._txt(s, val, (bx + 220, by), self.fs, col)
            self._bar(s, bx, by + 16, pw - 30, 20, ratio, col)

        st = info.get("financial_stress", 0)
        sc = GREEN if st < 0.4 else ORANGE if st < 0.7 else RED
        sy = py + 420
        self._txt(s, f"Stress: {st:.0%}", (px + 14, sy), self.fn, sc)
        self._bar(s, px + 14, sy + 18, pw - 30, 22, st, sc)
        self._txt(s, f"Inflation: {info.get('inflation_rate', 0):.1%}/yr", (px + 14, sy + 52), self.fn, ORANGE)

        # Center — current action
        cx, cy, cw = 360, 80, 360
        pygame.draw.rect(s, CARD, (cx, cy, cw, 280), border_radius=10)
        self._txt(s, "CURRENT STRATEGY", (cx + 12, cy + 12), self.fb, GOLD)
        if action is not None:
            ac = ACTION_COLORS[action]
            pygame.draw.rect(s, ac, (cx + 12, cy + 44, cw - 24, 52), border_radius=8, width=2)
            self._txt(s, ACTION_NAMES[action], (cx + cw // 2, cy + 70), self.fb, ac, center=True)
            al  = allocs.get(action, {})
            ay  = cy + 108
            cmap = {
                "savings": BLUE, "expenses": GRAY, "investments": ORANGE,
                "debt": RED, "emergency": TEAL, "education": PURPLE,
            }
            for k, col in cmap.items():
                v = al.get(k, 0)
                if v > 0:
                    self._bar(s, cx + 12, ay, (cw - 24) * v, 14, 1.0, col)
                    self._txt(s, f"{k} {v:.0%}", (cx + 14 + (cw - 24) * v + 4, ay), self.fs, col)
                    ay += 20
        if reward is not None:
            rc = GREEN if reward >= 0 else RED
            self._txt(s, f"Reward: {reward:+.2f}", (cx + 12, cy + 250), self.fn, rc)

        # Center — action legend
        lx, ly = 360, 375
        pygame.draw.rect(s, CARD, (lx, ly, cw, 290), border_radius=10)
        self._txt(s, "ACTION LEGEND", (lx + 12, ly + 12), self.fb, GOLD)
        for i, nm in enumerate(ACTION_NAMES):
            r2, c2 = i % 4, i // 4
            bx2 = lx + 12 + c2 * 172
            by2 = ly + 42 + r2 * 60
            ac  = ACTION_COLORS[i]
            if action == i:
                pygame.draw.rect(s, ac, (bx2, by2, 160, 50), border_radius=6, width=2)
            self._txt(s, f"{i}: {nm}", (bx2 + 6, by2 + 6), self.fs, ac)

        # Right panel — history charts
        rx, ry, rw = 735, 80, 350
        pygame.draw.rect(s, CARD, (rx, ry, rw, 580), border_radius=10)
        self._txt(s, "PERFORMANCE", (rx + 12, ry + 12), self.fb, GOLD)
        self._txt(s, "Net Worth History", (rx + 12, ry + 48), self.fs, LIGHT)
        pygame.draw.rect(s, (30, 40, 60), (rx + 12, ry + 66, rw - 24, 100), border_radius=4)
        self._spark(s, self.history, rx + 12, ry + 66, rw - 24, 100, GREEN)

        # Footer
        pygame.draw.rect(s, CARD, (0, self.H - 28, self.W, 28))
        self._txt(s, "Akiba AI  |  ALU Capstone 2025  |  Oyinwenebi Fiderikumo  |  Press Q to quit",
                  (self.W // 2, self.H - 14), self.fs, GRAY, center=True)

        if not self.headless:
            pygame.display.flip()
        self.clock.tick(10)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_q:
                pygame.quit()
                sys.exit()

    def close(self):
        pygame.quit()