import MetaTrader5 as mt5
import pandas as pd
import time
from ta.trend import SMAIndicator

# === CONFIG ===
SYMBOL = "EURUSD"          # Symbol as shown in your MT5 Market Watch (e.g., "EURUSD", "XAUUSD", "USDJPY")
TIMEFRAME = mt5.TIMEFRAME_M15
FAST_WINDOW = 20
SLOW_WINDOW = 50
RISK_PER_TRADE = 0.01      # 1% of balance
STOP_LOSS_PIPS = 20
TAKE_PROFIT_PIPS = 40

# Connect to MT5
if not mt5.initialize():
    print("❌ Failed to initialize MT5")
    mt5.shutdown()
    exit()

print("✅ Connected to MetaTrader 5")
account_info = mt5.account_info()
if account_info:
    print(f"🏦 Account: {account_info.login}, Balance: \${account_info.balance}")

# Get symbol info for pip calculation
symbol_info = mt5.symbol_info(SYMBOL)
if symbol_info is None:
    print(f"❌ {SYMBOL} not found in Market Watch. Please enable it in MT5.")
    mt5.shutdown()
    exit()

# Normalize symbol name
SYMBOL = symbol_info.name

def get_candles(count=100):
    rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, count)
    if rates is None:
        print(f"❌ Failed to get rates for {SYMBOL}")
        return pd.DataFrame()
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def calculate_signals(df):
    df['sma_slow'] = SMAIndicator(df['close'], window=SLOW_WINDOW).sma_indicator()
    df['sma_fast'] = SMAIndicator(df['close'], window=FAST_WINDOW).sma_indicator()
    df['signal'] = 0
    df.loc[df['sma_fast'] > df['sma_slow'], 'signal'] = 1   # Buy
    df.loc[df['sma_fast'] < df['sma_slow'], 'signal'] = -1  # Sell
    return df

def get_pip_size():
    # For JPY pairs, usually 0.01, else 0.0001
    if "JPY" in SYMBOL:
        return 0.01
    else:
        return 0.0001

def calculate_position_size(balance, stop_loss_pips):
    pip_size = get_pip_size()
    risk_amount = balance * RISK_PER_TRADE
    tick_value = mt5.symbol_info_tick(SYMBOL).ask  # approximate price
    contract_size = symbol_info.trade_contract_size  # e.g., 100000 for forex
    # Calculate pip value in account currency
    pip_value = (pip_size / tick_value) * contract_size
    if pip_value == 0:
        return 0.01  # fallback for non-forex
    lots = risk_amount / (stop_loss_pips * pip_value)
    # Round to 0.01 lot precision
    return round(lots, 2)

def place_order(order_type, lot_size, sl_price, tp_price):
    price = mt5.symbol_info_tick(SYMBOL).ask if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(SYMBOL).bid
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": lot_size,
        "type": order_type,
        "price": price,
        "sl": sl_price,
        "tp": tp_price,
        "deviation": 20,
        "magic": 100,
        "comment": "Python Bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ Order failed: {result.comment}")
    else:
        print(f"✅ Order placed! Ticket: {result.order}")

def main():
    print("🚀 Starting MT5 Forex Bot...")
    print(f"   Symbol: {SYMBOL}, Timeframe: M15, Risk: {RISK_PER_TRADE*100}%")
    time.sleep(5)

    last_signal = 0

    while True:
        try:
            df = get_candles(100)
            if df.empty:
                print("⚠️ No data received. Retrying...")
                time.sleep(30)
                continue

            df = calculate_signals(df)
            if len(df) < max(FAST_WINDOW, SLOW_WINDOW):
                print("⚠️ Not enough data for indicators.")
                time.sleep(30)
                continue

            latest = df.iloc[-1]
            current_signal = latest['signal']

            if current_signal != last_signal:
                pip_size = get_pip_size()
                balance = mt5.account_info().balance
                current_price = latest['close']
                lot_size = calculate_position_size(balance, STOP_LOSS_PIPS)

                if current_signal == 1:  # Buy
                    sl = current_price - (STOP_LOSS_PIPS * pip_size)
                    tp = current_price + (TAKE_PROFIT_PIPS * pip_size)
                    print(f"🟢 BUY Signal | Price: {current_price:.5f} | Lots: {lot_size}")
                    place_order(mt5.ORDER_TYPE_BUY, lot_size, sl, tp)

                elif current_signal == -1:  # Sell
                    sl = current_price + (STOP_LOSS_PIPS * pip_size)
                    tp = current_price - (TAKE_PROFIT_PIPS * pip_size)
                    print(f"🔴 SELL Signal | Price: {current_price:.5f} | Lots: {lot_size}")
                    place_order(mt5.ORDER_TYPE_SELL, lot_size, sl, tp)

                last_signal = current_signal

            print("🕒 Next check in 15 minutes...")
            time.sleep(60 * 15)

        except KeyboardInterrupt:
            print("🛑 Bot stopped by user.")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(30)

    mt5.shutdown()
    print("✅ MT5 connection closed.")

if __name__ == "__main__":
    main()