import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.user_data import load_user, PROFESSIONS


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
    history  = data.get("history", [])
    prof     = PROFESSIONS.get(data.get("profession", "market_trader"), {})

    st.markdown(f'<h2 style="color:#C9A84C">📊 My Dashboard</h2>', unsafe_allow_html=True)
    st.caption(f"{data.get('name', '')} · {prof.get('label', '')} · {len(history)} months tracked")

    if len(history) < 2:
        st.info("Complete at least 2 monthly check-ins to see your dashboard.")
        if st.button("Go to Monthly Check-in"):
            st.session_state.page = "checkin"
            st.rerun()
        return

    months   = [h.get("month", i + 1) for i, h in enumerate(history)]
    incomes  = [h.get("income", 0) for h in history]
    savings  = [h.get("savings", 0) for h in history]
    debts    = [h.get("debt", 0) for h in history]
    invests  = [h.get("investment", 0) for h in history]
    emergencies = [h.get("emergency", 0) for h in history]
    net_worth   = [s + inv + emg - d for s, inv, emg, d in zip(savings, invests, emergencies, debts)]

    # Summary metrics
    latest  = history[-1]
    prev    = history[-2] if len(history) > 1 else history[-1]
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        delta = latest.get("income", 0) - prev.get("income", 0)
        st.metric("Monthly income", f"RWF {latest.get('income', 0):,}", delta=f"RWF {delta:+,.0f}")
    with c2:
        delta = latest.get("savings", 0) - prev.get("savings", 0)
        st.metric("Total savings", f"RWF {latest.get('savings', 0):,}", delta=f"RWF {delta:+,.0f}")
    with c3:
        delta = latest.get("debt", 0) - prev.get("debt", 0)
        st.metric("Total debt", f"RWF {latest.get('debt', 0):,}", delta=f"RWF {delta:+,.0f}", delta_color="inverse")
    with c4:
        nw    = net_worth[-1]
        delta = net_worth[-1] - net_worth[-2] if len(net_worth) > 1 else 0
        st.metric("Net worth", f"RWF {nw:,}", delta=f"RWF {delta:+,.0f}")

    st.divider()

    # Net worth chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=net_worth, mode="lines+markers",
        name="Net worth", line=dict(color="#56D364", width=2),
        fill="tozeroy", fillcolor="rgba(86,211,100,0.1)",
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="#FF6B6B", opacity=0.5)
    fig.update_layout(
        title="Net Worth Over Time",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#C9D1D9"), height=280,
        xaxis=dict(title="Month", gridcolor="#21262D"),
        yaxis=dict(title="RWF", gridcolor="#21262D"),
        margin=dict(t=40, b=40, l=40, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Savings vs debt chart
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=months, y=savings,  name="Savings",  marker_color="#4EA3E0", opacity=0.8))
    fig2.add_trace(go.Bar(x=months, y=debts,    name="Debt",     marker_color="#FF6B6B", opacity=0.8))
    fig2.add_trace(go.Bar(x=months, y=invests,  name="Investments", marker_color="#F0883E", opacity=0.8))
    fig2.update_layout(
        title="Savings, Debt and Investments by Month",
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#C9D1D9"), height=280,
        xaxis=dict(title="Month", gridcolor="#21262D"),
        yaxis=dict(title="RWF", gridcolor="#21262D"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=40, b=40, l=40, r=20),
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Income trend
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=months, y=incomes, mode="lines+markers",
        name="Income", line=dict(color="#C9A84C", width=2),
    ))
    shock_months = [h.get("month", i + 1) for i, h in enumerate(history) if h.get("shock")]
    shock_incomes = [h.get("income", 0) for h in history if h.get("shock")]
    if shock_months:
        fig3.add_trace(go.Scatter(
            x=shock_months, y=shock_incomes, mode="markers",
            name="Shock months", marker=dict(color="#FF6B6B", size=10, symbol="x"),
        ))
    fig3.update_layout(
        title="Monthly Income (X = shock month)",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#C9D1D9"), height=260,
        xaxis=dict(title="Month", gridcolor="#21262D"),
        yaxis=dict(title="RWF", gridcolor="#21262D"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=40, b=40, l=40, r=20),
    )
    st.plotly_chart(fig3, use_container_width=True)

    # History table
    st.markdown('<p class="section-title">📋 Monthly history</p>', unsafe_allow_html=True)
    import pandas as pd
    rows = []
    for h in history:
        rows.append({
            "Month":      h.get("month", ""),
            "Date":       h.get("date", ""),
            "Income":     f"RWF {h.get('income', 0):,}",
            "Savings":    f"RWF {h.get('savings', 0):,}",
            "Debt":       f"RWF {h.get('debt', 0):,}",
            "Investment": f"RWF {h.get('investment', 0):,}",
            "Shock":      "⚡ Yes" if h.get("shock") else "No",
            "Note":       h.get("note", ""),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)