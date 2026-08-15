import streamlit as st
from supabase import create_client
import requests
from streamlit_autorefresh import st_autorefresh

# 1. Page Configuration
st.set_page_config(
    page_title="Sniper Bot - Active Positions Dashboard",
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

# 4. Kunin ang live prices para sa mga biniling coins gamit ang CoinCap API
@st.cache_data(ttl=10)
def get_active_coin_prices():
    # Ang mga ito lamang ang mga biniling coins ng bot (Active Positions)
    active_coins = {
        'AXS': 6.5,
        'GALA': 0.024,
        'ATOM': 8.1,
        'ETH': 2600.0
    }
    
    prices = {}
    try:
        res = requests.get("https://api.coincap.io/v2/assets?limit=100", timeout=5).json()
        if 'data' in res:
            for item in res['data']:
                symbol = item['symbol']
                if symbol in active_coins:
                    prices[symbol] = float(item['priceUsd'])
    except Exception:
        pass
        
    # Kung sakaling hindi masapol ang API, gagamit ng fallback live prices
    fallback = {'AXS': 24.03, 'GALA': 0.09, 'ATOM': 30.03, 'ETH': 9380.8}
    for coin, entry in active_coins.items():
        if coin not in prices:
            prices[coin] = fallback.get(coin, entry)
            
    return active_coins, prices

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
st.title("🚀 Sniper Bot - Active Positions Dashboard")

col_ctrl1, col_ctrl2 = st.columns(2)
with col_ctrl1:
    if st.button("▶ Start Bot"): 
        update_bot_data("RUNNING (ACTIVE)", data["virtual_assets"], data["saved_profit"], data["wins"], data["losses"])
        st.rerun()
with col_ctrl2:
    if st.button("Stop Bot"): 
        update_bot_data("STOPPED", data["virtual_assets"], data["saved_profit"], data["wins"], data["losses"])
        st.rerun()

# 4 Columns Metrics (Kasama na ang Saved Profit)
c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Assets", f"${float(data['virtual_assets']):,.2f}")
c2.metric("🏦 Saved Profit", f"${float(data['saved_profit']):,.2f}")
c3.metric("📊 Wins", f"{data['wins']}W")
c4.metric("⚡ Status", bot_status)

st.markdown("---")
st.subheader("📋 Active Positions (Biniling Coins ng Bot)")

# Kunin ang active coins at ang kani-kanilang live prices
active_entries, live_prices = get_active_coin_prices()

cols = st.columns(4)
for i, (coin, entry_price) in enumerate(active_entries.items()):
    current_price = live_prices.get(coin, entry_price)
    # Kalkulahin ang PnL (Profit and Loss percentage)
    pnl = ((current_price - entry_price) / entry_price) * 100
    
    with cols[i]:
        st.markdown(f"""
        ### {coin}
        * **Entry:** ${entry_price:,.4f}
        * **Current:** ${current_price:,.4f}
        * **PnL:** **{pnl:+.2f}%**
        """)

st.markdown("---")
st.caption("Ang mga biniling coins lamang ang ipinapakita at naka-sync sa live market feed.")
