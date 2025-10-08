import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime
import logging

# ------------------ SETTINGS ------------------
SYMBOL = "EURUSD"          # Forex pair
TIMEFRAME = mt5.TIMEFRAME_M5  # 5-minute candles
LOT = 0.1
TP_PIPS = 20
SL_PIPS = 10
EMA_FAST = 10
EMA_SLOW = 50
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
CHECK_INTERVAL = 60  # seconds

# ------------------ LOGGING ------------------
logging.basicConfig(filename="forex_bot.log",
                    level=logging.INFO,
                    format='%(asctime)s - %(message)s')

# ------------------ MT5 INITIALIZE ------------------
if not mt5.initialize():
    print("MT5 initialization failed")
    mt5.shutdown()
    exit()

# ------------------ HELPER FUNCTIONS ------------------
def get_data(symbol, timeframe, n=100):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def calculate_indicators(df):
    df['EMA_fast'] = df['close'].ewm(span=EMA_FAST, adjust=False).mean()
    df['EMA_slow'] = df['close'].ewm(span=EMA_SLOW, adjust=False).mean()
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.rolling(RSI_PERIOD).mean()
    avg_loss = loss.rolling(RSI_PERIOD).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def send_order(symbol, order_type, lot, sl_pips, tp_pips):
    price = mt5.symbol_info_tick(symbol).ask if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid
    deviation = 10
    point = mt5.symbol_info(symbol).point

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": price - SL_PIPS*point if order_type==mt5.ORDER_TYPE_BUY else price + SL_PIPS*point,
        "tp": price + TP_PIPS*point if order_type==mt5.ORDER_TYPE_BUY else price - TP_PIPS*point,
        "deviation": deviation,
        "magic": 123456,
        "comment": "EMA+RSI Bot",
        "type_filling": mt5.ORDER_FILLING_IOC
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logging.info(f"Order failed: {result}")
    else:
        logging.info(f"Order executed: {result}")

# ------------------ STRATEGY LOGIC ------------------
def check_signals(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]

    # Buy condition
    if prev['EMA_fast'] < prev['EMA_slow'] and last['EMA_fast'] > last['EMA_slow'] and last['RSI'] < RSI_OVERBOUGHT:
        send_order(SYMBOL, mt5.ORDER_TYPE_BUY, LOT, SL_PIPS, TP_PIPS)
    
    # Sell condition
    elif prev['EMA_fast'] > prev['EMA_slow'] and last['EMA_fast'] < last['EMA_slow'] and last['RSI'] > RSI_OVERSOLD:
        send_order(SYMBOL, mt5.ORDER_TYPE_SELL, LOT, SL_PIPS, TP_PIPS)

# ------------------ MAIN LOOP ------------------
print("Forex bot started...")
logging.info("Bot started")

try:
    while True:
        data = get_data(SYMBOL, TIMEFRAME)
        data = calculate_indicators(data)
        check_signals(data)
        time.sleep(CHECK_INTERVAL)
except KeyboardInterrupt:
    print("Bot stopped by user")
    logging.info("Bot stopped")
finally:
    mt5.shutdown()
