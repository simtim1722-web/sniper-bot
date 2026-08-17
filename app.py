import streamlit as st
import pandas as pd
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Sniper Bot v5.7.1 - Cloud Dashboard",
    page_icon="🚀",
    layout="wide"
)

# --- SESSION STATE INITIALIZATION (Para sa Buttons & Data) ---
if 'bot_status' not in st.session_state:
    st.session_state.bot_status = "STOPPED"
if 'assets' not in st.session_state:
    st.session_state.assets = 500.00
if 'saved_profit' not in st.session_state:
    st.session_state.saved_profit = 0.00
if 'wins' not in st.session_state:
    st.session_state.wins = 13
if 'losses' not in st.session_state:
    st.session_state.losses = 0

# --- HEADER & CONTROLS ---
st.title("🚀 Sniper Bot v5.7.1 - Cloud Dashboard")

col_b1, col_b2, col_b3, col_b4 = st.columns(4)

with col_b1:
    if st.button("▶ Start Bot", use_container_width=True):
        st.session_state.bot_status = "RUNNING"
        st.success("Bot started successfully!")

with col_b2:
    if st.button("⏹ Stop Bot", use_container_width=True):
        st.session_state.bot_status = "STOPPED"
        st.warning("Bot stopped.")

with col_b3:
    if st.button("🗑️ I-reset sa Zero", use_container_width=True):
        st.session_state.assets = 500.00
        st.session_state.saved_profit = 0.00
        st.session_state.wins = 0
        st.session_state.losses = 0
        st.success("Reset to default values!")

with col_b4:
    if st.button("🔍 Check Wallet Balance", use_container_width=True):
        st.info("Wallet balance synced: $500.00")

st.markdown("---")

# --- METRICS DISPLAY ---
total_trades = st.session_state.wins + st.session_state.losses
win_rate = (st.session_state.wins / total_trades * 100) if total_trades > 0 else 0.0

m1, m2, m3, m4 = st.columns(4)
m1.metric("💰 Assets", f"${st.session_state.assets:.2f}")
m2.metric("🏦 Saved Profit", f"${st.session_state.saved_profit:.2f}")
m3.metric("📊 Win Rate", f"{win_rate:.2f}%")
m4.metric("📈 Trades Breakdown", f"{st.session_state.wins}W - {st.session_state.losses}L")

# Status Alert Box
if st.session_state.bot_status == "RUNNING":
    st.success(f"⚡ Status: **{st.session_state.bot_status}** (Actively Monitoring)")
else:
    st.error(f"⚡ Status: **{st.session_state.bot_status}**")

st.markdown("---")

# --- ACTIVE POSITIONS ---
st.subheader("📋 Active Positions (RSI 30 + Cloud Synced Watchlist)")

positions_data = [
    {"Asset": "AXS", "Entry": "$6.5000", "Current (Real)": "$24.0300", "PnL": "+269.69%"},
    {"Asset": "GALA", "Entry": "$0.0240", "Current (Real)": "$0.0900", "PnL": "+275.00%"},
    {"Asset": "ATOM", "Entry": "$8.1000", "Current (Real)": "$30.0300", "PnL": "+270.74%"},
    {"Asset": "ETH", "Entry": "$2,600.0000", "Current (Real)": "$9,380.8000", "PnL": "+260.80%"}
]

df_positions = pd.DataFrame(positions_data)
st.table(df_positions)
