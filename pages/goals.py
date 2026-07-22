import streamlit as st
from utils.user_data import load_user, save_user, add_goal, SAVINGS_PRODUCTS, months_to_goal


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
    goals    = data.get("goals", [])
    history  = data.get("history", [])
    month_num = len(history)

    latest_savings = history[-1].get("savings", 0) if history else 0
    latest_income  = history[-1].get("income",  0) if history else 30000

    st.markdown('<h2 style="color:#C9A84C">🎯 My Goals</h2>', unsafe_allow_html=True)

    # Existing goals
    if goals:
        st.markdown('<p class="section-title">Your current goals</p>', unsafe_allow_html=True)
        for i, g in enumerate(goals):
            target  = g.get("target_rwf", 0)
            current = g.get("current_rwf", 0)
            product = g.get("savings_product", "mtn_momo")
            rate    = SAVINGS_PRODUCTS.get(product, {}).get("rate", 0.06)
            monthly = int(latest_income * 0.15)
            mn      = months_to_goal(current, target, monthly, rate)
            pct     = min(current / max(target, 1), 1.0)
            on_track= mn <= g.get("deadline_months", 24) - month_num

            st.markdown(f"""
            <div class="card card-gold">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                    <span style="color:#C9A84C;font-weight:700;font-size:1rem">🎯 {g.get('name', '')}</span>
                    <span style="color:{'#56D364' if on_track else '#FF6B6B'};font-size:0.82rem">
                        {'✅ On track' if on_track else f'⚠️ {mn} months needed'}
                    </span>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:8px">
                    <span style="color:#8B949E">Target: <strong style="color:#C9D1D9">RWF {target:,}</strong></span>
                    <span style="color:#8B949E">Saved: <strong style="color:#56D364">RWF {current:,}</strong></span>
                    <span style="color:#8B949E">Saving via: <strong style="color:#C9D1D9">{SAVINGS_PRODUCTS.get(product, {}).get('name', product)}</strong></span>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:0.82rem">
                    <span style="color:#8B949E">Saving RWF {monthly:,}/month → done in ~{mn} months</span>
                    <span style="color:#4EA3E0">Deadline: {g.get('deadline_months', 24)} months</span>
                </div>
            </div>""", unsafe_allow_html=True)
            st.progress(pct)

            c1, c2 = st.columns(2)
            with c1:
                new_current = st.number_input(
                    f"Update saved amount for '{g.get('name', '')}'",
                    0, int(target * 2), int(current), 1000,
                    key=f"goal_upd_{i}",
                )
            with c2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(f"Update goal {i + 1}", key=f"upd_btn_{i}"):
                    data["goals"][i]["current_rwf"] = new_current
                    save_user(username, data)
                    st.success("Updated!")
                    st.rerun()
    else:
        st.info("You have no goals yet. Add one below.")

    st.divider()
    st.markdown('<p class="section-title">Add a new goal</p>', unsafe_allow_html=True)

    with st.form("new_goal"):
        c1, c2 = st.columns(2)
        with c1:
            goal_name    = st.text_input("Goal name", placeholder="e.g. School fees, Motorcycle, Emergency fund")
            target_rwf   = st.number_input("Target amount (RWF)", 10000, 50000000, 500000, 10000)
        with c2:
            deadline     = st.slider("Deadline (months from now)", 1, 60, 12)
            product      = st.selectbox(
                "Save using",
                list(SAVINGS_PRODUCTS.keys()),
                format_func=lambda k: f"{SAVINGS_PRODUCTS[k]['name']} ({SAVINGS_PRODUCTS[k]['rate_display']})",
            )
        note = st.text_area("Notes (optional)", height=60)
        submitted = st.form_submit_button("➕ Add Goal", use_container_width=True)

    if submitted:
        if not goal_name:
            st.error("Please enter a goal name.")
        else:
            add_goal(username, {
                "name":            goal_name,
                "target_rwf":      target_rwf,
                "current_rwf":     latest_savings if len(goals) == 0 else 0,
                "savings_product": product,
                "deadline_months": deadline,
                "note":            note,
            })
            st.success(f"✅ Goal '{goal_name}' added!")
            st.rerun()