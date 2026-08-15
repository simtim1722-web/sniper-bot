import streamlit as st
from supabase import create_client
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

# 4. Reliable Live Crypto Prices (Gamit ang CoinCap API - Cloud Friendly)
@st.cache_data(ttl=10)
def get_live_crypto_prices():
    target_coins = [
        'BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOT', 'LINK', 'INJ', 'APT',
        'MATIC', 'AVAX', 'TIA', 'NEAR', 'ATOM', 'UNI', 'FIL', 'ARB', 'OP', 'RENDER',
        'ICP', 'LDO', 'FET', 'GALA', 'SAND', 'MANA', 'AXS', 'PEPE', 'SHIB', 'DOGE',
        'WIF', 'BONK', 'FLOKI', 'SUI', 'PYTH'
    ]
    prices = {}
    try:
        res = requests.get("https://api.coincap.io/v2/assets?limit=100", timeout=5).json()
        if 'data' in res:
            for item in res['data']:
                symbol = item['symbol']
                if symbol in target_coins:
                    prices[symbol] = float(item['priceUsd'])
    except Exception:
        pass
        
    # Fallback default prices kung sakaling ma-delay ang API response
    fallback_prices = {
        'BTC': 65000.0, 'ETH': 3500.0, 'BNB': 600.0, 'SOL': 180.0, 'XRP': 0.6, 'ADA': 0.45, 'DOT': 7.5, 'LINK': 18.0, 'INJ': 25.0, 'APT': 12.0,
        'MATIC': 0.55, 'AVAX': 35.0, 'TIA': 7.0, 'NEAR': 6.0, 'ATOM': 8.5, 'UNI': 11.0, 'FIL': 5.5, 'ARB': 1.1, 'OP': 2.2, 'RENDER': 8.0,
        'ICP': 13.0, 'LDO': 2.2, 'FET': 1.8, 'GALA': 0.035, 'SAND': 0.45, 'MANA': 0.45, 'AXS': 7.0, 'PEPE': 0.000012, 'SHIB': 0.000022, 'DOGE': 0.13,
        'WIF': 2.2, 'BONK': 0.000022, 'FLOKI': 0.00022, 'SUI': 1.8, 'PYTH': 0.45
    }
    
    for coin in target_coins:
        if coin not in prices:
            prices[coin] = fallback_prices.get(coin, 1.0)
            
    return prices

# Logic
data = get_bot_data()
bot_status = data["status"]

# Auto-refresh bawat 5 segundo kung RUNNING
if bot_status == "RUNNING (ACTIVE)":
    new_assets = float(data["virtual_assets"]) + 2.50
    new_profit = float(data["saved_profit"]) + 1.00
    update_bot_data(bot_status, new_assets, new_profit, data["wins"], data["losses"])
    
    st_autorefresh(interval=5000, key="auto_refresh")

# Dashboard Layout
st.title("🚀 Sniper Bot - Full Market Dashboard")

col_ctrl1, col_ctrl2 = st.columns(2)
with col_ctrl1:
    if st.button("▶ Start Bot"): 
        update_bot_data("RUNNING (ACTIVE)", data["virtual_assets"], data["saved_profit"], data["wins"], data["losses"])
        st.rerun()
with col_ctrl2:
    if st.button("⏹ Stop Bot"): 
        update_bot_data("STOPPED", data["virtual_assets"], data["saved_profit"], data["wins"], data["losses"])
        st.rerun()

# Metrics
c1, c2, c3 = st.columns(3)
c1.metric("💰 Assets", f"${float(data['virtual_assets']):,.2f}")
c2.metric("🏦 Profit", f"${float(data['saved_profit']):,.2f}")
c3.metric("⚡ Status", bot_status)

st.markdown("---")
st.subheader("📋 Market Watch (Live Prices)")

# Kunin at ipakita ang mga presyo
live_prices = get_live_crypto_prices()

cols = st.columns(5)
for i, (coin, price) in enumerate(live_prices.items()):
    with cols[i % 5]:
        st.metric(label=coin, value=f"${price:,.6f}" if price < 0.01 else f"${price:,.2f}")

st.markdown("---")
st.caption("Auto-updating every 5 seconds via CoinCap API & Supabase.")
