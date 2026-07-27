# Akiba AI — Financial Stability Agent for East Africa

AI-powered financial advisor for boda-boda drivers, market traders,
domestic workers, and smallholder farmers in East Africa.

## Installation

git clone https://github.com/wenebifid/akiba-ai
cd akiba-ai
pip install -r requirements.txt

## Step 1 — Train the model (20-40 min)

python quick_train.py

## Step 2 — Run the web app

streamlit run app.py

## Step 3 — Run the RL simulation demo (for video)

python demo.py

## What it does

- Monthly check-ins: log income, savings, debt, shocks
- AI recommendation in English, Kinyarwanda, and Swahili
- Specific savings products: Ejo Heza (12%), SACCO (11%), MoMo (6%)
- 3-month shock recovery plan when income drops
- Debt ranking by interest rate — pay highest first
- Goal setting with projected timeline

## Data sources

- NISR Labour Force Survey 2023/2024 — income parameters
- World Bank 2024 — lending rate 15.72%
- Macrotrends — Rwanda inflation 19.79% (2023)
- GSMA 2025 — mobile money statistics
