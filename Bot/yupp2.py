import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

import MetaTrader5 as mt5
import pandas as pd
from ta.trend import SMAIndicator


# -----------------------------
# TRADING BOT LOGIC (as a thread)
# -----------------------------
class TradingBot(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, symbol, timeframe, fast_window, slow_window,
                 risk_per_trade, stop_loss_pips, take_profit_pips,
                 min_lot, max_lot, max_trades):
        super().__init__()
        self.symbol = symbol
        self.timeframe = timeframe
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.risk_per_trade = risk_per_trade
        self.stop_loss_pips = stop_loss_pips
        self.take_profit_pips = take_profit_pips
        self.min_lot = min_lot
        self.max_lot = max_lot
        self.max_trades = max_trades
        self.running = False
        self.last_signal = 0
        self.trade_count = 0
        self.filling_mode = None  # Will detect proper filling mode

    def run(self):
        self.running = True
        self.log("🚀 Bot started!")

        if not mt5.initialize():
            self.log("❌ Failed to initialize MT5")
            self.running = False
            return

        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            self.log(f"❌ {self.symbol} not found in Market Watch")
            mt5.shutdown()
            self.running = False
            return
        
        # Detect proper filling mode for this broker
        self.filling_mode = self.detect_filling_mode()
        if self.filling_mode is None:
            self.log("❌ Failed to determine filling mode")
            mt5.shutdown()
            self.running = False
            return

        while self.running:
            try:
                rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 100)
                if rates is None:
                    self.log("⚠️ No data received.")
                    time.sleep(30)
                    continue

                df = pd.DataFrame(rates)
                df['sma_slow'] = SMAIndicator(df['close'], window=self.slow_window).sma_indicator()
                df['sma_fast'] = SMAIndicator(df['close'], window=self.fast_window).sma_indicator()
                df['signal'] = 0
                df.loc[df['sma_fast'] > df['sma_slow'], 'signal'] = 1
                df.loc[df['sma_fast'] < df['sma_slow'], 'signal'] = -1

                if len(df) < max(self.fast_window, self.slow_window):
                    time.sleep(30)
                    continue

                latest = df.iloc[-1]
                current_signal = latest['signal']
                current_price = latest['close']

                if current_signal != self.last_signal and self.trade_count < self.max_trades:
                    pip_size = 0.01 if "JPY" in self.symbol else 0.0001
                    lot_size = self.calculate_position_size(current_price, pip_size)
                    lot_size = max(self.min_lot, min(lot_size, self.max_lot))

                    if current_signal == 1:
                        sl = current_price - (self.stop_loss_pips * pip_size)
                        tp = current_price + (self.take_profit_pips * pip_size)
                        self.log(f"🟢 BUY Signal | Price: {current_price:.5f} | Lots: {lot_size}")
                        self.place_order(mt5.ORDER_TYPE_BUY, lot_size, sl, tp)

                    elif current_signal == -1:
                        sl = current_price + (self.stop_loss_pips * pip_size)
                        tp = current_price - (self.take_profit_pips * pip_size)
                        self.log(f"🔴 SELL Signal | Price: {current_price:.5f} | Lots: {lot_size}")
                        self.place_order(mt5.ORDER_TYPE_SELL, lot_size, sl, tp)

                    self.last_signal = current_signal

                time.sleep(60 * 15)

            except Exception as e:
                self.log(f"⚠️ Error: {e}")
                time.sleep(30)

        mt5.shutdown()
        self.log("✅ Bot stopped. MT5 connection closed.")

    def stop(self):
        self.running = False

    def log(self, msg):
        self.log_signal.emit(msg)
        
    def detect_filling_mode(self):
        """Detect the proper filling mode for this broker"""
        modes = [
            mt5.ORDER_FILLING_FOK,    # Fill or Kill
            mt5.ORDER_FILLING_IOC,    # Immediate or Cancel
            mt5.ORDER_FILLING_RETURN, # Return remaining
            mt5.ORDER_FILLING_BOC     # Book or Cancel
        ]
        
        # Try all modes until we find one that works
        for mode in modes:
            if self.test_filling_mode(mode):
                self.log(f"✅ Using filling mode: {self.filling_mode_to_str(mode)}")
                return mode
                
        return None
        
    def test_filling_mode(self, mode):
        """Test if a filling mode is supported"""
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": 0.01,
            "type": mt5.ORDER_TYPE_BUY,
            "price": mt5.symbol_info_tick(self.symbol).ask,
            "deviation": 20,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mode,
        }
        
        result = mt5.order_check(request)
        return result.retcode == mt5.TRADE_RETCODE_DONE
        
    def filling_mode_to_str(self, mode):
        """Convert filling mode to string"""
        modes = {
            mt5.ORDER_FILLING_FOK: "FOK (Fill or Kill)",
            mt5.ORDER_FILLING_IOC: "IOC (Immediate or Cancel)",
            mt5.ORDER_FILLING_RETURN: "Return",
            mt5.ORDER_FILLING_BOC: "BOC (Book or Cancel)"
        }
        return modes.get(mode, "Unknown")

    def calculate_position_size(self, price, pip_size):
        account = mt5.account_info()
        if not account:
            return 0.01
        risk_amount = account.balance * self.risk_per_trade
        contract_size = mt5.symbol_info(self.symbol).trade_contract_size
        pip_value = (pip_size / price) * contract_size
        if pip_value == 0:
            return 0.01
        lots = risk_amount / (self.stop_loss_pips * pip_value)
        return round(lots, 2)

    def place_order(self, order_type, lot_size, sl, tp):
        # Ensure symbol is visible and ready
        if not mt5.symbol_select(self.symbol, True):
            self.log(f"❌ Failed to select symbol {self.symbol}")
            return

        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            self.log("❌ No tick data")
            return

        price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid

        # Prepare base request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": lot_size,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 2025,
            "comment": "Python Bot",
            "type_time": mt5.ORDER_TIME_GTC,
        }

        # Strategy: Try with RETURN first (most brokers accept it)
        # If that fails with "unsupported", try without it — but we'll do it in one go
        # Actually, the BEST practice: Check what the symbol allows

        sym = mt5.symbol_info(self.symbol)
        if sym is None:
            self.log("❌ Symbol info unavailable")
            return

        # Default to RETURN if allowed, otherwise omit
        if sym.filling_mode & mt5.SYMBOL_FILLING_RETURN:
            request["type_filling"] = mt5.ORDER_FILLING_RETURN
        elif sym.filling_mode & mt5.SYMBOL_FILLING_IOC:
            request["type_filling"] = mt5.ORDER_FILLING_IOC
        elif sym.filling_mode & mt5.SYMBOL_FILLING_FOK:
            request["type_filling"] = mt5.ORDER_FILLING_FOK
        else:
            # Last resort: DO NOT include type_filling
            pass  # omit it

        result = mt5.order_send(request)
        
        # If failed due to filling mode, retry WITHOUT type_filling
        if result.retcode == 10030:  # TRADE_RETCODE_INVALID_FILL
            self.log("⚠️ Filling mode rejected — retrying without type_filling...")
            request.pop("type_filling", None)
            result = mt5.order_send(request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.log(f"❌ Order failed: {result.comment} (retcode: {result.retcode})")
        else:
            self.log(f"✅ Order placed! Lots: {lot_size}, Ticket: {result.order}")


# -----------------------------
# MAIN DASHBOARD WINDOW
# -----------------------------
class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔷 MT5 Forex Bot Dashboard")
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f0c29, stop:0.5 #302b63, stop:1 #24243e
                );
            }
            QLabel, QLineEdit, QTextEdit, QPushButton {
                font-family: 'Segoe UI', sans-serif;
                color: #e0e0ff;
            }
            QLineEdit {
                background: rgba(30, 30, 50, 0.7);
                color: white;
                border: 1px solid #5a5a8a;
                padding: 8px;
                border-radius: 6px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6a11cb, stop:1 #2575fc);
                color: white;
                border: none;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #7a21db, stop:1 #3585ff);
            }
            QTextEdit {
                background: rgba(20, 20, 35, 0.8);
                color: #aaffaa;
                border: 1px solid #4a4a7a;
                border-radius: 6px;
            }
            QGroupBox {
                color: #bb86fc;
                font-weight: bold;
                border: 1px solid #5a5a8a;
                border-radius: 8px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        self.setGeometry(100, 100, 850, 680)
        self.bot_thread = None

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        title = QLabel("🤖 MT5 Forex Trading Bot")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setStyleSheet("color: #64ffda; margin: 15px;")
        layout.addWidget(title)

        # Controls
        control_group = QGroupBox("⚙️ Bot Configuration")
        control_layout = QFormLayout()
        control_layout.setSpacing(12)
        control_layout.setContentsMargins(20, 20, 20, 20)

        self.symbol_input = QLineEdit("EURUSD")
        self.min_lot_input = QLineEdit("0.01")
        self.max_lot_input = QLineEdit("1.0")
        self.max_trades_input = QLineEdit("5")
        self.sl_input = QLineEdit("20")
        self.tp_input = QLineEdit("40")

        control_layout.addRow("Symbol:", self.symbol_input)
        control_layout.addRow("Min Lot Size:", self.min_lot_input)
        control_layout.addRow("Max Lot Size:", self.max_lot_input)
        control_layout.addRow("Max Trades to Place:", self.max_trades_input)
        control_layout.addRow("Stop Loss (pips):", self.sl_input)
        control_layout.addRow("Take Profit (pips):", self.tp_input)

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # Buttons
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("▶️ Start Bot")
        self.stop_btn = QPushButton("⏹️ Stop Bot")
        self.stop_btn.setEnabled(False)

        self.start_btn.clicked.connect(self.start_bot)
        self.stop_btn.clicked.connect(self.stop_bot)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        layout.addLayout(btn_layout)

        # Log
        layout.addWidget(QLabel("📜 Live Log:"))
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

    def log(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {msg}")
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())

    def start_bot(self):
        if self.bot_thread and self.bot_thread.isRunning():
            self.log("⚠️ Bot is already running!")
            return

        try:
            symbol = self.symbol_input.text().strip().upper()
            min_lot = float(self.min_lot_input.text())
            max_lot = float(self.max_lot_input.text())
            max_trades = int(self.max_trades_input.text())
            sl_pips = int(self.sl_input.text())
            tp_pips = int(self.tp_input.text())
        except ValueError:
            self.log("❌ Invalid input! Please enter valid numbers.")
            return

        if min_lot <= 0 or max_lot <= 0 or max_trades <= 0:
            self.log("❌ Lot sizes and max trades must be positive!")
            return

        self.bot_thread = TradingBot(
            symbol=symbol,
            timeframe=mt5.TIMEFRAME_M15,
            fast_window=20,
            slow_window=50,
            risk_per_trade=0.01,
            stop_loss_pips=sl_pips,
            take_profit_pips=tp_pips,
            min_lot=min_lot,
            max_lot=max_lot,
            max_trades=max_trades
        )
        self.bot_thread.log_signal.connect(self.log)
        self.bot_thread.start()

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.log("▶️ Bot starting...")

    def stop_bot(self):
        if self.bot_thread and self.bot_thread.isRunning():
            self.bot_thread.stop()
            self.bot_thread.wait()
            self.log("⏹️ Bot shutdown initiated.")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec_())