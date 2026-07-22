import streamlit as st
from utils.user_data import load_user, SAVINGS_PRODUCTS, PROFESSIONS


def render():
    username = st.session_state.get("username")
    data     = load_user(username) if username else {}
    history  = data.get("history", [])
    income   = history[-1].get("income", 30000) if history else 30000
    inflation= history[-1].get("inflation_pct", 18) if history else 18
    prof_key = data.get("profession", "market_trader")
    best     = PROFESSIONS.get(prof_key, {}).get("best_savings", [])

    st.markdown('<h2 style="color:#C9A84C">🏦 Where to Save Your Money</h2>', unsafe_allow_html=True)
    st.caption(f"Compared against {inflation}% annual inflation. A positive real return means your money is growing in real terms.")

    st.markdown(f"""
    <div class="tip">
        💡 Rwanda's inflation was 19.79% in 2023 (NISR). Any savings product earning less than this
        means your money is losing value. Ejo Heza at 12% still loses to 20% inflation — but far less
        than keeping cash at home at 0%.
    </div>""", unsafe_allow_html=True)

    st.divider()

    for key, prod in SAVINGS_PRODUCTS.items():
        rate    = prod.get("rate", 0)
        real_r  = ((1 + rate) / (1 + inflation / 100) - 1) * 100
        is_best = key in best
        border  = "#C9A84C" if is_best else "#2E4057"
        badge   = "⭐ Recommended for you" if is_best else ""

        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"""
            <div class="card" style="border-color:{border}">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                    <div>
                        <p style="color:#C9A84C;font-weight:700;font-size:1rem;margin:0">
                            🏦 {prod.get('name', '')}
                        </p>
                        <p style="color:#56D364;font-size:0.85rem;margin:4px 0">
                            {prod.get('rate_display', '')}
                        </p>
                    </div>
                    <span style="color:#C9A84C;font-size:0.78rem">{badge}</span>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px;font-size:0.82rem">
                    <div>
                        <span style="color:#8B949E">Real return (after {inflation}% inflation)</span><br>
                        <strong style="color:{'#56D364' if real_r > 0 else '#FF6B6B'}">{real_r:+.1f}%</strong>
                    </div>
                    <div>
                        <span style="color:#8B949E">Minimum amount</span><br>
                        <strong style="color:#C9D1D9">RWF {prod.get('min_amount', 0):,}</strong>
                    </div>
                    <div>
                        <span style="color:#8B949E">Access to money</span><br>
                        <strong style="color:#C9D1D9">{prod.get('liquidity', '').replace('_', ' ').title()}</strong>
                    </div>
                    <div>
                        <span style="color:#8B949E">Risk level</span><br>
                        <strong style="color:#C9D1D9">{prod.get('risk', '').replace('_', ' ').title()}</strong>
                    </div>
                </div>
                <p style="color:#8B949E;font-size:0.82rem;margin:10px 0 4px">{prod.get('who_for', '')}</p>
                {f'<p style="color:#F0883E;font-size:0.78rem;margin:4px 0">Note: {prod.get("note", "")}</p>' if prod.get('note') else ''}
                <p style="color:#4EA3E0;font-size:0.82rem;margin:6px 0 0">📱 How to sign up: {prod.get('how_to', '')}</p>
            </div>""", unsafe_allow_html=True)

        with col2:
            suggested = max(prod.get("min_amount", 0), int(income * 0.10))
            years     = [1, 2, 3, 5]
            st.markdown(f"**If you save RWF {suggested:,}/month:**")
            for y in years:
                months = y * 12
                r      = rate / 12
                future = suggested * ((1 + r) ** months - 1) / (r + 1e-9) if r > 0 else suggested * months
                st.markdown(f"- {y} year{'s' if y > 1 else ''}: **RWF {int(future):,}**")