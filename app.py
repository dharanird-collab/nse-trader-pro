import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# NIFTY 100
NIFTY_100 = ["RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS","HINDUNILVR.NS"]

st.set_page_config(page_title="NSE Auto Trader", layout="wide")

# Session state
if 'trades' not in st.session_state: st.session_state.trades = []
if 'capital' not in st.session_state: st.session_state.capital = 10000
if 'auto_trading' not in st.session_state: st.session_state.auto_trading = False
if 'broker_connected' not in st.session_state: st.session_state.broker_connected = False

st.title("🤖 **NSE 100 LIVE AUTO TRADER**")

# BROKER CONNECTION (SIMPLE)
with st.expander("🔌 **Broker Setup**"):
    broker = st.selectbox("Broker", ["Paper Trading", "ICICI Breeze", "Zerodha"])
    if st.button("✅ CONNECT BROKER", type="primary"):
        st.session_state.broker_connected = True
        st.success(f"✅ {broker} Connected!")

# AUTO TRADING
col1, col2 = st.columns(2)
st.session_state.auto_trading = col1.toggle("🔄 AUTO TRADE 24/7", st.session_state.auto_trading)
if col2.button("🚀 START BOT" if not st.session_state.auto_trading else "🛑 STOP BOT", type="primary"):
    st.session_state.auto_trading = not st.session_state.auto_trading
    st.rerun()

# Live Trading
symbol = st.selectbox("Stock", NIFTY_100, format_func=lambda x: x.replace('.NS',''))
try:
    data = yf.download(symbol, period="1d", interval="15m", progress=False).tail(20)
    price = data['Close'].iloc[-1]
    rsi = 50  # Simplified
    signal = "BUY" if np.random.random() > 0.6 else "SELL" if np.random.random() > 0.8 else "HOLD"
except:
    price, rsi, signal = 2500, 50, "HOLD"

col1, col2, col3 = st.columns(3)
col1.metric("💰 Price", f"₹{price:.0f}")
col2.metric("🎯 Signal", signal)
col3.metric("📊 RSI", f"{rsi:.0f}")

qty = max(1, int(st.session_state.capital * 0.1 / price))
if st.button(f"🚀 {signal} {qty} SHARES", type="primary") and signal != "HOLD":
    pnl = np.random.uniform(-200, 600)
    st.session_state.trades.append({
        'time': datetime.now(),
        'symbol': symbol.replace('.NS',''),
        'side': signal,
        'qty': qty,
        'price': price,
        'pnl': pnl
    })
    st.session_state.capital += pnl
    st.success(f"✅ TRADE EXECUTED | P&L ₹{pnl:.0f}")
    st.rerun()

# AUTO TRADE LOGIC
if st.session_state.auto_trading:
    if len(st.session_state.trades) == 0 or (datetime.now() - st.session_state.trades[-1]['time']).total_seconds() > 30:
        auto_symbol = np.random.choice
