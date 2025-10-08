import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import time

def initialize_mt5():
    if not mt5.initialize():
        print("initialize() failed")
        mt5.shutdown()
        return False
    print("MT5 Initialized Successfully")
    return True

def fetch_forex_data(symbol, timeframe, num_bars):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_bars)
    if rates is None:
        print(f"Failed to fetch data for {symbol}. Error: {mt5.last_error()}")
        return None
    if len(rates) == 0:
        print(f"No data available for {symbol}.")
        return None
    print(f"Fetched {len(rates)} bars for {symbol}: {rates}")  # Print raw data
    return pd.DataFrame(rates)

def moving_average_strategy(data, short_window=3, long_window=15):
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data['close']
    signals['short_mavg'] = data['close'].rolling(window=short_window, min_periods=1).mean()
    signals['long_mavg'] = data['close'].rolling(window=long_window, min_periods=1).mean()
    signals['signal'] = 0.0

    # Create signals based on moving average crossovers
    signals['signal'] = np.where(
        signals['short_mavg'] > signals['long_mavg'], 1.0, 0.0
    )  # Buy signal
    signals['signal'] = np.where(
        signals['short_mavg'] < signals['long_mavg'], -1.0, signals['signal']
    )  # Sell signal

    signals['positions'] = signals['signal'].diff()

    # Debugging output
    print("Short Moving Average:", signals['short_mavg'].tail())
    print("Long Moving Average:", signals['long_mavg'].tail())
    print("Signals:", signals['signal'].tail())
    
    return signals

def execute_trade(symbol, action, lot_size=0.1):
    # Define order types
    ORDER_BUY = 0
    ORDER_SELL = 1

    if action == 1:  # Buy
        order_type = ORDER_BUY
        price = mt5.symbol_info_tick(symbol).ask
        sl = price - 0.0020  # Set SL further away (20 pips below the ask price)
        tp = price + 0.0020  # Set TP (20 pips above the ask price)
    elif action == -1:  # Sell
        order_type = ORDER_SELL
        price = mt5.symbol_info_tick(symbol).bid
        sl = price + 0.0020  # Set SL (20 pips above the bid price)
        tp = price - 0.0020  # Set TP (20 pips below the bid price)
    else:
        return

    # Print current prices and SL/TP values for debugging
    print(f"Current Ask Price: {mt5.symbol_info_tick(symbol).ask}")
    print(f"Current Bid Price: {mt5.symbol_info_tick(symbol).bid}")
    print(f"Calculated SL: {sl}, TP: {tp}")

    # Ensure SL and TP are valid
    if sl <= 0 or tp <= 0:
        print("Invalid SL or TP values. SL and TP must be greater than 0.")
        return

    request = {
        "action": mt5.TRADE_ACTION_DEAL,  # Use market order for testing
        "symbol": symbol,
        "volume": lot_size,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 234000,
        "comment": "Python MT5 trading bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    print(f"Sending order: {request}")  # Print the request details for debugging
    result = mt5.order_send(request)

    if result is None:
        print(f"Order send failed: {mt5.last_error()}")
    else:
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Failed to execute trade: {result.retcode}, {mt5.last_error()}")
        else:
            print(f"Trade executed: {'Buy' if action == 1 else 'Sell'} {symbol} at {price}")





if __name__ == "__main__":
    if not initialize_mt5():
        exit()

    symbol = "EURUSD"  # Change to your desired currency pair
    timeframe = mt5.TIMEFRAME_M1  # 1-minute timeframe
    num_bars = 100  # Number of bars to fetch

    last_position = 0  # Track the last position to avoid repeated trades

    while True:
        data = fetch_forex_data(symbol, timeframe, num_bars)  # Corrected line
        if data is not None:
            signals = moving_average_strategy(data)
            current_signal = signals['signal'].iloc[-1]  # Get the latest signal

            if current_signal != last_position:  # Check if the signal has changed
                execute_trade(symbol, current_signal)
                last_position = current_signal  # Update last position

        time.sleep(60)  # Wait for 1 minute before fetching new data
