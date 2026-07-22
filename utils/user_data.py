import os, json, datetime
from pathlib import Path

DATA_DIR = Path(os.path.dirname(os.path.dirname(__file__))) / "data" / "users"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SAVINGS_PRODUCTS = {
    "mtn_momo": {
        "name": "MTN MoMo / MoKash",
        "name_kiny": "MTN MoMo / MoKash",
        "name_sw": "MTN MoMo / MoKash",
        "rate": 0.06,
        "rate_display": "~6% per year",
        "min_amount": 100,
        "liquidity": "instant",
        "how_to": "Dial *182# → MoKash → Save",
        "who_for": "Anyone with an MTN SIM. Best for short-term accessible savings.",
        "risk": "low",
    },
    "airtel_money": {
        "name": "Airtel Money Savings",
        "name_kiny": "Airtel Money Ibikoresho",
        "name_sw": "Airtel Money Akiba",
        "rate": 0.05,
        "rate_display": "~5% per year",
        "min_amount": 100,
        "liquidity": "instant",
        "how_to": "Dial *185# → Savings",
        "who_for": "Airtel SIM holders. Similar to MoMo.",
        "risk": "low",
    },
    "ejo_heza": {
        "name": "Ejo Heza (RSSB Pension)",
        "name_kiny": "Ejo Heza (Izigamiro ry'Ejo Hazaza)",
        "name_sw": "Ejo Heza (Akiba ya Mustakabali)",
        "rate": 0.12,
        "rate_display": "12% per year + govt top-up",
        "min_amount": 1000,
        "liquidity": "locked",
        "how_to": "Register via *550# or visit nearest RSSB office",
        "who_for": "Everyone. Government top-up makes this the best long-term rate in Rwanda.",
        "note": "Funds locked until age 55. Can use as collateral for bank loans.",
        "risk": "very_low",
    },
    "umurenge_sacco": {
        "name": "Umurenge SACCO",
        "name_kiny": "Ikigega cy'Umurenge (SACCO)",
        "name_sw": "SACCO ya Kata",
        "rate": 0.11,
        "rate_display": "10-12% per year on savings",
        "min_amount": 2000,
        "liquidity": "weekly",
        "how_to": "Visit your local Umurenge (sector) office to join",
        "who_for": "Community members. Loans at 24% — far cheaper than moneylenders.",
        "note": "416 SACCOs across Rwanda. Loans available to members at 24% vs 120%+ informal.",
        "risk": "low",
    },
    "bank_deposit": {
        "name": "Commercial Bank Deposit",
        "name_kiny": "Konti ya Banki",
        "name_sw": "Akaunti ya Benki",
        "rate": 0.1033,
        "rate_display": "~10% per year",
        "min_amount": 20000,
        "liquidity": "daily",
        "how_to": "Visit BK, Equity Bank, I&M, or Cogebanque with your ID",
        "who_for": "Those with formal income and ID. Requires minimum balance.",
        "risk": "very_low",
    },
    "tontine": {
        "name": "Tontine / Ibimina (Rotating Savings)",
        "name_kiny": "Ibimina / Tontine",
        "name_sw": "Chama / Upatu",
        "rate": 0.0,
        "rate_display": "0% — savings discipline through social commitment",
        "min_amount": 500,
        "liquidity": "monthly_rotation",
        "how_to": "Join or form a group of 5-20 trusted people who each contribute monthly",
        "who_for": "Anyone. No bank account needed. Forces savings habit.",
        "note": "Risk is social — if a member defaults, the group loses. Choose trusted members.",
        "risk": "medium",
    },
}

DEBT_SOURCES = {
    "momo_loan":     {"name": "MTN MoKash / Airtel Loan",  "rate_annual": 0.24,  "note": "Short-term only. Repay within 30 days."},
    "sacco_loan":    {"name": "Umurenge SACCO Loan",        "rate_annual": 0.24,  "note": "Best formal option. Requires SACCO membership."},
    "bank_loan":     {"name": "Commercial Bank Loan",       "rate_annual": 0.1572,"note": "Cheapest formal rate. Requires collateral."},
    "moneylender":   {"name": "Informal Moneylender",       "rate_annual": 1.20,  "note": "DANGEROUS. 10% per month = 120% per year."},
    "family_friend": {"name": "Family / Friend",            "rate_annual": 0.0,   "note": "No interest but social obligation."},
}

PROFESSIONS = {
    "boda_boda": {
        "label": "Boda-Boda Driver",
        "label_kiny": "Umunyabodaboda",
        "label_sw": "Dereva wa Boda-Boda",
        "income_pattern": "daily",
        "typical_income_rwf": [15000, 45000],
        "typical_expenses_pct": 0.70,
        "main_risks": ["fuel_cost", "accident", "breakdown", "rain"],
        "income_tip": "Track daily earnings. Set aside RWF 500-1,000 every day before spending on anything else.",
        "best_savings": ["mtn_momo", "tontine"],
        "seasonal": False,
    },
    "market_trader": {
        "label": "Market Trader",
        "label_kiny": "Umuguzi w'Isoko",
        "label_sw": "Muuzaji wa Soko",
        "income_pattern": "weekly",
        "typical_income_rwf": [20000, 80000],
        "typical_expenses_pct": 0.68,
        "main_risks": ["market_closure", "stock_loss", "price_drops"],
        "income_tip": "Separate your stock capital from your profit. Never spend your stock money on household expenses.",
        "best_savings": ["mtn_momo", "umurenge_sacco"],
        "seasonal": True,
    },
    "domestic_worker": {
        "label": "Domestic Worker",
        "label_kiny": "Umukozi w'Urugo",
        "label_sw": "Msaidizi wa Nyumbani",
        "income_pattern": "monthly",
        "typical_income_rwf": [25000, 70000],
        "typical_expenses_pct": 0.65,
        "main_risks": ["job_loss", "family_pressure", "non_payment"],
        "income_tip": "Your stable income is your advantage. Use it to build Ejo Heza contributions — 12% annual return is hard to beat.",
        "best_savings": ["ejo_heza", "umurenge_sacco"],
        "seasonal": False,
    },
    "smallholder_farmer": {
        "label": "Smallholder Farmer",
        "label_kiny": "Umuhinzi",
        "label_sw": "Mkulima Mdogo",
        "income_pattern": "seasonal",
        "typical_income_rwf": [10000, 100000],
        "typical_expenses_pct": 0.72,
        "main_risks": ["drought", "crop_failure", "price_drops", "input_costs"],
        "income_tip": "At harvest time, save aggressively — you need to survive 4-6 months with little income. Save at least 40% at harvest.",
        "best_savings": ["umurenge_sacco", "ejo_heza", "tontine"],
        "seasonal": True,
    },
}


def user_path(username):
    return DATA_DIR / f"{username.lower().replace(' ', '_')}.json"

def user_exists(username):
    return user_path(username).exists()

def load_user(username):
    p = user_path(username)
    return json.loads(p.read_text()) if p.exists() else {}

def save_user(username, data):
    user_path(username).write_text(json.dumps(data, indent=2, default=str))

def list_users():
    return [p.stem for p in DATA_DIR.glob("*.json")]

def create_user(username, profession, name=""):
    data = {
        "username":        username,
        "name":            name or username,
        "profession":      profession,
        "created_at":      str(datetime.date.today()),
        "language":        "en",
        "goals":           [],
        "debts":           [],
        "history":         [],
        "savings_products":[],
        "has_bank":        False,
    }
    save_user(username, data)
    return data

def add_monthly_entry(username, entry):
    data = load_user(username)
    entry["date"]  = str(datetime.date.today())
    entry["month"] = len(data.get("history", [])) + 1
    data.setdefault("history", []).append(entry)
    save_user(username, data)

def add_goal(username, goal):
    data = load_user(username)
    goal["created_at"] = str(datetime.date.today())
    data.setdefault("goals", []).append(goal)
    save_user(username, data)

def add_debt(username, debt):
    data = load_user(username)
    data.setdefault("debts", []).append(debt)
    save_user(username, data)

def remove_debt(username, idx):
    data = load_user(username)
    if 0 <= idx < len(data.get("debts", [])):
        data["debts"].pop(idx)
        save_user(username, data)

def months_to_goal(current, target, monthly_contribution, annual_rate):
    if monthly_contribution <= 0:
        return 999
    r       = annual_rate / 12
    balance = current
    for m in range(1, 361):
        balance = balance * (1 + r) + monthly_contribution
        if balance >= target:
            return m
    return 999

def debt_payoff_months(debt, monthly_payment, annual_rate):
    if monthly_payment <= 0 or debt <= 0:
        return 0
    r       = annual_rate / 12
    balance = debt
    for m in range(1, 361):
        balance = balance * (1 + r) - monthly_payment
        if balance <= 0:
            return m
    return 999

def monthly_interest_cost(debt, annual_rate):
    return debt * (annual_rate / 12)

def real_return(nominal, inflation=0.18):
    return (1 + nominal) / (1 + inflation) - 1

def rank_debts(debts):
    return sorted(debts, key=lambda d: d.get("rate_annual", 0), reverse=True)

def recommend_savings_product(income_rwf, savings_rwf, debt_rwf, has_bank, goal_type, profession):
    recs = []
    prof = PROFESSIONS.get(profession, {})

    if income_rwf >= 5000:
        recs.append({
            "product": "mtn_momo",
            "priority": 1,
            "reason": "Available to anyone with a phone. No bank account needed. Start here.",
            "suggested_monthly_rwf": max(500, int(income_rwf * 0.10)),
        })

    if goal_type == "long_term" or "ejo_heza" in prof.get("best_savings", []):
        recs.append({
            "product": "ejo_heza",
            "priority": 2,
            "reason": "12% annual + government top-up. Best long-term rate in Rwanda. Locked until 55.",
            "suggested_monthly_rwf": max(1000, int(income_rwf * 0.05)),
        })

    if income_rwf >= 20000 and savings_rwf > income_rwf:
        recs.append({
            "product": "umurenge_sacco",
            "priority": 3,
            "reason": "10-12% return + access to cheap loans (24%) when you need them.",
            "suggested_monthly_rwf": int(income_rwf * 0.10),
        })

    if has_bank and income_rwf >= 50000:
        recs.append({
            "product": "bank_deposit",
            "priority": 4,
            "reason": "Safe and regulated. Good for amounts above RWF 100,000.",
            "suggested_monthly_rwf": int(income_rwf * 0.15),
        })

    if "tontine" in prof.get("best_savings", []):
        recs.append({
            "product": "tontine",
            "priority": 5,
            "reason": "Builds savings discipline through social commitment. No bank account needed.",
            "suggested_monthly_rwf": int(income_rwf * 0.08),
        })

    return sorted(recs, key=lambda x: x["priority"])