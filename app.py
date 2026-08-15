import streamlit as st
import random
import time

# --- STREAMLIT PAGE CONFIG ---
st.set_page_config(
    page_title="Sniper Bot SaaS Platform",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Sniper Bot - Live Mock Trading Dashboard")
st.markdown("Makikita rito ang paggalaw at pagbili ng mga coins ng bot sa real-time.")

# --- INITIALIZE SESSION STATE ---
if 'assets' not in st.session_state:
    st.session_state.assets = 500.00
if 'saved_profit' not in st.session_state:
    st.session_state.saved_profit = 0.00
if 'wins' not in st.session_state:
    st.session_state.wins = 0
if 'losses' not in st.session_state:
    st.session_state.losses = 0
if 'bot_running' not in st.session_state:
    st.session_state.bot_running = False

available_coins = ["BTC", "ETH", "SOL", "AXS", "GALA", "ATOM", "RENDER", "DOGE", "NEAR", "XRP", "ADA", "MATIC"]

if 'active_positions' not in st.session_state:
    st.session_state.active_positions = [
        {"symbol": "AXS", "entry": 6.50, "current": 6.50, "pnl": 0.0},
        {"symbol": "GALA", "entry": 0.024, "current": 0.024, "pnl": 0.0},
        {"symbol": "ATOM", "entry": 8.10, "current": 8.10, "pnl": 0.0},
        {"symbol": "ETH", "entry": 2600.0, "current": 2600.0, "pnl": 0.0}
    ]

# --- SIDEBAR: CONTROLS & RESET ---
st.sidebar.header("⚙️ Bot Controls")
if st.sidebar.button("🗑️ I-reset Lahat (Reset All)", use_container_width=True, type="secondary"):
    st.session_state.assets = 500.00
    st.session_state.saved_profit = 0.00
    st.session_state.wins = 0
    st.session_state.losses = 0
    st.session_state.bot_running = False
    st.session_state.active_positions = [
        {"symbol": "AXS", "entry": 6.50, "current": 6.50, "pnl": 0.0},
        {"symbol": "GALA", "entry": 0.024, "current": 0.024, "pnl": 0.0},
        {"symbol": "ATOM", "entry": 8.10, "current": 8.10, "pnl": 0.0},
        {"symbol": "ETH", "entry": 2600.0, "current": 2600.0, "pnl": 0.0}
    ]
    st.rerun()

# --- MAIN DASHBOARD METRICS ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="💰 Virtual Assets", value=f"${st.session_state.assets:.2f}")
with col2:
    total_trades = st.session_state.wins + st.session_state.losses
    win_rate = (st.session_state.wins / total_trades) * 100 if total_trades > 0 else 0
    st.metric(label="📊 Win Rate", value=f"{win_rate:.2f}%", delta=f"{st.session_state.wins}W - {st.session_state.losses}L")
with col3:
    st.metric(label="🏦 Saved Profit", value=f"${st.session_state.saved_profit:.2f}")
with col4:
    status_text = "RUNNING (ACTIVE)" if st.session_state.bot_running else "STOPPED"
    st.metric(label="⚡ Bot Status", value=status_text)

st.markdown("---")

# Control Buttons
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("▶ Start Mock Bot", use_container_width=True, type="primary"):
        st.session_state.bot_running = True
        st.success("✅ Nagsimula na ang bot!")
with c2:
    if st.button("⏹ Stop Bot", use_container_width=True):
        st.session_state.bot_running = False
        st.warning("⚠️ Huminto ang bot.")
with c3:
    if st.button("🔄 I-simulate ang Paggalaw / Panalo", use_container_width=True):
        profit_add = round(random.uniform(0.40, 1.80), 2)
        st.session_state.saved_profit += profit_add
        st.session_state.assets += profit_add
        st.session_state.wins += 1
        
        new_coin = random.choice([c for c in available_coins if c not in [p['symbol'] for p in st.session_state.active_positions]])
        rand_entry = round(random.uniform(1.0, 100.0), 2)
        rand_pnl = round(random.uniform(-1.5, 2.5), 2)
        
        st.session_state.active_positions.pop(0)
        st.session_state.active_positions.append({
            "symbol": new_coin, 
            "entry": rand_entry, 
            "current": round(rand_entry * (1 + rand_pnl/100), 2), 
            "pnl": rand_pnl
        })
        st.rerun()

# --- ACTIVE POSITIONS (CLEAN LAYOUT) ---
st.subheader("📋 Active Positions (Biniling Coins ng Bot)")

cols = st.columns(len(st.session_state.active_positions))
for i, pos in enumerate(st.session_state.active_positions):
    with cols[i]:
        pnl_str = f"+{pos['pnl']}%" if pos['pnl'] >= 0 else f"{pos['pnl']}%"
        card_content = f"**{pos['symbol']}**\n\n- Entry: ${pos['entry']}\n- Current: ${pos['current']}\n- PnL: {pnl_str}"
        
        if pos['pnl'] >= 0:
            st.success(card_content)
        else:
            st.info(card_content)

# --- TRADE HISTORY ---
st.subheader("📜 Recent Trade History")
st.text(" [Wala pang history dahil na-reset ang sistema]")

# Auto-refresh kung naka-start ang bot
if st.session_state.bot_running:
    time.sleep(3)
    for p in st.session_state.active_positions:
        p['pnl'] = round(p['pnl'] + random.uniform(-0.2, 0.3), 2)
        p['current'] = round(p['entry'] * (1 + p['pnl']/100), 2)
    st.rerun()
