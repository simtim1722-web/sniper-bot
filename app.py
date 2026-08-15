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

# 4. Fast Live Crypto Prices (Gamit ang Binance All-Prices Endpoint para mabilis)
@st.cache_data(ttl=3) # I-cache ng 3 segundo para hindi ma-block ng Binance API
def get_live_crypto_prices():
    target_coins = [
        'BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOT', 'LINK', 'INJ', 'APT',
        'MATIC', 'AVAX', 'TIA', 'NEAR', 'ATOM', 'UNI', 'FIL', 'ARB', 'OP', 'RENDER',
        'ICP', 'LDO', 'FET', 'GALA', 'SAND', 'MANA', 'AXS', 'PEPE', 'SHIB', 'DOGE',
        'WIF', 'BONK', 'FLOKI', 'SUI', 'PYTH'
    ]
    prices = {}
    try:
        # Isang tawag lang sa API para makuha ang lahat ng presyo sa Binance (Mas mabilis!)
        res = requests.get("https://api.binance.com/api/v3/ticker/price", timeout=3).json()
        if isinstance(res, list):
            for item in res:
                symbol = item['symbol']
                if symbol.endswith('USDT'):
                    coin = symbol[:-4]
                    if coin in target_coins:
                        prices[coin] = float(item['price'])
    except Exception as e:
        st.warning(f"Live Feed Warning: {e}")
        
    return prices

# Logic
data = get_bot_data()
bot_status = data["status"]

# Auto-refresh bawat 5 segundo kung RUNNING
if bot_status == "RUNNING (ACTIVE)":
    # Optional simulation updater para gumalaw ang assets
    new_assets = float(data["virtual_assets"]) + 2.50
    new_profit = float(data["saved_profit"]) + 1.00
    update_bot_data(bot_status, new_assets, new_profit, data["wins"], data["losses"])
    
    st_autorefresh(interval=5000, key="auto_refresh")

# Dashboard Layout
st.title("🚀 Sniper Bot - Full Market Dashboard")

# Controls sa Sidebar o sa Taas
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

# Kunin ang mga presyo
live_prices = get_live_crypto_prices()

if live_prices:
    cols = st.columns(5)
    for i, (coin, price) in enumerate(live_prices.items()):
        with cols[i % 5]:
            st.metric(label=coin, value=f"${price:,.4f}" if price < 1 else f"${price:,.2f}")
else:
    st.info("Kumukuha ng datos mula sa Binance market...")

st.markdown("---")
st.caption("Auto-updating every 5 seconds via Binance API & Supabase.")
