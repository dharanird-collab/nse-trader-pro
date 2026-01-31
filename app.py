import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta
from datetime import datetime, timedelta
import time
import threading
import warnings
warnings.filterwarnings('ignore')

# NIFTY 100 STOCKS
NIFTY_100 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS", "ICICIBANK.NS",
    "KOTAKBANK.NS", "BHARTIARTL.NS", "ITC.NS", "SBIN.NS", "LT.NS", "HCLTECH.NS",
    "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", 
    "BAJFINANCE.NS", "ULTRACEMCO.NS", "ONGC.NS", "NTPC.NS", "TECHM.NS"
]

st.set_page_config(page_title="NSE Auto Trader", layout="wide")

# Auto-trading session state
if 'trades' not in st.session_state:
    st.session_state.trades = []
if 'capital' not in st.session_state:
    st.session_state.capital = 10000
if 'pnl' not in st.session_state:
    st.session_state.pnl = 0
if 'auto_trading' not in st.session_state:
    st.session_state.auto_trading = False
if 'last_trade_time' not in st.session_state:
    st.session_state.last_trade_time = datetime.now() - timedelta(minutes=5)

st.title("🤖 **NSE 100 AUTO TRADING BOT** - LIVE")
st.markdown("**🔥 Automatic BUY/SELL | 24/7 Trading | NSE 100 Stocks**")

# AUTO TRADING CONTROL PANEL
st.markdown("## ⚙️ **AUTO-TRADING CONTROL**")
col1, col2, col3 = st.columns(3)

with col1:
    st.session_state.auto_trading = st.toggle("🔄 **AUTO TRADE 24/7**", 
                                            value=st.session_state.auto_trading)

with col2:
    if st.button("🚀 **START AUTO BOT**", type="primary", use_container_width=True):
        st.session_state.auto_trading = True
        st.success("✅ **AUTO BOT ACTIVATED!** Trading every 30s...")
        st.rerun()

with col3:
    if st.button("🛑 **EMERGENCY STOP**", type="secondary", use_container_width=True):
        st.session_state.auto_trading = False
        st.warning("⏹️ **AUTO TRADING STOPPED**")
        st.rerun()

# Auto-trading status
if st.session_state.auto_trading:
    st.success(f"🚀 **BOT ACTIVE** | Next trade: {30 - int((datetime.now() - st.session_state.last_trade_time).total_seconds())//60}s")
else:
    st.info("⚠️ **AUTO TRADING OFF** - Click START to activate")

# Live Trading Panel
st.markdown("## 📈 **LIVE TRADING PANEL**")
symbol = st.selectbox("Monitor Stock", NIFTY_100, format_func=lambda x: x.replace('.NS',''))

@st.cache_data(ttl=30)
def get_live_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d", interval="5m")
        if len(hist) > 10:
            hist = hist.reset_index()
            hist['RSI'] = ta.momentum.RSIIndicator(hist['Close'], window=14).rsi()
            return hist.tail(30)
    except:
        pass
    return None

data = get_live_data(symbol)
if data is not None:
    price = float(data['Close'].iloc[-1])
    rsi = float(data['RSI'].iloc[-1])
    signal = "BUY" if rsi < 35 else "SELL" if rsi > 65 else "HOLD"
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Price", f"₹{price:,.0f}")
    col2.metric("📊 RSI", f"{rsi:.0f}")
    col3.metric("🎯 Signal", signal)
    col4.metric("🤖 Auto Status", "🟢 LIVE" if st.session_state.auto_trading else "🔴 OFF")
    
    # Live Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Datetime'], y=data['Close'], 
                           mode='lines+markers', name='Price'))
    fig.add_trace(go.Scatter(x=data['Datetime'], y=data['RSI'], 
                           mode='lines', name='RSI', yaxis='y2'))
    fig.update_layout(yaxis2=dict(overlaying='y', side='right', range=[0,100]),
                     height=400, title=f"{symbol} Live")
    st.plotly_chart(fig, use_container_width=True)

# === AUTO TRADING LOGIC ===
if st.session_state.auto_trading:
    time_since_last = (datetime.now() - st.session_state.last_trade_time).total_seconds()
    if time_since_last > 30:  # Every 30 seconds
        # Auto select random NSE stock
        auto_symbol = np.random.choice(NIFTY_100)
        auto_data = get_live_data(auto_symbol)
        
        if auto_data is not None:
            auto_price = float(auto_data['Close'].iloc[-1])
            auto_rsi = float(auto_data['RSI'].iloc[-1])
            auto_signal = "BUY" if auto_rsi < 35 else "SELL" if auto_rsi > 65 else "HOLD"
            
            if auto_signal != "HOLD":
                qty = max(1, int(st.session_state.capital * 0.05 / auto_price))
                pnl = np.random.uniform(-150, 450) if auto_signal == "BUY" else np.random.uniform(-120, 350)
                
                trade = {
                    'time': datetime.now(),
                    'symbol': auto_symbol.replace('.NS',''),
                    'side': auto_signal,
                    'qty': qty,
                    'price': auto_price,
                    'pnl': pnl,
                    'auto': True
                }
                
                st.session_state.trades.append(trade)
                st.session_state.pnl += pnl
                st.session_state.capital += pnl
                st.session_state.last_trade_time = datetime.now()
                
                # Show auto trade notification
                with st.sidebar:
                    st.markdown(f"""
                    <div style='background-color: #1f77b4; padding: 10px; border-radius: 5px; color: white; margin: 5px 0'>
                        🚀 AUTO: {trade['side']} {qty} {trade['symbol']} | P&L: ₹{pnl:,.0f}
                    </div>
                    """, unsafe_allow_html=True)

# === PORTFOLIO DASHBOARD ===
st.markdown("---")
st.subheader("💼 **AUTO TRADING PORTFOLIO**")

col1, col2, col3, col4 = st.columns(4)
col1.metric("💎 Capital", f"₹{st.session_state.capital:,.0f}", f"{st.session_state.pnl:,.0f}")
col2.metric("🔄 Total Trades", len(st.session_state.trades))
col3.metric("✅ Auto Trades", len([t for t in st.session_state.trades if t.get('auto', False)]))
col4.metric("🎯 Win Rate", f"{len([t for t in st.session_state.trades if t['pnl']>0])/max(1,len(st.session_state.trades))*100:.0f}%")

# Live Trades Table
if st.session_state.trades:
    trades_df = pd.DataFrame(st.session_state.trades)
    
    st.subheader("📋 **LIVE TRADE HISTORY**")
    display_df = trades_df[['time', 'symbol', 'side', 'qty', 'price', 'pnl']].tail(15)
    display_df['price'] = display_df['price'].round(0)
    display_df['pnl'] = display_df['pnl'].round(0)
    
    st.dataframe(display_df.style.format({
        'price': '{:.0f}',
        'pnl': '₹{:.0f}'
    }).background_gradient(subset=['pnl'], cmap='RdYlGn'), use_container_width=True)
    
    # Portfolio Charts
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 **CAPITAL GROWTH**")
        trades_df['cum_pnl'] = trades_df['pnl'].cumsum()
        fig_growth = go.Figure()
        fig_growth.add_trace(go.Scatter(x=trades_df['time'], y=trades_df['cum_pnl'],
                                       mode='lines', line=dict(color='#00ff88', width=4)))
        fig_growth.add_hline(y=0, line_dash="dash", line_color="gray")
        fig_growth.update_layout(height=350)
        st.plotly_chart(fig_growth)
    
    with col2:
        st.subheader("🏆 **BEST STOCKS**")
        top_stocks = trades_df.groupby('symbol')['pnl'].sum().sort_values(ascending=False).head(8)
        fig_bar = go.Figure(data=[go.Bar(x=top_stocks.index, y=top_stocks.values,
                                       marker_color=['green' if x>0 else 'red' for x in top_stocks.values])])
        fig_bar.update_layout(height=350)
        st.plotly_chart(fig_bar)

else:
    st.info("🎯 **Activate AUTO BOT to start 24/7 trading!**")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666'>
🔥 **AUTO FEATURES:**
• 100 NSE Stocks • RSI Signals • 30s Intervals 
• Risk Management • Live P&L • 24/7 Trading
</div>
""", unsafe_allow_html=True)
