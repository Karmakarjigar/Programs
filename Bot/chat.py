import tkinter as tk
from tkinter import scrolledtext
import MetaTrader5 as mt5
import threading
import time
import logging
import pandas as pd

# -------------------------------
# Logging
# -------------------------------
logging.basicConfig(level=logging.INFO, format="%(message)s")

# -------------------------------
# Bot Config
# -------------------------------
bot_running = False
threads = []
active_positions = set()  # avoid duplicate trades

# -------------------------------
# Helpers
# -------------------------------
def log(msg):
    log_panel.insert(tk.END, msg + "\n")
    log_panel.see(tk.END)

def connect_mt5():
    if not mt5.initialize():
        log("[ERROR] MT5 initialization failed")
        return False
    acc = mt5.account_info()
    if acc:
        log(f"[BOT] Connected to MT5 (Balance: {acc.balance})")
    return True

def disconnect_mt5():
    mt5.shutdown()
    log("[BOT] Disconnected from MT5")

# -------------------------------
# Indicators
# -------------------------------
def get_data(symbol, n=100):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, n)
    return pd.DataFrame(rates)

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calc_atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean().iloc[-1]

# -------------------------------
# Risk Management
# -------------------------------
def calc_lot(symbol, balance, risk_pct, stop_loss_pips):
    info = mt5.symbol_info(symbol)
    if not info:
        return 0.1
    tick_value = info.trade_tick_value
    tick_size = info.trade_tick_size
    contract_size = info.trade_contract_size
    value_per_pip = (tick_value / tick_size) * contract_size / 10
    risk_amount = balance * (risk_pct / 100)
    lot = risk_amount / (stop_loss_pips * value_per_pip)
    return round(max(info.volume_min, min(lot, info.volume_max)), 2)

# -------------------------------
# Trading Logic
# -------------------------------
def generate_signal(symbol):
    df = get_data(symbol, 200)
    if df.empty:
        return None

    df['rsi'] = calc_rsi(df['close'])
    rsi = df['rsi'].iloc[-1]

    if rsi < 30:   # oversold -> BUY
        return "BUY"
    elif rsi > 70: # overbought -> SELL
        return "SELL"
    return None

def place_trade(symbol, lot, direction, atr):
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        log(f"[ERROR] No tick data for {symbol}")
        return

    price = tick.ask if direction == "BUY" else tick.bid
    point = mt5.symbol_info(symbol).point

    sl = price - 1.5 * atr if direction == "BUY" else price + 1.5 * atr
    tp = price + 3 * atr if direction == "BUY" else price - 3 * atr

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY if direction == "BUY" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 123456,
        "comment": "RainBot trade",
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)

    if result.retcode == mt5.TRADE_RETCODE_DONE:
        log(f"[TRADE] {direction} {symbol} {lot} lots @ {price:.5f} (TP={tp:.5f}, SL={sl:.5f})")
        active_positions.add((symbol, direction))
    else:
        log(f"[ERROR] Order failed: code={result.retcode}, dir={direction}")

def trade_worker(symbol, risk_pct, trade_limit):
    global bot_running
    count = 0
    while bot_running and count < trade_limit:
        signal = generate_signal(symbol)
        if signal and (symbol, signal) not in active_positions:
            acc = mt5.account_info()
            df = get_data(symbol, 100)
            atr = calc_atr(df)
            stop_loss_pips = atr / mt5.symbol_info(symbol).point
            lot = calc_lot(symbol, acc.balance, risk_pct, stop_loss_pips)
            place_trade(symbol, lot, signal, atr)
            count += 1
        time.sleep(10)
    log(f"[BOT] Stopped for {symbol}")

# -------------------------------
# Dashboard Controls
# -------------------------------
def start_bot():
    global bot_running, threads
    if not connect_mt5():
        return
    bot_running = True
    threads = []

    selected_pairs = [p for p, v in pair_vars.items() if v.get()]
    trade_limit = int(trade_limit_entry.get())
    risk_pct = float(risk_entry.get())

    log(f"[BOT] Started for {selected_pairs} (Risk {risk_pct}%, Limit {trade_limit})")

    for sym in selected_pairs:
        t = threading.Thread(target=trade_worker, args=(sym, risk_pct, trade_limit))
        t.daemon = True
        t.start()
        threads.append(t)

def stop_bot():
    global bot_running, active_positions
    bot_running = False
    active_positions.clear()
    disconnect_mt5()

# -------------------------------
# UI
# -------------------------------
root = tk.Tk()
root.title("RainBot Dashboard")
root.geometry("800x600")
root.configure(bg="black")

frame = tk.Frame(root, bg="black")
frame.pack(pady=10)

tk.Label(frame, text="Select Pairs:", bg="black", fg="white").grid(row=0, column=0, sticky="w")
pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "XAUUSD"]
pair_vars = {p: tk.BooleanVar() for p in pairs}
for i, pair in enumerate(pairs):
    tk.Checkbutton(frame, text=pair, variable=pair_vars[pair], bg="black", fg="white").grid(row=1, column=i, padx=5)

tk.Label(frame, text="Risk %:", bg="black", fg="white").grid(row=2, column=0)
risk_entry = tk.Entry(frame)
risk_entry.insert(0, "1.0")
risk_entry.grid(row=2, column=1)

tk.Label(frame, text="Trade Limit:", bg="black", fg="white").grid(row=2, column=2)
trade_limit_entry = tk.Entry(frame)
trade_limit_entry.insert(0, "5")
trade_limit_entry.grid(row=2, column=3)

start_btn = tk.Button(frame, text="🚀 Start Bot", command=start_bot, bg="green", fg="white")
start_btn.grid(row=3, column=0, pady=10)

stop_btn = tk.Button(frame, text="🛑 Stop Bot", command=stop_bot, bg="red", fg="white")
stop_btn.grid(row=3, column=1, pady=10)

log_panel = scrolledtext.ScrolledText(root, width=100, height=25, bg="black", fg="white")
log_panel.pack(padx=10, pady=10)

root.mainloop()
