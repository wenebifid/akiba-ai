import gymnasium as gym
import numpy as np
from gymnasium import spaces


class AfricanFinanceEnv(gym.Env):
    """
    AfricanFinanceEnv — calibrated to real East African economic data.

    Sources:
    - NISR Labour Force Survey 2023/2024: median income ~RWF 26,000/month (~$24 USD)
    - Rwanda CPI 2023 (NISR): annual inflation 19.79%
    - World Bank 2024: formal lending rate 15.72% annual
    - Allen et al. 2021: 6% monthly income shock probability
    - World Bank 2022: 55-75% of income spent on food
    """

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 10}

    ACTION_ALLOCATIONS = {
        0: {"savings": 0.60, "expenses": 0.30, "investments": 0.10, "debt": 0.00, "emergency": 0.00, "education": 0.00},
        1: {"savings": 0.30, "expenses": 0.40, "investments": 0.30, "debt": 0.00, "emergency": 0.00, "education": 0.00},
        2: {"savings": 0.10, "expenses": 0.30, "investments": 0.60, "debt": 0.00, "emergency": 0.00, "education": 0.00},
        3: {"savings": 0.10, "expenses": 0.30, "investments": 0.20, "debt": 0.40, "emergency": 0.00, "education": 0.00},
        4: {"savings": 0.20, "expenses": 0.30, "investments": 0.00, "debt": 0.00, "emergency": 0.50, "education": 0.00},
        5: {"savings": 0.40, "expenses": 0.40, "investments": 0.00, "debt": 0.00, "emergency": 0.00, "education": 0.20},
        6: {"savings": 0.30, "expenses": 0.40, "investments": 0.00, "debt": 0.00, "emergency": 0.00, "education": 0.00},
        7: {"savings": 0.20, "expenses": 0.70, "investments": 0.00, "debt": 0.00, "emergency": 0.10, "education": 0.00},
    }

    ACTION_NAMES = [
        "Conservative Save", "Balanced Allocate", "Aggressive Invest",
        "Debt Repayment", "Emergency Fund", "Education & Skills",
        "Mobile Money Save", "Survival Mode",
    ]

    def __init__(self, render_mode=None):
        super().__init__()
        self.render_mode        = render_mode
        self.max_income         = 120.0     # $120/month upper bound (lower formal sector)
        self.base_income        = 28.0      # $28/month — NISR 2023 median informal worker
        self.max_steps          = 60        # 5-year simulation
        self.inflation_base     = 0.18      # 18% annual — Rwanda CPI average 2022-2023
        self.investment_target  = 1500.0    # $1,500 realistic 5-year savings goal
        self.lending_rate       = 0.1572    # 15.72% annual — World Bank Rwanda 2024
        self.shock_prob         = 0.06      # 6% monthly — Allen et al. 2021
        self.expense_lo         = 0.55      # 55-75% on food — World Bank 2022
        self.expense_hi         = 0.75
        self.action_allocations = self.ACTION_ALLOCATIONS

        self.action_space = spaces.Discrete(8)
        self.observation_space = spaces.Box(
            low=np.zeros(9, dtype=np.float32),
            high=np.ones(9, dtype=np.float32),
            dtype=np.float32,
        )
        self.renderer = None
        self.reset()

    def _stress(self):
        return float(np.clip(
            0.4 * min(self.debt / (self.income * 12 + 1e-9), 1.0) +
            0.4 * max(0, 1 - self.savings / (self.income * 3 + 1e-9)) +
            0.2 * min(self.inflation_rate / 0.30, 1.0),
            0, 1
        ))

    def _obs(self):
        return np.array([
            np.clip(self.income / self.max_income, 0, 1),
            np.clip(self.savings / (self.income * 12 + 1e-9), 0, 1),
            np.clip(self.monthly_expenses / (self.income + 1e-9), 0, 1),
            np.clip(self.debt / (self.income * 12 + 1e-9), 0, 1),
            np.clip(self.inflation_rate / 0.30, 0, 1),
            np.clip(self.investment_value / self.investment_target, 0, 1),
            self.step_count / self.max_steps,
            float(self.shock_active),
            np.clip(self.financial_stress, 0, 1),
        ], dtype=np.float32)

    def _info(self):
        return {
            "income":           round(self.income, 2),
            "savings":          round(self.savings, 2),
            "debt":             round(self.debt, 2),
            "investment_value": round(self.investment_value, 2),
            "emergency_fund":   round(self.emergency_fund, 2),
            "inflation_rate":   round(self.inflation_rate, 4),
            "financial_stress": round(self.financial_stress, 4),
            "step":             self.step_count,
            "economic_shock":   self.shock_active,
            "monthly_expenses": round(self.monthly_expenses, 2),
            "net_worth":        round(
                self.savings + self.investment_value + self.emergency_fund - self.debt, 2
            ),
        }

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        rng = self.np_random
        self.income           = float(np.clip(self.base_income + rng.uniform(-8, 92), 10, self.max_income))
        self.savings          = rng.uniform(0, 30)
        self.debt             = rng.uniform(0, 150)
        self.investment_value = rng.uniform(0, 20)
        self.emergency_fund   = rng.uniform(0, 15)
        self.monthly_expenses = self.income * rng.uniform(self.expense_lo, self.expense_hi)
        self.inflation_rate   = float(np.clip(self.inflation_base + rng.uniform(-0.04, 0.08), 0.05, 0.30))
        self.shock_active     = False
        self.shock_dur        = 0
        self.pre_shock_income = self.income
        self.education_level  = 0.0
        self.step_count       = 0
        self.stable_streak    = 0
        self.cumulative_reward = 0.0
        self.financial_stress = self._stress()
        return self._obs(), self._info()

    def step(self, action):
        assert self.action_space.contains(action)
        alloc = self.ACTION_ALLOCATIONS[action]

        # Income growth (education slowly increases income)
        self.income = float(np.clip(
            self.income * (1 + 0.001 + self.education_level * 0.003), 10, self.max_income
        ))

        # Economic shock logic
        if not self.shock_active:
            if self.np_random.random() < self.shock_prob:
                self.shock_active     = True
                self.pre_shock_income = self.income
                self.shock_dur        = int(self.np_random.integers(1, 5))
                self.income           = float(np.clip(
                    self.income * self.np_random.uniform(0.3, 0.7), 5, self.max_income
                ))
                self.inflation_rate = float(np.clip(
                    self.inflation_rate + self.np_random.uniform(0.02, 0.06), 0.05, 0.30
                ))
        else:
            self.shock_dur -= 1
            if self.shock_dur <= 0:
                self.shock_active   = False
                self.income         = float(np.clip(
                    self.pre_shock_income * self.np_random.uniform(0.7, 1.0), 10, self.max_income
                ))
                self.inflation_rate = float(np.clip(
                    self.inflation_rate - 0.02, self.inflation_base, 0.30
                ))

        # Allocate income
        a = self.income
        savings_add   = a * alloc["savings"]
        expense_spend = a * alloc["expenses"]
        invest_add    = a * alloc["investments"]
        debt_pay      = a * alloc["debt"]
        emergency_add = a * alloc["emergency"]
        edu_add       = a * alloc["education"]

        # Action 6: Mobile Money — extra 40% into savings at MoMo rate (~6% annual)
        if action == 6:
            momo        = a * 0.40
            savings_add += momo * (1 + self.np_random.uniform(0.004, 0.005))

        # Update state
        self.savings          += savings_add
        self.emergency_fund   += emergency_add
        self.debt              = max(0.0, self.debt - debt_pay)
        self.education_level   = float(np.clip(self.education_level + edu_add / 2000, 0, 1))

        # Investment returns: mean 0.6%/month, std 3%
        inv_ret = float(np.clip(self.np_random.normal(0.006, 0.03), -0.12, 0.10))
        self.investment_value = max(0.0, self.investment_value * (1 + inv_ret) + invest_add)

        # Inflation erodes savings (~1.5%/month at 18% annual)
        self.savings = max(0.0, self.savings * (1 - self.inflation_rate / 12))

        # Cover expenses
        self.monthly_expenses = self.income * self.np_random.uniform(self.expense_lo, self.expense_hi)
        deficit = max(0.0, self.monthly_expenses - expense_spend)
        if deficit > 0:
            if self.savings >= deficit:
                self.savings -= deficit
            else:
                self.debt    += deficit - self.savings
                self.savings  = 0.0

        # Debt interest at 15.72% annual
        self.debt *= (1 + self.lending_rate / 12)

        # Financial stress
        self.financial_stress = self._stress()

        # Reward — scaled to real East African income ($28/month baseline)
        nw = self.savings + self.investment_value + self.emergency_fund - self.debt
        r = (
            float(np.tanh(nw / 300)) * 5.0
            - min(self.debt / 30, 3.0)
            + (1 - self.financial_stress) * 2.0
            + float(np.tanh(self.investment_value / self.investment_target)) * 3.0
            + (1.0 if self.emergency_fund >= self.monthly_expenses * 3 else -0.3)
            + (-5.0 if deficit > self.income * 0.30 else 0.0)
            + (1.0 if self.shock_active and self.savings > self.monthly_expenses else 0.0)
        )

        if self.financial_stress < 0.4:
            self.stable_streak += 1
            if self.stable_streak >= 6:
                r += 2.0
        else:
            self.stable_streak = 0

        self.step_count        += 1
        self.cumulative_reward += r

        # Terminal conditions
        terminated = False
        truncated  = False
        if self.debt > self.income * 36:
            terminated = True
            r -= 20.0
        if self.investment_value >= self.investment_target and self.debt < self.income:
            terminated = True
            r += 30.0
        if self.step_count >= self.max_steps:
            truncated = True

        return self._obs(), float(r), terminated, truncated, self._info()

    def render(self):
        if self.render_mode == "human":
            if self.renderer is None:
                import sys, os
                sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
                from environment.rendering import FinanceRenderer
                self.renderer = FinanceRenderer()
            self.renderer.render(self._info(), self.step_count, self.ACTION_ALLOCATIONS)

    def close(self):
        if self.renderer:
            self.renderer.close()
            self.renderer = None