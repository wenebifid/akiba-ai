import streamlit as st
import plotly.graph_objects as go
from utils.user_data import load_user, add_monthly_entry, PROFESSIONS, SAVINGS_PRODUCTS
from utils.advisor import full_recommendation

ICONS  = ["💰", "⚖️", "📈", "💳", "🛡️", "📚", "📱", "🆘"]
COLORS = {
    "savings": "#4EA3E0", "expenses": "#8B949E", "investments": "#F0883E",
    "debt": "#FF6B6B", "emergency": "#00C8B4", "education": "#BC8CFF",
}


def require_login():
    if "username" not in st.session_state:
        st.warning("Please sign in or create a profile first.")
        if st.button("Go to Home"):
            st.session_state.page = "home"
            st.rerun()
        return False
    return True


def render(model, algo):
    if not require_login():
        return

    username  = st.session_state.username
    data      = load_user(username)
    prof      = PROFESSIONS.get(data.get("profession", "market_trader"), {})
    history   = data.get("history", [])
    month_num = len(history)
    lang      = data.get("language", "en")
    last      = history[-1] if history else {}

    st.markdown(f'<h2 style="color:#C9A84C">📅 Monthly Check-in — Month {month_num + 1}</h2>', unsafe_allow_html=True)
    st.caption(f"Hello, {data.get('name', 'friend')} · {prof.get('label', '')} · Tell us how this month went")

    with st.form("checkin"):
        st.markdown('<p class="section-title">This month\'s numbers (RWF)</p>', unsafe_allow_html=True)
        lo = prof.get("typical_income_rwf", [30000, 60000])[0]
        c1, c2, c3 = st.columns(3)
        with c1:
            income   = st.number_input("💵 Income this month",  0, 500000,  int(last.get("income",   lo)),  1000)
            savings  = st.number_input("🏦 Total savings now",  0, 5000000, int(last.get("savings", 5000)), 1000)
        with c2:
            expenses = st.number_input("🛒 Total expenses",     0, 500000,  int(last.get("expenses", int(lo * 0.65))), 1000)
            debt     = st.number_input("💳 Total debt now",     0, 10000000,int(last.get("debt",     0)),   5000)
        with c3:
            invest   = st.number_input("📈 Investments",        0, 50000000,int(last.get("investment", 0)), 5000)
            emergency= st.number_input("🛡️ Emergency fund",    0, 5000000, int(last.get("emergency",  0)),  1000)

        st.markdown('<p class="section-title">What happened this month?</p>', unsafe_allow_html=True)
        c4, c5 = st.columns(2)
        with c4:
            had_shock = st.checkbox("⚡ I had an income shock (illness, bad harvest, theft, etc.)")
            shock_sev = 0.0
            if had_shock:
                shock_sev = st.slider("How much income did you lose?", 10, 90, 40, format="%d%%") / 100
                st.selectbox("What caused it?", [
                    "Illness/injury", "Bad harvest", "Market closure",
                    "Theft/loss", "Breakdown", "Family emergency", "Other",
                ])
        with c5:
            inflation = st.slider("📊 How do prices feel? (%)", 5, 30, int(last.get("inflation_pct", 18)))
            note      = st.text_area("📝 Notes (optional)", placeholder="School fees next month...", height=80)

        submitted = st.form_submit_button("🔍 Get My Recommendation →", use_container_width=True)

    if submitted:
        add_monthly_entry(username, {
            "income": income, "expenses": expenses, "savings": savings,
            "debt": debt, "investment": invest, "emergency": emergency,
            "shock": had_shock, "shock_severity": shock_sev,
            "inflation_pct": inflation, "note": note,
        })
        data = load_user(username)

        with st.spinner("🤖 Analyzing your finances..."):
            rec = full_recommendation(
                model=model,
                income_rwf=income,      savings_rwf=savings,
                debt_rwf=debt,          investment_rwf=invest,
                emergency_rwf=emergency,inflation_pct=inflation,
                month_num=month_num + 1,had_shock=had_shock,
                shock_severity=shock_sev,
                profession=data.get("profession", "market_trader"),
                goals=data.get("goals", []),
                debts=data.get("debts", []),
                has_bank=data.get("has_bank", False),
                language=lang,
            )

        action = rec["action"]

        # Main recommendation card
        st.markdown(f"""
        <div class="rec-card">
            <p style="color:#8B949E;font-size:0.78rem;margin:0 0 8px">{rec['source']} · Month {month_num + 1} of 60</p>
            <p class="rec-headline">{ICONS[action]} {rec['action_text_en']}</p>
            <p class="rec-lang">🇷🇼 {rec['action_text_kiny']}</p>
            <p class="rec-lang">🌍 {rec['action_text_sw']}</p>
            <p class="rec-explain">{rec['action_explain']}</p>
        </div>""", unsafe_allow_html=True)

        # Shock recovery plan
        if had_shock and rec.get("shock_plan"):
            sp = rec["shock_plan"]
            st.markdown(f"""
            <div class="shock-card">
                <p style="color:#FF6B6B;font-size:1rem;font-weight:700;margin:0">
                    ⚡ Income Shock — Severity: {shock_sev * 100:.0f}%
                </p>
                <p style="color:#C9D1D9;font-size:0.88rem;margin:8px 0 0">
                    Your emergency fund covers <strong>{sp['buffer_months']}</strong> months.
                    {"You can manage without borrowing." if sp['can_survive'] else "You may need short-term support."}
                </p>
            </div>""", unsafe_allow_html=True)

            st.markdown('<p class="section-title">⚡ Your 3-month recovery plan</p>', unsafe_allow_html=True)
            for col, m, color in zip(st.columns(3), sp["months"], ["#FF6B6B", "#F0883E", "#56D364"]):
                with col:
                    st.markdown(f"""
                    <div class="card" style="border-color:{color};text-align:center">
                        <p style="color:{color};font-weight:700;font-size:1.1rem;margin:0">
                            Month {m['month']}: {m['label']}
                        </p>
                        <p style="color:#8B949E;font-size:0.82rem;margin:8px 0 0">{m['focus']}</p>
                    </div>""", unsafe_allow_html=True)

            if sp.get("borrow_advice"):
                ba = sp["borrow_advice"]
                if ba["should_borrow"]:
                    st.markdown(f"""
                    <div class="tip">
                        💡 <strong>If you need to borrow:</strong> Use <strong>{ba['source']}</strong><br>
                        {ba['reason']}<br>
                        <span style="color:#FF6B6B">{ba.get('warning', '')}</span>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="warn">⚠️ {ba["reason"]}</div>', unsafe_allow_html=True)

        # Money breakdown
        st.markdown(f'<p class="section-title">💰 Where your RWF {income:,} goes this month</p>', unsafe_allow_html=True)
        c_chart, c_detail = st.columns([1.2, 1])

        with c_chart:
            labels, values, colors_p, amounts = [], [], [], []
            for k, pct in rec["alloc_pct"].items():
                if pct > 0:
                    labels.append(k.title())
                    values.append(pct)
                    colors_p.append(COLORS.get(k, "#C9A84C"))
                    amounts.append(int(income * pct))

            fig = go.Figure(go.Pie(
                labels=labels, values=values,
                marker=dict(colors=colors_p, line=dict(color="#0D1117", width=2)),
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>%{percent}<br>RWF %{customdata:,}<extra></extra>",
                customdata=amounts, hole=0.42,
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#C9D1D9", family="Inter"),
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                margin=dict(t=10, b=10, l=10, r=10), height=300,
                annotations=[dict(
                    text=f"RWF<br>{income:,}", x=0.5, y=0.5,
                    font=dict(size=12, color="#C9A84C"), showarrow=False,
                )],
            )
            st.plotly_chart(fig, use_container_width=True)

        with c_detail:
            st.markdown("<br>", unsafe_allow_html=True)
            for k, pct in rec["alloc_pct"].items():
                if pct > 0:
                    amt = int(income * pct)
                    c   = COLORS.get(k, "#C9A84C")
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #21262D">
                        <span style="color:#C9D1D9;font-size:0.9rem">{k.title()}</span>
                        <span style="color:{c};font-weight:700;font-size:0.9rem">RWF {amt:,} ({pct * 100:.0f}%)</span>
                    </div>""", unsafe_allow_html=True)

        # Where to save
        if rec.get("savings_recs"):
            st.markdown('<p class="section-title">🏦 Where to put your savings</p>', unsafe_allow_html=True)
            for r in rec["savings_recs"][:3]:
                prod   = SAVINGS_PRODUCTS.get(r["product"], {})
                real_r = ((1 + prod.get("rate", 0)) / (1 + inflation / 100) - 1) * 100
                st.markdown(f"""
                <div class="product-card">
                    <p style="color:#C9A84C;font-weight:700;font-size:1rem;margin:0">🏦 {prod.get('name', '')}</p>
                    <p style="color:#56D364;font-size:0.85rem;margin:4px 0">
                        {prod.get('rate_display', '')} · Real return after {inflation}% inflation:
                        <span style="color:{'#56D364' if real_r > 0 else '#FF6B6B'}">{real_r:+.1f}%</span>
                    </p>
                    <p style="color:#C9D1D9;font-size:0.82rem;margin:4px 0">
                        Suggested: <strong>RWF {r.get('suggested_monthly_rwf', 0):,}/month</strong> · {r.get('reason', '')}
                    </p>
                    <p style="color:#8B949E;font-size:0.78rem;margin:4px 0">📱 {prod.get('how_to', '')}</p>
                </div>""", unsafe_allow_html=True)

        # Inflation warning
        erosion = rec.get("inflation_erosion_rwf", 0)
        if erosion > 500:
            st.markdown(f"""
            <div class="warn">
                📉 <strong>Inflation alert:</strong> At {inflation}% annual, your savings are losing
                <strong>RWF {erosion:,}</strong> in purchasing power this month.
                Keep money in Ejo Heza (12%) or SACCO (11%) — not in cash at home.
            </div>""", unsafe_allow_html=True)

        # Debt danger
        if rec.get("debt_advice", {}).get("danger"):
            st.markdown(f'<div class="warn">{rec["debt_advice"]["danger_message"]}</div>', unsafe_allow_html=True)

        # Goal progress
        if rec.get("goal_projections"):
            st.markdown('<p class="section-title">🎯 Goal updates</p>', unsafe_allow_html=True)
            for gp in rec["goal_projections"]:
                pct   = min(gp["current_rwf"] / max(gp["target_rwf"], 1), 1.0)
                color = "#56D364" if gp["on_track"] else "#FF6B6B"
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;margin-bottom:4px">
                    <span style="color:#C9D1D9;font-weight:600">{gp['name']}</span>
                    <span style="color:{color};font-size:0.82rem">
                        {"✅ On track" if gp['on_track'] else f"⚠️ {gp['months_needed']} months needed"}
                    </span>
                </div>""", unsafe_allow_html=True)
                st.progress(pct)

        # Profession tip
        if rec.get("prof_tip"):
            st.markdown(f'<div class="tip">💡 <strong>Tip for {prof.get("label", "")}s:</strong> {rec["prof_tip"]}</div>',
                        unsafe_allow_html=True)

        st.success("✅ Check-in saved! Come back next month to track your progress.")
        if st.button("📊 View My Dashboard →"):
            st.session_state.page = "dashboard"
            st.rerun()