import os, sys, json
import numpy as np
from pathlib import Path

ROOT = Path(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, str(ROOT))

from utils.user_data import (
    SAVINGS_PRODUCTS, PROFESSIONS, rank_debts,
    monthly_interest_cost, months_to_goal,
    debt_payoff_months, recommend_savings_product, real_return,
)

RWF_PER_USD = 1370

ACTION_TRANSLATIONS = {
    0: {"en": "Save as much as possible this month",            "kiny": "Bika amafaranga menshi ku kwezi gukwiye",                    "sw": "Okoa iwezekanavyo mwezi huu"},
    1: {"en": "Balance your spending, saving, and investing",   "kiny": "Kerekanya amafaranga yo gusarura, kuzigama no guteza imbere", "sw": "Gawanya pesa kati ya matumizi, akiba, na uwekezaji"},
    2: {"en": "Invest aggressively — your safety net is ready", "kiny": "Teza imbere cyane — ufite ibihagije",                        "sw": "Wekeza kwa nguvu — una usalama wa kutosha"},
    3: {"en": "Focus on paying off your debt this month",       "kiny": "Iga kwishyura imyenda yawe uyu kwezi",                      "sw": "Zingatia kulipa madeni yako mwezi huu"},
    4: {"en": "Build your emergency fund first",                "kiny": "Banza wubake inguzanyo y'ivuka",                             "sw": "Jenga akiba ya dharura kwanza"},
    5: {"en": "Invest in your skills to increase future income","kiny": "Jya wize no gukurura imyanya myiza",                        "sw": "Wekeza katika ujuzi wako kupata mapato zaidi"},
    6: {"en": "Save via Mobile Money (MoMo / MoKash)",          "kiny": "Bika amafaranga kuri MTN MoMo cyangwa MoKash",              "sw": "Weka pesa kwenye Mobile Money (MoMo / MoKash)"},
    7: {"en": "Survival mode — cover basic needs only",         "kiny": "Gucika intege — fata ibihangange gusa uyu kwezi",           "sw": "Hali ya dharura — jaza mahitaji ya msingi tu"},
}

ACTION_EXPLAIN = {
    0: "Your finances are stable enough to save aggressively. Put 60% away before spending — this builds your foundation.",
    1: "A balanced approach: save a third, cover expenses, put a third into investments. Good for normal months.",
    2: "Your safety cushion is solid and debt is low. Now is the time to put money to work.",
    3: "Your debt is a burden. Paying it down now saves you money on interest and reduces stress.",
    4: "You don't have enough buffer. Build your emergency fund — it protects you from being forced to borrow.",
    5: "Investing in your skills will increase your income over time. A long-term play that pays off for years.",
    6: "Put money into MTN MoMo or Ejo Heza — safe, accessible, earning steady returns. Better than cash at home.",
    7: "A tough month. Cover basic needs first. This is temporary — stability comes before growth.",
}


def load_best_model():
    algo_map = {
        "PPO":       ("stable_baselines3", "PPO", ROOT / "models" / "pg" / "ppo"),
        "DQN":       ("stable_baselines3", "DQN", ROOT / "models" / "dqn"),
        "A2C":       ("stable_baselines3", "A2C", ROOT / "models" / "pg" / "a2c"),
        "REINFORCE": ("stable_baselines3", "A2C", ROOT / "models" / "pg" / "reinforce"),
    }
    best_algo, best_reward, best_info = None, -np.inf, None

    for algo, (module, cls, model_dir) in algo_map.items():
        for mp in [model_dir / "best_run.json", model_dir.parent / "best_run.json"]:
            if mp.exists():
                try:
                    m = json.loads(mp.read_text())
                    r = m.get("best_mean_reward", -np.inf)
                    if r > best_reward:
                        best_reward = r
                        best_algo   = algo
                        best_info   = (module, cls, model_dir, m.get("best_run_id", 1))
                except Exception:
                    pass

    if best_info is None:
        return None, None

    module, cls, model_dir, run_id = best_info
    import importlib
    Cls = getattr(importlib.import_module(module), cls)

    for p in [
        model_dir / f"run{run_id}" / "best_model",
        model_dir / f"run{run_id}" / "final_model",
        model_dir / "best_model",
    ]:
        if Path(str(p) + ".zip").exists():
            try:
                return Cls.load(str(p)), best_algo
            except Exception:
                pass

    return None, None


def build_obs(income_usd, savings_usd, debt_usd, investment_usd,
              emergency_usd, inflation, month_num, had_shock,
              max_income=120.0, inv_target=1500.0):
    debt_r   = min(debt_usd / (income_usd * 12 + 1e-9), 1.0)
    sav_gap  = max(0, 1 - savings_usd / (income_usd * 3 + 1e-9))
    inf_s    = min(inflation / 0.30, 1.0)
    stress   = float(np.clip(0.4 * debt_r + 0.4 * sav_gap + 0.2 * inf_s, 0, 1))

    obs = np.array([
        np.clip(income_usd / max_income, 0, 1),
        np.clip(savings_usd / (income_usd * 12 + 1e-9), 0, 1),
        0.65,
        np.clip(debt_usd / (income_usd * 12 + 1e-9), 0, 1),
        np.clip(inflation / 0.30, 0, 1),
        np.clip(investment_usd / inv_target, 0, 1),
        np.clip(month_num / 60, 0, 1),
        float(had_shock),
        stress,
    ], dtype=np.float32)

    return obs, stress


def rule_based(income, savings, debt, emergency, investment, had_shock, stress, month):
    if had_shock or income < 15:
        return 7
    if debt > income * 8:
        return 3
    if emergency < income * 2:
        return 4
    if stress > 0.70:
        return 0
    if investment > income * 6 and debt < income:
        return 2
    if savings < income * 1.5:
        return 6
    if month <= 6:
        return 4
    return 1


def shock_recovery_plan(income_rwf, savings_rwf, debt_rwf, emergency_rwf, severity, profession):
    buffer_months = emergency_rwf / max(income_rwf * 0.65, 1)
    lost_rwf      = income_rwf * severity
    can_survive   = buffer_months >= 1.0

    plan = {
        "severity":      "severe" if severity > 0.5 else "moderate",
        "buffer_months": round(buffer_months, 1),
        "can_survive":   can_survive,
        "borrow_advice": None,
        "months": [
            {"month": 1, "label": "Survive",   "focus": "Cover food and rent only. Pause savings. Use emergency fund if needed.", "action": 7},
            {"month": 2, "label": "Stabilize", "focus": "Income partially recovering. Restart small daily MoMo savings.", "action": 0},
            {"month": 3, "label": "Rebuild",   "focus": "Back to normal. Replenish emergency fund before resuming investments.", "action": 4},
        ],
    }

    if not can_survive:
        if debt_rwf < income_rwf * 3:
            plan["borrow_advice"] = {
                "should_borrow": True,
                "source":        "Umurenge SACCO",
                "reason":        f"Your emergency fund covers only {buffer_months:.1f} months. Borrow RWF {int(lost_rwf):,} from your SACCO at 24%/year — far cheaper than a moneylender's 120%+.",
                "warning":       "Do NOT borrow from informal moneylenders. A RWF 10,000 loan at 10%/month becomes RWF 31,000 in 12 months.",
                "amount_rwf":    int(lost_rwf * 1.5),
            }
        else:
            plan["borrow_advice"] = {
                "should_borrow": False,
                "reason":        "Existing debt is already high. Cut expenses to bare minimum instead of borrowing more.",
            }

    return plan


def debt_advice(debts, income_rwf):
    if not debts:
        return {"total_rwf": 0, "advice": [], "danger": False, "monthly_cost_rwf": 0}

    ranked  = rank_debts(debts)
    total   = sum(d.get("amount_rwf", 0) for d in debts)
    mc      = sum(monthly_interest_cost(d.get("amount_rwf", 0), d.get("rate_annual", 0)) for d in debts)
    danger  = any(d.get("rate_annual", 0) >= 0.60 for d in debts)
    advice  = []

    for d in ranked:
        amt    = d.get("amount_rwf", 0)
        rate   = d.get("rate_annual", 0)
        cost   = monthly_interest_cost(amt, rate)
        pay    = min(int(income_rwf * 0.30), int(amt / 6))
        months = debt_payoff_months(amt, pay, rate)
        advice.append({
            "name":                     d.get("source", "Debt"),
            "amount_rwf":               int(amt),
            "rate_annual":              rate,
            "rate_pct":                 f"{rate * 100:.0f}%",
            "monthly_cost_rwf":         int(cost),
            "recommended_payment_rwf":  pay,
            "months_to_payoff":         months,
            "priority":                 "PAY FIRST" if rate >= 0.60 else ("HIGH" if rate >= 0.20 else "NORMAL"),
            "danger":                   rate >= 0.60,
        })

    return {
        "total_rwf":        int(total),
        "monthly_cost_rwf": int(mc),
        "pct_of_income":    round(mc / max(income_rwf, 1) * 100, 1),
        "advice":           advice,
        "danger":           danger,
        "danger_message":   (
            f"You are paying RWF {int(mc):,}/month just in interest — "
            f"{round(mc / max(income_rwf, 1) * 100, 0):.0f}% of your income. "
            "Pay the highest-rate debt immediately."
        ) if danger else None,
    }


def full_recommendation(model, income_rwf, savings_rwf, debt_rwf, investment_rwf,
                        emergency_rwf, inflation_pct, month_num, had_shock,
                        shock_severity, profession, goals, debts, has_bank, language="en"):

    income_usd     = income_rwf     / RWF_PER_USD
    savings_usd    = savings_rwf    / RWF_PER_USD
    debt_usd       = debt_rwf       / RWF_PER_USD
    investment_usd = investment_rwf / RWF_PER_USD
    emergency_usd  = emergency_rwf  / RWF_PER_USD
    inflation      = inflation_pct  / 100

    obs, stress = build_obs(
        income_usd, savings_usd, debt_usd, investment_usd,
        emergency_usd, inflation, month_num, had_shock,
    )

    if model is not None:
        action, _ = model.predict(obs, deterministic=True)
        action    = int(action)
        source    = "AI Model (PPO)"
    else:
        action = rule_based(
            income_usd, savings_usd, debt_usd, emergency_usd,
            investment_usd, had_shock, stress, month_num,
        )
        source = "Rule-based (train model for AI recommendations)"

    if had_shock and shock_severity > 0.4 and action not in (7, 0, 3):
        action = 7

    from environment.custom_env import AfricanFinanceEnv
    alloc_pct = AfricanFinanceEnv.ACTION_ALLOCATIONS[action]
    alloc_rwf = {k: int(income_rwf * v) for k, v in alloc_pct.items() if v > 0}

    goal_type    = "long_term" if month_num > 12 else "emergency"
    savings_recs = recommend_savings_product(income_rwf, savings_rwf, debt_rwf, has_bank, goal_type, profession)
    d_advice     = debt_advice(debts, income_rwf)
    shock_plan   = shock_recovery_plan(
        income_rwf, savings_rwf, debt_rwf, emergency_rwf, shock_severity, profession
    ) if had_shock else None

    monthly_sav      = alloc_rwf.get("savings", 0) + alloc_rwf.get("emergency", 0)
    goal_projections = []
    for g in goals:
        target  = g.get("target_rwf", 0)
        current = g.get("current_rwf", 0)
        product = g.get("savings_product", "mtn_momo")
        rate    = SAVINGS_PRODUCTS.get(product, {}).get("rate", 0.06)
        mn      = months_to_goal(current, target, monthly_sav, rate)
        goal_projections.append({
            "name":           g.get("name", "Goal"),
            "target_rwf":     target,
            "current_rwf":    current,
            "months_needed":  mn,
            "on_track":       mn <= g.get("deadline_months", 24) - month_num,
            "monthly_needed": int((target - current) / max(mn, 1)),
            "product":        product,
            "product_name":   SAVINGS_PRODUCTS.get(product, {}).get("name", product),
        })

    return {
        "action":           action,
        "source":           source,
        "stress":           round(stress, 3),
        "alloc_pct":        alloc_pct,
        "alloc_rwf":        alloc_rwf,
        "action_text_en":   ACTION_TRANSLATIONS[action]["en"],
        "action_text_kiny": ACTION_TRANSLATIONS[action]["kiny"],
        "action_text_sw":   ACTION_TRANSLATIONS[action]["sw"],
        "action_explain":   ACTION_EXPLAIN[action],
        "savings_recs":     savings_recs,
        "debt_advice":      d_advice,
        "shock_plan":       shock_plan,
        "goal_projections": goal_projections,
        "prof_tip":         PROFESSIONS.get(profession, {}).get("income_tip", ""),
        "inflation_erosion_rwf": int(savings_rwf * inflation / 12),
        "had_shock":        had_shock,
        "month_num":        month_num,
    }