import streamlit as st
from supabase import create_client
import random
import time

# 1. Page Configuration
st.set_page_config(
    page_title="Sniper Bot - Live Mock Trading Dashboard",
    page_icon="🚀",
    layout="wide"
)

# 2. Supabase Connection Setup
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
        if response.data:
            return response.data[0]
    except Exception as e:
        st.error(f"Database Error: {e}")
    # Default fallback kung sakaling may error
    return {
        "status": "STOPPED",
        "virtual_assets": 500.00,
        "saved_profit": 0.00,
        "wins": 0,
        "losses": 0
    }

def update_bot_data(status, virtual_assets, saved_profit, wins, losses):
    try:
        supabase.table("bot_state").update({
            "status": status,
            "virtual_assets": virtual_assets,
            "saved_profit": saved_profit,
            "wins": wins,
            "losses": losses
        }).eq("id", 1).execute()
    except Exception as e:
        st.error(f"Update Error: {e}")

# Kunin ang kasalukuyang data mula sa Supabase cloud
data = get_bot_data()

bot_status = data["status"]
virtual_assets = float(data["virtual_assets"])
saved_profit = float(data["saved_profit"])
wins = int(data["wins"])
losses = int(data["losses"])
total_trades = wins + losses
win_rate = (wins / total_trades * 100) if total_trades > 0 else 0.0

# 4. Sidebar Controls
st.sidebar.markdown("⚙️ **Bot Controls**")
if st.sidebar.button("🗑️ I-reset Lahat (Reset All)"):
    update_bot_data("STOPPED", 500.00, 0.00, 0, 0)
    st.rerun()

st.sidebar.markdown("---")
if bot_status == "RUNNING (ACTIVE)":
    if st.sidebar.button("⏹ Stop Bot"):
        update_bot_data("STOPPED", virtual_assets, saved_profit, wins, losses)
        st.rerun()
else:
    if st.sidebar.button("▶ Start Mock Bot"):
        update_bot_data("RUNNING (ACTIVE)", virtual_assets, saved_profit, wins, losses)
        st.rerun()

if st.sidebar.button("🔄 I-simulate ang Paggalaw / Panalo"):
    new_assets = virtual_assets + random.choice([15.0, 35.0, -10.0, 50.0])
    new_profit = saved_profit + random.choice([5.0, 12.0, 20.0])
    new_wins = wins + 1
    update_bot_data(bot_status, new_assets, new_profit, new_wins, losses)
    st.rerun()

# 5. Main Dashboard Layout
st.title("🚀 Sniper Bot - Live Mock Trading Dashboard (Cloud Synced)")
st.markdown("Makikita rito ang paggalaw at pagbili ng mga coins ng bot sa real-time na naka-save sa Supabase Cloud.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="💰 Virtual Assets", value=f"${virtual_assets:,.2f}")

with col2:
    st.metric(label="📊 Win Rate", value=f"{win_rate:.2f}%", delta=f"{wins}W - {losses}L")

with col3:
    st.metric(label="🏦 Saved Profit", value=f"${saved_profit:,.2f}")

with col4:
    st.metric(label="⚡ Bot Status", value=bot_status)

st.markdown("---")

# 6. Active Positions Mock View
st.subheader("📋 Active Positions (Biniling Coins ng Bot)")
pos_col1, pos_col2, pos_col3, pos_col4 = st.columns(4)

with pos_col1:
    st.markdown("**AXS**\n* Entry: $6.5\n* Current: $24.03\n* PnL: **+269.72%**")
with pos_col2:
    st.markdown("**GALA**\n* Entry: $0.024\n* Current: $0.09\n* PnL: **+260.9%**")
with pos_col3:
    st.markdown("**ATOM**\n* Entry: $8.1\n* Current: $30.03\n* PnL: **+270.8%**")
with pos_col4:
    st.markdown("**ETH**\n* Entry: $2600.0\n* Current: $9380.8\n* PnL: **+260.8%**")

st.markdown("---")
st.subheader("📜 Recent Trade History")
st.info("Lahat ng galaw at trade history ay ligtas na naka-sync sa iyong Supabase database.")
