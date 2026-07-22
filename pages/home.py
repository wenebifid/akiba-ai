import streamlit as st
from utils.user_data import list_users, load_user, PROFESSIONS

ICONS = {
    "boda_boda": "🏍️",
    "market_trader": "🛒",
    "domestic_worker": "🏠",
    "smallholder_farmer": "🌾",
}


def render(model, algo):
    st.markdown("""
    <div class="akiba-header">
        <h1>🌍 Akiba AI</h1>
        <p>Mshauri wako wa fedha · Umujyanama wawe w'imari · Your personal financial advisor<br>
        <small>Powered by Reinforcement Learning · Calibrated for East Africa</small></p>
    </div>
    """, unsafe_allow_html=True)

    users = list_users()
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown('<p class="section-title">👋 Sign in or get started</p>', unsafe_allow_html=True)
        if users:
            selected = st.selectbox("Your name", ["— Select —"] + users, label_visibility="collapsed")
            if selected != "— Select —":
                if st.button("Continue →", use_container_width=True):
                    st.session_state.username  = selected
                    st.session_state.user_data = load_user(selected)
                    st.session_state.page      = "checkin"
                    st.rerun()
            st.markdown("---")
        if st.button("➕ Create My Profile", use_container_width=True):
            st.session_state.page = "profile"
            st.rerun()

    with col2:
        st.markdown('<p class="section-title">What Akiba AI does</p>', unsafe_allow_html=True)
        for icon, title, desc in [
            ("📅", "Monthly check-ins",        "Log your income and expenses every month"),
            ("🤖", "AI recommendations",        "Personalized advice from a trained RL model"),
            ("🏦", "Where exactly to save",     "Ejo Heza, SACCO, MoMo — with real interest rates"),
            ("⚡", "Shock recovery plan",        "3-month plan when income drops unexpectedly"),
            ("💳", "Debt ranking",              "Know which debt to pay first and exactly why"),
            ("🎯", "Goal tracking",             "Set a goal and see exactly when you'll reach it"),
        ]:
            st.markdown(f"""
            <div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:10px">
                <span style="font-size:1.4rem">{icon}</span>
                <div>
                    <p style="color:#C9D1D9;font-weight:600;margin:0;font-size:0.9rem">{title}</p>
                    <p style="color:#8B949E;margin:2px 0 0;font-size:0.8rem">{desc}</p>
                </div>
            </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown('<p class="section-title">💼 Built for these professions</p>', unsafe_allow_html=True)
    cols = st.columns(4)
    for col, (key, prof) in zip(cols, PROFESSIONS.items()):
        lo, hi = prof["typical_income_rwf"]
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center">
                <p style="font-size:2rem;margin:0">{ICONS.get(key, '💼')}</p>
                <p style="color:#C9A84C;font-weight:700;margin:6px 0 4px;font-size:0.9rem">{prof['label']}</p>
                <p style="color:#8B949E;font-size:0.78rem;margin:0">RWF {lo:,}–{hi:,}/month</p>
                <p style="color:#56D364;font-size:0.75rem;margin:4px 0 0">{prof['income_pattern'].title()} income</p>
                <p style="color:#4EA3E0;font-size:0.72rem;margin:4px 0 0;font-style:italic">{prof['label_kiny']}</p>
            </div>""", unsafe_allow_html=True)