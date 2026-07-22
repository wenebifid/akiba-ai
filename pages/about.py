import streamlit as st


def render():
    st.markdown('<h2 style="color:#C9A84C">ℹ️ About Akiba AI</h2>', unsafe_allow_html=True)

    st.markdown("""
    <div class="card card-gold">
        <p style="color:#C9A84C;font-weight:700;font-size:1.1rem;margin:0 0 8px">What is Akiba AI?</p>
        <p style="color:#C9D1D9;font-size:0.9rem;line-height:1.7;margin:0">
            Akiba AI is a reinforcement learning-powered financial advisor built for low-income
            informal sector workers in East Africa. It learns optimal monthly income allocation
            strategies through simulation of realistic economic conditions — including inflation,
            income shocks, microfinance debt, and investment growth.
        </p>
    </div>""", unsafe_allow_html=True)

    st.markdown('<p class="section-title">The problem we\'re solving</p>', unsafe_allow_html=True)
    for stat in [
        ("90.4%", "of Rwanda's employment is informal (NISR, 2024)"),
        ("RWF 26,000", "median monthly income of an informal worker — ~$24 USD (NISR, 2023)"),
        ("19.79%", "annual inflation in Rwanda in 2023, eroding savings faster than MoMo returns (Macrotrends, 2024)"),
        ("6%", "monthly probability of an income shock for East African households (Demirguc-Kunt et al., 2022)"),
        ("120%", "annual interest rate from informal moneylenders vs 24% from a SACCO"),
    ]:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:16px;padding:10px 0;border-bottom:1px solid #21262D">
            <span style="color:#C9A84C;font-size:1.3rem;font-weight:700;min-width:120px">{stat[0]}</span>
            <span style="color:#8B949E;font-size:0.9rem">{stat[1]}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown('<p class="section-title">The AI behind it</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <p style="color:#C9D1D9;font-size:0.9rem;line-height:1.7;margin:0">
            Four reinforcement learning algorithms were trained and compared on a custom simulation
            environment (AfricanFinanceEnv) calibrated to real East African economic data:
        </p>
        <ul style="color:#8B949E;font-size:0.88rem;line-height:2;margin:10px 0 0">
            <li><strong style="color:#4EA3E0">DQN</strong> — Deep Q-Network (value-based) · Best run mean reward: 514.09</li>
            <li><strong style="color:#BC8CFF">REINFORCE</strong> — Monte Carlo policy gradient · Best run: 405.72</li>
            <li><strong style="color:#56D364">PPO</strong> — Proximal Policy Optimization · Best run: 515.68</li>
            <li><strong style="color:#F0883E">A2C</strong> — Advantage Actor-Critic · Best run: 456.98</li>
        </ul>
        <p style="color:#8B949E;font-size:0.85rem;margin:10px 0 0">
            PPO was selected as the production model for its highest mean reward and lowest variance.
        </p>
    </div>""", unsafe_allow_html=True)

    st.markdown('<p class="section-title">Data sources</p>', unsafe_allow_html=True)
    for source, url, desc in [
        ("NISR Labour Force Survey 2023/2024", "https://www.statistics.gov.rw", "Income and employment data"),
        ("World Bank Rwanda 2024",             "https://data.worldbank.org/indicator/FR.INR.LEND?locations=RW", "Formal lending rate 15.72%"),
        ("Macrotrends Rwanda CPI",             "https://www.macrotrends.net/global-metrics/countries/rwa/rwanda/inflation-rate-cpi", "Annual inflation 19.79% (2023)"),
        ("GSMA State of Industry 2025",        "https://www.gsma.com/sotir/", "Mobile money statistics"),
        ("Demirguc-Kunt et al. 2022",          "https://doi.org/10.1596/978-1-4648-1897-4", "Global Findex — income shock frequency"),
        ("Anker Research Institute 2025",      "https://www.ankerresearchinstitute.org", "Rwanda living wage $166/month"),
    ]:
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #21262D">
            <div>
                <span style="color:#C9D1D9;font-size:0.88rem;font-weight:600">{source}</span><br>
                <span style="color:#8B949E;font-size:0.8rem">{desc}</span>
            </div>
            <a href="{url}" style="color:#4EA3E0;font-size:0.78rem;align-self:center" target="_blank">View source →</a>
        </div>""", unsafe_allow_html=True)

    st.markdown('<p class="section-title">Project</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <p style="color:#8B949E;font-size:0.88rem;margin:0">
            <strong style="color:#C9D1D9">Student:</strong> Oyinwenebi Fiderikumo<br>
            <strong style="color:#C9D1D9">Institution:</strong> African Leadership University (ALU)<br>
            <strong style="color:#C9D1D9">Year:</strong> 2025<br>
            <strong style="color:#C9D1D9">GitHub:</strong>
            <a href="https://github.com/wenebifid/akiba-ai" style="color:#4EA3E0">
                github.com/wenebifid/akiba-ai
            </a>
        </p>
    </div>""", unsafe_allow_html=True)