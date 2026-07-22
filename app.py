import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

st.set_page_config(
    page_title="Akiba AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.akiba-header { background: linear-gradient(135deg, #0D1117 0%, #1a2744 100%); border-radius: 16px; padding: 24px; margin-bottom: 20px; border: 1px solid #C9A84C; text-align: center; }
.akiba-header h1 { color: #C9A84C; font-size: 2.2rem; margin: 0; }
.akiba-header p { color: #8B949E; margin: 6px 0 0; font-size: 0.95rem; }
.card { background: #161B22; border-radius: 12px; padding: 20px; border: 1px solid #2E4057; margin-bottom: 16px; }
.card-gold { border-color: #C9A84C; }
.card-red  { border-color: #FF6B6B; }
.metric-box { background: #0D1117; border-radius: 10px; padding: 14px; border: 1px solid #2E4057; text-align: center; }
.metric-label { color: #8B949E; font-size: 0.78rem; margin: 0; }
.metric-value { color: #C9D1D9; font-size: 1.25rem; font-weight: 700; margin: 4px 0 0; }
.green  { color: #56D364 !important; }
.red    { color: #FF6B6B !important; }
.orange { color: #F0883E !important; }
.gold   { color: #C9A84C !important; }
.blue   { color: #4EA3E0 !important; }
.rec-card { background: linear-gradient(135deg, #1a2744 0%, #0D1117 100%); border-radius: 16px; padding: 28px 24px; margin: 16px 0; border: 2px solid #C9A84C; }
.rec-headline { color: #C9A84C; font-size: 1.6rem; font-weight: 700; margin: 0; }
.rec-lang { color: #56D364; font-size: 0.85rem; margin: 4px 0; font-style: italic; }
.rec-explain { color: #8B949E; font-size: 0.9rem; margin: 14px 0 0; line-height: 1.7; }
.warn { background: rgba(255,107,107,0.1); border: 1px solid #FF6B6B; border-radius: 10px; padding: 14px; margin: 10px 0; color: #FF6B6B; font-size: 0.9rem; }
.info { background: rgba(86,211,100,0.08); border: 1px solid #56D364; border-radius: 10px; padding: 14px; margin: 10px 0; color: #56D364; font-size: 0.9rem; }
.tip  { background: rgba(78,163,224,0.08); border: 1px solid #4EA3E0; border-radius: 10px; padding: 14px; margin: 10px 0; color: #4EA3E0; font-size: 0.9rem; }
.product-card { background: #0D1117; border-radius: 10px; padding: 14px; border-left: 4px solid #C9A84C; margin-bottom: 10px; }
.debt-card { background: #0D1117; border-radius: 10px; padding: 14px; border-left: 4px solid #FF6B6B; margin-bottom: 10px; }
.shock-card { background: rgba(255,107,107,0.05); border-radius: 12px; padding: 18px; border: 2px solid #FF6B6B; margin: 12px 0; }
.section-title { color: #C9A84C; font-size: 1.05rem; font-weight: 700; padding-bottom: 8px; border-bottom: 1px solid #2E4057; margin: 20px 0 14px; }
footer { visibility: hidden; }
.stButton > button { background: linear-gradient(135deg, #C9A84C, #F0C060); color: #0D1117; font-weight: 700; border: none; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def get_model():
    try:
        from utils.advisor import load_best_model
        return load_best_model()
    except Exception:
        return None, None


def nav():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:16px 0 8px">
            <span style="font-size:2.5rem">🌍</span>
            <p style="color:#C9A84C;font-size:1.2rem;font-weight:700;margin:4px 0 0">Akiba AI</p>
            <p style="color:#8B949E;font-size:0.78rem;margin:0">Your Financial Advisor</p>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

        model, algo = get_model()
        if model:
            st.success(f"✅ AI Model: {algo}")
        else:
            st.warning("⚠️ No model yet\nRun: `python quick_train.py`")

        if "username" in st.session_state:
            st.info(f"👤 {st.session_state.get('username', '')}")

        st.divider()
        pages = {
            "🏠 Home":             "home",
            "👤 My Profile":       "profile",
            "📅 Monthly Check-in": "checkin",
            "📊 My Dashboard":     "dashboard",
            "🎯 My Goals":         "goals",
            "💳 Debt Advisor":     "debt",
            "🏦 Where to Save":    "products",
            "ℹ️ About":            "about",
        }
        if "page" not in st.session_state:
            st.session_state.page = "home"

        for label, key in pages.items():
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()

        st.divider()
        st.caption("Akiba AI · ALU Capstone 2025\nOyinwenebi Fiderikumo")


def main():
    nav()
    model, algo = get_model()
    page = st.session_state.get("page", "home")

    if   page == "home":      from pages.home      import render; render(model, algo)
    elif page == "profile":   from pages.profile   import render; render()
    elif page == "checkin":   from pages.checkin   import render; render(model, algo)
    elif page == "dashboard": from pages.dashboard import render; render()
    elif page == "goals":     from pages.goals     import render; render()
    elif page == "debt":      from pages.debt      import render; render()
    elif page == "products":  from pages.products  import render; render()
    elif page == "about":     from pages.about     import render; render()


if __name__ == "__main__":
    main()