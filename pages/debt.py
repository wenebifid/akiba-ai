import streamlit as st
from utils.user_data import load_user, save_user, add_debt, remove_debt, DEBT_SOURCES, rank_debts, monthly_interest_cost, debt_payoff_months


def require_login():
    if "username" not in st.session_state:
        st.warning("Please sign in first.")
        if st.button("Go to Home"):
            st.session_state.page = "home"
            st.rerun()
        return False
    return True


def render():
    if not require_login():
        return

    username = st.session_state.username
    data     = load_user(username)
    debts    = data.get("debts", [])
    history  = data.get("history", [])
    income   = history[-1].get("income", 30000) if history else 30000

    st.markdown('<h2 style="color:#C9A84C">💳 Debt Advisor</h2>', unsafe_allow_html=True)

    if debts:
        ranked     = rank_debts(debts)
        total_debt = sum(d.get("amount_rwf", 0) for d in debts)
        total_mc   = sum(monthly_interest_cost(d.get("amount_rwf", 0), d.get("rate_annual", 0)) for d in debts)
        danger     = any(d.get("rate_annual", 0) >= 0.60 for d in debts)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total debt",          f"RWF {total_debt:,}")
        with c2:
            st.metric("Monthly interest cost", f"RWF {int(total_mc):,}")
        with c3:
            st.metric("% of income on interest", f"{total_mc / max(income, 1) * 100:.1f}%")

        if danger:
            st.markdown(f"""
            <div class="warn">
                ⚠️ <strong>Debt trap warning:</strong> You are paying RWF {int(total_mc):,}/month
                just in interest — {total_mc / max(income, 1) * 100:.0f}% of your income.
                A moneylender charges 10% per month = 120% per year. Pay this off first.
            </div>""", unsafe_allow_html=True)

        st.markdown('<p class="section-title">Your debts — ranked by interest rate (pay highest first)</p>',
                    unsafe_allow_html=True)

        for i, d in enumerate(ranked):
            amt    = d.get("amount_rwf", 0)
            rate   = d.get("rate_annual", 0)
            mc     = monthly_interest_cost(amt, rate)
            pay    = min(int(income * 0.30), int(amt / 6))
            months = debt_payoff_months(amt, pay, rate)
            is_dan = rate >= 0.60
            color  = "#FF6B6B" if is_dan else "#F0883E" if rate >= 0.20 else "#4EA3E0"
            label  = "⚠️ PAY FIRST" if is_dan else "HIGH" if rate >= 0.20 else "NORMAL"

            st.markdown(f"""
            <div class="debt-card">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="color:{color};font-weight:700;font-size:0.95rem">{d.get('source', 'Debt')} — {label}</span>
                    <span style="color:#8B949E;font-size:0.82rem">Priority #{i + 1}</span>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-top:10px;font-size:0.82rem">
                    <div><span style="color:#8B949E">Amount owed</span><br><strong style="color:#C9D1D9">RWF {int(amt):,}</strong></div>
                    <div><span style="color:#8B949E">Interest rate</span><br><strong style="color:{color}">{rate * 100:.0f}% per year</strong></div>
                    <div><span style="color:#8B949E">Monthly interest</span><br><strong style="color:#FF6B6B">RWF {int(mc):,}</strong></div>
                    <div><span style="color:#8B949E">Recommended payment</span><br><strong style="color:#56D364">RWF {pay:,}/month</strong></div>
                    <div><span style="color:#8B949E">Paid off in</span><br><strong style="color:#C9D1D9">{months} months</strong></div>
                </div>
            </div>""", unsafe_allow_html=True)

            if st.button(f"Mark as paid off — {d.get('source', 'Debt')}", key=f"del_debt_{i}"):
                remove_debt(username, debts.index(d))
                st.success("Debt removed!")
                st.rerun()

        st.markdown(f"""
        <div class="tip">
            💡 <strong>Avalanche method:</strong> Always pay the minimum on all debts,
            then put every extra RWF toward the highest-rate debt first.
            This saves the most money overall.
        </div>""", unsafe_allow_html=True)

    else:
        st.markdown('<div class="info">✅ No debts recorded. Add any debts you have below.</div>',
                    unsafe_allow_html=True)

    st.divider()
    st.markdown('<p class="section-title">Add a debt</p>', unsafe_allow_html=True)

    with st.form("add_debt"):
        c1, c2, c3 = st.columns(3)
        with c1:
            source = st.selectbox(
                "Where is this debt from?",
                list(DEBT_SOURCES.keys()),
                format_func=lambda k: DEBT_SOURCES[k]["name"],
            )
        with c2:
            amount = st.number_input("Amount owed (RWF)", 0, 10000000, 50000, 5000)
        with c3:
            custom_rate = st.number_input(
                "Interest rate (% per year)",
                0.0, 200.0,
                float(DEBT_SOURCES[source]["rate_annual"] * 100),
                0.5,
            )
        st.caption(DEBT_SOURCES[source]["note"])
        submitted = st.form_submit_button("➕ Add Debt", use_container_width=True)

    if submitted and amount > 0:
        add_debt(username, {
            "source":      DEBT_SOURCES[source]["name"],
            "amount_rwf":  amount,
            "rate_annual": custom_rate / 100,
        })
        st.success("Debt added.")
        st.rerun()