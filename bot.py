import time
import ccxt
import os
import pandas as pd
import requests
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from datetime import timedelta

# --- CONFIGURATION ---
VERSION = "5.7.1"

# Babasahin nito ang API keys mula sa Render Environment Variables o gagamit ng fallback kung nasa local PC
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')
BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.environ.get('BINANCE_API_SECRET', '')

# Initialize CCXT Binance exchange (gagamit ng keys kung meron, o public data kung wala)
exchange = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_API_SECRET,
    'enableRateLimit': True
})

FEE_RATE = 0.001
TRADE_SIZE = 75.0
MAX_POS = 5 
TIMEFRAME = '1m'
WATCHLIST = [
    "BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOT", "LINK", "INJ", "APT",
    "MATIC", "AVAX", "TIA", "NEAR", "ATOM", "UNI", "FIL", "ARB", "OP", "RENDER",
    "ICP", "LDO", "FET", "GALA", "SAND", "MANA", "AXS", "PEPE", "SHIB", "DOGE",
    "WIF", "BONK", "FLOKI", "SUI", "PYTH"
]

STATE = {
    "cash_balance": 500.0,
    "positions": {},
    "total_trades": 0,
    "win_trades": 0,
    "loss_trades": 0,
    "start_time": time.time(),
    "start_balance": 500.0,
    "banked_profit": 0.0
}

def get_stats_data():
    total_trades = STATE["win_trades"] + STATE["loss_trades"]
    win_rate = (STATE["win_trades"] / total_trades * 100) if total_trades > 0 else 0
    return win_rate, total_trades

def safe_fetch_ohlcv(symbol, timeframe, limit=250):
    try: return exchange.fetch_ohlcv(f"{symbol}/USDT", timeframe=timeframe, limit=limit)
    except: return None

def get_indicators(symbol):
    ohlcv = safe_fetch_ohlcv(symbol, TIMEFRAME, 250)
    if ohlcv is None: return 50, 0
    try:
        df = pd.DataFrame(ohlcv, columns=['t', 'o', 'h', 'l', 'c', 'v'])
        rsi = RSIIndicator(close=df['c'], window=14).rsi().iloc[-1]
        ema200 = EMAIndicator(close=df['c'], window=200).ema_indicator().iloc[-1]
        return rsi, ema200
    except: return 50, 0

def send_telegram_msg(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    win_rate, _ = get_stats_data()
    full_msg = (f"{message}\n\n"
                f"📊 STATS: {STATE['win_trades']}W-{STATE['loss_trades']}L | WR: {win_rate:.2f}%\n"
                f"💰 Saved Profit: ${STATE['banked_profit']:.2f}")
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={full_msg}"
        requests.get(url, timeout=5)
    except: pass

def run_bot():
    print(f"[+] Sniper Bot {VERSION} (RSI 30 + Optimized Stats) Active...")
    try:
        while True:
            to_sell = []
            total_pos_value = 0.0
            
            for symbol, pos in STATE["positions"].items():
                ohlcv = safe_fetch_ohlcv(symbol, TIMEFRAME, 1)
                if ohlcv is None: continue 
                curr_price = ohlcv[0][4]
                pnl = ((curr_price - pos['entry_price']) / pos['entry_price']) * 100
                total_pos_value += (pos['amount'] * curr_price)
                
                if pnl > pos.get('max_pnl', 0): pos['max_pnl'] = pnl
                if pos.get('max_pnl', 0) > 0.5 and pnl < pos['max_pnl'] - 0.3: to_sell.append(symbol)
                elif pnl <= -3.5: to_sell.append(symbol)
            
            for s in to_sell:
                pos = STATE["positions"][s]
                ohlcv_sell = safe_fetch_ohlcv(s, TIMEFRAME, 1)
                if ohlcv_sell is None: continue
                curr_price = ohlcv_sell[0][4]
                
                sell_value = (pos['amount'] * curr_price) * (1 - FEE_RATE)
                profit = sell_value - (pos['amount'] * pos['entry_price'])
                
                if profit > 0:
                    STATE["banked_profit"] += profit
                    STATE["win_trades"] += 1
                else:
                    STATE["loss_trades"] += 1
                
                STATE["cash_balance"] += sell_value
                STATE["total_trades"] += 1
                
                send_telegram_msg(f"🚀 SOLD: {s}\n💵 Profit: ${profit:.2f}")
                del STATE["positions"][s]

            if len(STATE["positions"]) < MAX_POS and STATE["cash_balance"] >= TRADE_SIZE:
                for coin in WATCHLIST:
                    if coin not in STATE["positions"]:
                        rsi, ema200 = get_indicators(coin)
                        ohlcv = safe_fetch_ohlcv(coin, TIMEFRAME, 1)
                        if ohlcv and ohlcv[0][4] > ema200 and rsi < 30:
                            price = ohlcv[0][4]
                            amount = (TRADE_SIZE * (1 - FEE_RATE)) / price
                            STATE["cash_balance"] -= TRADE_SIZE
                            STATE["positions"][coin] = {"entry_price": price, "amount": amount, "max_pnl": 0}
                            send_telegram_msg(f"✅ BOUGHT {coin} at ${price:.4f}")
                            break

            total_assets = STATE["cash_balance"] + total_pos_value
            kita = total_assets - STATE["start_balance"]
            win_rate, _ = get_stats_data()
            
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"=== SNIPER BOT {VERSION} ===")
            print(f"TIME: {time.strftime('%H:%M:%S')} | RUNTIME: {str(timedelta(seconds=int(time.time() - STATE['start_time'])))}")
            print(f"WIN: {STATE['win_trades']}W | LOSS: {STATE['loss_trades']}L | WR: {win_rate:.2f}%")
            print(f"ASSETS: ${total_assets:.2f} | KITA: ${kita:>+.2f} | SAVED: ${STATE['banked_profit']:.2f}")
            print("-" * 50)
            for s, pos in STATE["positions"].items():
                ohlcv_disp = safe_fetch_ohlcv(s, TIMEFRAME, 1)
                if ohlcv_disp:
                    pnl_disp = ((ohlcv_disp[0][4] - pos['entry_price']) / pos['entry_price']) * 100
                    print(f"{s:<8} | {pnl_disp:>+6.2f}%")
            time.sleep(10)
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    run_bot()
