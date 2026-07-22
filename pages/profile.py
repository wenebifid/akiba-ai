import streamlit as st
import datetime
from utils.user_data import (
    create_user, user_exists, load_user, save_user,
    PROFESSIONS, SAVINGS_PRODUCTS, user_path,
)


def render():
    st.markdown('<h2 style="color:#C9A84C">👤 My Profile</h2>', unsafe_allow_html=True)
    existing = st.session_state.get("username")
    data     = load_user(existing) if existing else {}
    st.caption("This takes 2 minutes. All advice is personalised to your situation.")

    with st.form("profile_form"):
        st.markdown('<p class="section-title">Basic information</p>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            name     = st.text_input("Your name",             value=data.get("name", ""))
            username = st.text_input("Username (no spaces)",   value=existing or "")
        with c2:
            lang_map   = {"English": "en", "Kinyarwanda": "kiny", "Kiswahili": "sw"}
            cur_lang   = next((k for k, v in lang_map.items() if v == data.get("language", "en")), "English")
            lang_label = st.selectbox("Preferred language", list(lang_map.keys()),
                                      index=list(lang_map.keys()).index(cur_lang))
            language   = lang_map[lang_label]

        st.markdown('<p class="section-title">Your profession</p>', unsafe_allow_html=True)
        prof_labels = {k: f"{v['label']} — {v['label_kiny']}" for k, v in PROFESSIONS.items()}
        cur_prof    = data.get("profession", "market_trader")
        prof_key    = st.radio(
            "What best describes your work?",
            list(prof_labels.keys()),
            format_func=lambda k: prof_labels[k],
            index=list(PROFESSIONS.keys()).index(cur_prof) if cur_prof in PROFESSIONS else 0,
        )
        prof   = PROFESSIONS[prof_key]
        lo, hi = prof["typical_income_rwf"]
        st.caption(f"Typical income: RWF {lo:,}–{hi:,}/month · {prof['income_pattern'].title()} income · {prof['income_tip']}")

        st.markdown('<p class="section-title">Starting financial situation</p>', unsafe_allow_html=True)
        last = data["history"][-1] if data.get("history") else {}
        c1, c2, c3 = st.columns(3)
        with c1:
            inc = st.number_input("Monthly income (RWF)",  5000,  500000, int(last.get("income",     lo)),  1000)
            sav = st.number_input("Total savings (RWF)",      0, 2000000, int(last.get("savings",  5000)),  1000)
        with c2:
            dbt = st.number_input("Total debt (RWF)",          0, 5000000, int(last.get("debt",        0)),  5000)
            emg = st.number_input("Emergency fund (RWF)",      0, 1000000, int(last.get("emergency",   0)),  1000)
        with c3:
            inv      = st.number_input("Investments (RWF)",    0, 10000000, int(last.get("investment", 0)), 5000)
            has_bank = st.checkbox("I have a bank account", value=data.get("has_bank", False))

        st.markdown('<p class="section-title">Savings products you currently use</p>', unsafe_allow_html=True)
        selected_prods = st.multiselect(
            "Select all that apply",
            list(SAVINGS_PRODUCTS.keys()),
            default=data.get("savings_products", []),
            format_func=lambda k: SAVINGS_PRODUCTS[k]["name"],
        )

        submitted = st.form_submit_button("💾 Save Profile", use_container_width=True)

    if submitted:
        if not username:
            st.error("Please enter a username.")
            return
        username = username.lower().replace(" ", "_")
        if user_exists(username) and username != existing:
            st.error("Username taken. Choose another.")
            return
        if existing and username != existing:
            old = user_path(existing)
            if old.exists():
                old.rename(user_path(username))

        profile = load_user(username) if user_exists(username) else create_user(username, prof_key, name)
        profile.update({
            "name":             name,
            "profession":       prof_key,
            "language":         language,
            "has_bank":         has_bank,
            "savings_products": selected_prods,
        })
        if not profile.get("history"):
            profile["history"] = [{
                "month": 0, "income": inc, "expenses": int(inc * 0.65),
                "savings": sav, "debt": dbt, "investment": inv,
                "emergency": emg, "shock": False, "shock_severity": 0,
                "inflation_pct": 18, "date": str(datetime.date.today()),
                "note": "Starting balance",
            }]
        save_user(username, profile)
        st.session_state.username  = username
        st.session_state.user_data = profile
        st.success(f"✅ Profile saved! Welcome, {name}.")
        st.balloons()
        import time; time.sleep(1.5)
        st.session_state.page = "checkin"
        st.rerun()