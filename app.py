import streamlit as st
from supabase import create_client
import random
import requests
from streamlit_autorefresh import st_autorefresh

# 1. Page Configuration
st.set_page_config(
    page_title="Sniper Bot - Full Market Dashboard",
    page_icon="🚀",
    layout="wide"
)

# 2. Supabase Connection
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# 3. Database Functions
def get_bot_data():
    try:
        response = supabase.table("bot_state").select("*").eq("id", 1).execute()
        if response.data: return response.data[0]
    except: pass
    return {"status": "STOPPED", "virtual_assets": 500.00, "saved_profit": 0.00, "wins": 0, "losses": 0}

def update_bot_data(status, virtual_assets, saved_profit, wins, losses):
    try:
        supabase.table("bot_state").update({
            "status": status, "virtual_assets": virtual_assets,
            "saved_profit": saved_profit, "wins": wins, "losses": losses
        }).eq("id", 1).execute()
    except: pass

# 4. Live Crypto Prices
def get_live_crypto_prices():
    symbols = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT', 'INJUSDT', 'APTUSDT',
        'MATICUSDT', 'AVAXUSDT', 'TIAUSDT', 'NEARUSDT', 'ATOMUSDT', 'UNIUSDT', 'FILUSDT', 'ARBUSDT', 'OPUSDT', 'RENDERUSDT',
        'ICPUSDT', 'LDOUSDT', 'FETUSDT', 'GALAUSDT', 'SANDUSDT', 'MANAUSDT', 'AXSUSDT', 'PEPEUSDT', 'SHIBUSDT', 'DOGEUSDT',
        'WIFUSDT', 'BONKUSDT', 'FLOKIUSDT', 'SUIUSDT', 'PYTHUSDT'
    ]
    prices = {}
    try:
        for symbol in symbols:
            res = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}", timeout=2).json()
            if 'price' in res:
                prices[symbol.replace('USDT', '')] = float(res['price'])
    except: pass
    return prices

# Logic
data = get_bot_data()
live_prices = get_live_crypto_prices()
bot_status = data["status"]

if bot_status == "RUNNING (ACTIVE)":
    st_autorefresh(interval=5000, key="auto_refresh")

# Dashboard Layout
st.title("🚀 Sniper Bot - Full Market Dashboard")

# Controls
col_ctrl1, col_ctrl2 = st.columns(2)
with col_ctrl1:
    if st.button("▶ Start Bot"): update_bot_data("RUNNING (ACTIVE)", data["virtual_assets"], data["saved_profit"], data["wins"], data["losses"])
with col_ctrl2:
    if st.button("⏹ Stop Bot"): update_bot_data("STOPPED", data["virtual_assets"], data["saved_profit"], data["wins"], data["losses"])

# Metrics
c1, c2, c3 = st.columns(3)
c1.metric("💰 Assets", f"${float(data['virtual_assets']):,.2f}")
c2.metric("🏦 Profit", f"${float(data['saved_profit']):,.2f}")
c3.metric("⚡ Status", bot_status)

st.markdown("---")
st.subheader("📋 Market Watch (Live)")

# Grid View for 35+ Coins
coins_list = list(live_prices.keys())
cols = st.columns(5) # 5 columns para hindi siksikan
for i, coin in enumerate(coins_list):
    price = live_prices[coin]
    with cols[i % 5]:
        st.info(f"**{coin}**: ${price:,.4f}")

st.markdown("---")
st.caption("Auto-updating every 5 seconds via Binance API & Supabase.")
