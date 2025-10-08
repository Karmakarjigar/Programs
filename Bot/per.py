import MetaTrader5 as mt5

mt5.initialize()
symbol = "EURUSD"

# Try the different filling modes one by one
filling_modes = [
    mt5.ORDER_FILLING_IOC,
    mt5.ORDER_FILLING_FOK,
    mt5.ORDER_FILLING_RETURN
]

for mode in filling_modes:
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": 0.1,
        "type": mt5.ORDER_TYPE_BUY,
        "price": mt5.symbol_info_tick(symbol).ask,
        "deviation": 10,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mode,
    }
    result = mt5.order_send(request)
    print(f"Mode: {mode}, Result: {result.comment}")
    if result.retcode == 10009:   # 10009 means TRADE_RETCODE_DONE (order successful)
        print("Success!")
        break

mt5.shutdown()
