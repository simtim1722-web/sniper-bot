import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Sniper Bot v5.7.1 - Cloud Dashboard",
    page_icon="🚀",
    layout="wide"
)

VERSION = "5.7.1"
TIMEFRAME = '1m'

# Initialize CCXT Binance exchange for live prices on the website
@st.cache_resource
def get_exchange():
    return ccxt.binance({'enableRateLimit': True})

exchange = get_exchange()

# --- SESSION STATE INITIALIZATION ---
if 'bot_status' not in st.session_state:
    st.session_state.bot_status = "STOPPED"
if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 500.00
if 'banked_profit' not in st.session_state:
    st.session_state.banked_profit = 0.00
if 'wins' not in st.session_state:
    st.session_state.wins = 0
if 'losses' not in st.session_state:
    st.session_state.losses = 0
if 'positions' not in st.session_state:
    # Halimbawang active positions para magtugma sa hitsura
    st.session_state.positions = {
        "AXS": {"entry_price": 6.50, "amount": 11.53},
        "GALA": {"entry_price": 0.0240, "amount": 3125.0},
        "ATOM": {"entry_price": 8.10, "amount": 9.25},
        "ETH": {"entry_price": 2600.0, "amount": 0.028}
    }

# --- HEADER & CONTROLS ---
st.title(f"🚀 Sniper Bot v{VERSION} - Cloud Dashboard")

col_b1, col_b2, col_b3, col_b4 = st.columns(4)

with col_b1:
    if st.button("▶ Start Bot", use_container_width=True):
        st.session_state.bot_status = "RUNNING"
        st.success("Bot status set to RUNNING!")

with col_b2:
    if st.button("⏹ Stop Bot", use_container_width=True):
        st.session_state.bot_status = "STOPPED"
        st.warning("Bot status set to STOPPED.")

with col_b3:
    if st.button("🗑️ I-reset sa Zero", use_container_width=True):
        st.session_state.cash_balance = 500.00
        st.session_state.banked_profit = 0.00
        st.session_state.wins = 0
        st.session_state.losses = 0
        st.session_state.positions = {}
        st.success("Reset completed!")

with col_b4:
    if st.button("🔍 Check Wallet Balance", use_container_width=True):
        st.info(f"Wallet Cash Balance: ${st.session_state.cash_balance:.2f}")

st.markdown("---")

# --- CALCULATE TOTAL ASSETS & PNL ---
total_pos_value = 0.0
display_positions = []

for symbol, pos in st.session_state.positions.items():
    try:
        ticker = exchange.fetch_ticker(f"{symbol}/USDT")
        curr_price = ticker['last']
    except:
        curr_price = pos['entry_price']
        
    pos_value = pos['amount'] * curr_price
    total_pos_value += pos_value
    pnl = ((curr_price - pos['entry_price']) / pos['entry_price']) * 100
    
    display_positions.append({
        "Asset": symbol,
        "Entry": f"${pos['entry_price']:.4f}",
        "Current (Real)": f"${curr_price:.4f}",
        "PnL": f"{pnl:+.2f}%"
    })

total_assets = st.session_state.cash_balance + total_pos_value
total_trades = st.session_state.wins + st.session_state.losses
win_rate = (st.session_state.wins / total_trades * 100) if total_trades > 0 else 0.0

# --- METRICS DISPLAY ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("💰 Assets", f"${total_assets:.2f}")
m2.metric("🏦 Saved Profit", f"${st.session_state.banked_profit:.2f}")
m3.metric("📊 Win Rate", f"{win_rate:.2f}%")
m4.metric("📈 Trades Breakdown", f"{st.session_state.wins}W - {st.session_state.losses}L")

# Status Alert Box
if st.session_state.bot_status == "RUNNING":
    st.success(f"⚡ Status: **{st.session_state.bot_status}** (Cloud Dashboard Live)")
else:
    st.error(f"⚡ Status: **{st.session_state.bot_status}**")

st.markdown("---")

# --- ACTIVE POSITIONS TABLE ---
st.subheader("📋 Active Positions (RSI 30 + Cloud Synced Watchlist)")

if display_positions:
    df_positions = pd.DataFrame(display_positions)
    st.table(df_positions)
else:
    st.info("Wala pang active positions sa ngayon.")
