import tkinter as tk
from tkinter import scrolledtext
import MetaTrader5 as mt5
import threading
import time
import logging
import pandas as pd
import numpy as np
import os

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
RSI_BUY_THRESHOLD = 30
RSI_SELL_THRESHOLD = 70

# -------------------------------
# Helpers
# -------------------------------
def log(msg):
    log_panel.insert(tk.END, msg + "\n")
    log_panel.see(tk.END)

def connect_mt5():
    # --- IMPORTANT: Update this path to your MT5 terminal location ---
    # To find the path, right-click your MT5 shortcut, select "Properties",
    # and copy the "Target" path.
    # Example: "C:\\Program Files\\MetaTrader 5\\terminal64.exe"
    mt5_path = "C:\\Program Files\\MetaTrader 5\\terminal64.exe"
    
    if not os.path.exists(mt5_path):
        log(f"[ERROR] MT5 executable not found at: {mt5_path}")
        log("[ERROR] Please update the 'mt5_path' variable in the code to your correct MT5 installation path.")
        return False
        
    if not mt5.initialize(path=mt5_path):
        log(f"[ERROR] MT5 initialization failed, error code={mt5.last_error()}")
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
def get_data(symbol, n=200):
    try:
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, n)
        if rates is None:
            log(f"[DEBUG] No rates data received for {symbol}. mt5.copy_rates_from_pos returned None.")
            return pd.DataFrame()
        
        df = pd.DataFrame(rates)
        if df.empty:
            log(f"[DEBUG] Received 0 data points for {symbol}.")
        else:
            log(f"[DEBUG] Successfully received {len(df)} data points for {symbol}.")
            
        return df
    except Exception as e:
        log(f"[ERROR] Failed to get data for {symbol}: {e}")
        return pd.DataFrame()

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    
    rs = avg_gain / avg_loss
    
    # Handle division by zero
    rs = np.where(avg_loss == 0, np.inf, rs)
    
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calc_atr(df, period=14):
    if df.empty or len(df) < period:
        return 0
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
    
    if stop_loss_pips == 0:
        return 0.1
        
    tick_value = info.trade_tick_value
    tick_size = info.trade_tick_size
    contract_size = info.trade_contract_size
    
    if tick_size == 0:
        log(f"[ERROR] Tick size is zero for {symbol}, cannot calculate lot size.")
        return 0.1
        
    value_per_pip = (tick_value / tick_size) * contract_size / 10
    risk_amount = balance * (risk_pct / 100)
    
    if value_per_pip == 0:
        return 0.1
        
    lot = risk_amount / (stop_loss_pips * value_per_pip)
    return round(max(info.volume_min, min(lot, info.volume_max)), 2)

# -------------------------------
# Trading Logic
# -------------------------------
def generate_signal(symbol):
    df = get_data(symbol)
    if df.empty or 'close' not in df.columns or len(df) < 14:
        log(f"[INFO] Skipping signal generation for {symbol} due to insufficient data.")
        return None, None

    df['rsi'] = calc_rsi(df['close'])
    
    # Check if the most recent RSI value is a valid number.
    # The first 'period' values will be NaN due to the rolling average calculation.
    rsi = df['rsi'].iloc[-1]
    if pd.isna(rsi):
        log(f"[INFO] RSI calculation failed for {symbol} on the most recent data point.")
        return None, None
        
    log(f"[INFO] Current RSI for {symbol}: {rsi:.2f}")

    if rsi < RSI_BUY_THRESHOLD:  # oversold -> BUY
        return "BUY", rsi
    elif rsi > RSI_SELL_THRESHOLD: # overbought -> SELL
        return "SELL", rsi
    return None, rsi

def place_trade(symbol, lot, direction, atr):
    try:
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
            log(f"[ERROR] Order failed: code={result.retcode}, comment={result.comment}")

    except Exception as e:
        log(f"[ERROR] An unexpected error occurred in place_trade: {e}")

def trade_worker(symbol, risk_pct, trade_limit):
    global bot_running
    count = 0
    while bot_running:
        try:
            signal, rsi_val = generate_signal(symbol)
            
            if signal:
                if (symbol, signal) in active_positions:
                    log(f"[INFO] Skipping trade for {symbol}: Position already exists.")
                else:
                    acc = mt5.account_info()
                    df = get_data(symbol, 100)
                    if df.empty or len(df) < 14:
                        log(f"[INFO] Skipping trade for {symbol} due to insufficient data for ATR.")
                        time.sleep(10)
                        continue
                    
                    atr = calc_atr(df)
                    if atr == 0 or atr is None:
                        log(f"[INFO] ATR is zero or not available for {symbol}, skipping trade.")
                        time.sleep(10)
                        continue
                        
                    point_info = mt5.symbol_info(symbol)
                    if not point_info:
                        log(f"[ERROR] Failed to get symbol info for {symbol}.")
                        time.sleep(10)
                        continue
                    
                    stop_loss_pips = atr / point_info.point
                    lot = calc_lot(symbol, acc.balance, risk_pct, stop_loss_pips)
                    
                    if lot > 0:
                        place_trade(symbol, lot, signal, atr)
                        count += 1
                        if count >= trade_limit:
                            log(f"[BOT] Trade limit of {trade_limit} reached for {symbol}. Stopping worker.")
                            break
                    else:
                        log(f"[WARNING] Calculated lot size is 0 for {symbol}. Skipping trade.")
            else:
                rsi_display = f"{rsi_val:.2f}" if rsi_val is not None else "N/A"
                log(f"[INFO] No signal for {symbol} (RSI: {rsi_display}). Waiting...")
        
            time.sleep(10)
        except Exception as e:
            log(f"[ERROR] An unexpected error occurred in trade_worker for {symbol}: {e}")
            time.sleep(10)
            
    log(f"[BOT] Stopped for {symbol}")
    if threading.active_count() <= 2: 
        log("[BOT] All workers stopped.")

# -------------------------------
# Dashboard Controls
# -------------------------------
def start_bot():
    global bot_running, threads
    if bot_running:
        log("[BOT] Bot is already running.")
        return
        
    if not connect_mt5():
        return
    
    bot_running = True
    threads = []

    selected_pairs = [p for p, v in pair_vars.items() if v.get()]
    if not selected_pairs:
        log("[ERROR] No pairs selected. Please select at least one pair.")
        stop_bot()
        return
        
    try:
        trade_limit = int(trade_limit_entry.get())
        risk_pct = float(risk_entry.get())
    except ValueError:
        log("[ERROR] Invalid input for Risk % or Trade Limit. Please enter numbers.")
        stop_bot()
        return

    log(f"[BOT] Started for {selected_pairs} (Risk {risk_pct}%, Limit {trade_limit})")
    log("[BOT] Monitoring market for signals. This may take some time.")

    for sym in selected_pairs:
        t = threading.Thread(target=trade_worker, args=(sym, risk_pct, trade_limit))
        t.daemon = True
        t.start()
        threads.append(t)

def stop_bot():
    global bot_running, active_positions
    if not bot_running:
        log("[BOT] Bot is not running.")
        return
    bot_running = False
    active_positions.clear()
    disconnect_mt5()
    log("[BOT] Stop command sent. Waiting for threads to finish...")

# -------------------------------
# UI
# -------------------------------
root = tk.Tk()
root.title("RainBot Dashboard")
root.geometry("800x600")
root.configure(bg="#2c3e50")

frame = tk.Frame(root, bg="#2c3e50")
frame.pack(pady=10)

tk.Label(frame, text="Select Pairs:", bg="#2c3e50", fg="white").grid(row=0, column=0, sticky="w", padx=5)
pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "XAUUSD"]
pair_vars = {p: tk.BooleanVar() for p in pairs}
for i, pair in enumerate(pairs):
    tk.Checkbutton(frame, text=pair, variable=pair_vars[pair], bg="#2c3e50", fg="white", selectcolor="#34495e").grid(row=1, column=i, padx=5, pady=5)

tk.Label(frame, text="Risk %:", bg="#2c3e50", fg="white").grid(row=2, column=0, padx=5, pady=5)
risk_entry = tk.Entry(frame, bg="#34495e", fg="white", insertbackground="white")
risk_entry.insert(0, "1.0")
risk_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame, text="Trade Limit:", bg="#2c3e50", fg="white").grid(row=2, column=2, padx=5, pady=5)
trade_limit_entry = tk.Entry(frame, bg="#34495e", fg="white", insertbackground="white")
trade_limit_entry.insert(0, "5")
trade_limit_entry.grid(row=2, column=3, padx=5, pady=5)

start_btn = tk.Button(frame, text="🚀 Start Bot", command=start_bot, bg="#27ae60", fg="white", activebackground="#2ecc71", activeforeground="white", relief="flat")
start_btn.grid(row=3, column=0, pady=10, padx=5, columnspan=2, sticky="ew")

stop_btn = tk.Button(frame, text="🛑 Stop Bot", command=stop_bot, bg="#e74c3c", fg="white", activebackground="#c0392b", activeforeground="white", relief="flat")
stop_btn.grid(row=3, column=2, pady=10, padx=5, columnspan=2, sticky="ew")

log_panel = scrolledtext.ScrolledText(root, width=100, height=25, bg="#34495e", fg="white", relief="flat", borderwidth=0, highlightthickness=0)
log_panel.pack(padx=10, pady=10, fill="both", expand=True)

root.mainloop()
