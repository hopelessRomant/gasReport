import sys
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QSizePolicy, QFrame, QHeaderView, QApplication
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QCursor, QBrush, QColor, QDoubleValidator
from main import get_gas_costs_json

logging.basicConfig(level=logging.INFO)


class FetchThread(QThread):
    finished = pyqtSignal(object)
    errored = pyqtSignal(str)

    def __init__(self, gas_used, currency, parent=None):
        super().__init__(parent)
        self.gas_used = gas_used
        self.currency = currency

    def run(self):
        try:
            results = get_gas_costs_json(self.gas_used, self.currency)
            self.finished.emit(results)
        except Exception as e:
            self.errored.emit(str(e))


class GasPriceApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gas Report")
        self.setStyleSheet("background-color: #121212; color: white; font-family: Roboto;")
        self.resize(700, 400)

        # state
        self.gas_used = None
        self.currency = None
        self.counter = 30
        self.fetch_thread = None
        self.failure_count = 0
        self.min_refresh_interval = 30

        # UI setup
        self._setup_ui()

        # timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        # colors
        self.color_map = {
            "safe": "#00FF00",
            "average": "#33CFFF",
            "fast": "#FF6347"
        }

    # ---------------- UI setup ----------------
    def _setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        # countdown label
        self.countdown_label = QLabel("", self)
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setStyleSheet("font-size: 16px; padding: 8px;")
        self.countdown_label.setVisible(False)
        main_layout.addWidget(self.countdown_label)

        # input row
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(6, 6, 6, 6)
        input_layout.setSpacing(8)

        self.gas_input = QLineEdit(self)
        self.gas_input.setPlaceholderText("Enter Gas Used (e.g. 21000)")
        self.gas_input.setStyleSheet(self._input_style())
        self.gas_input.setValidator(QDoubleValidator(0.0, 1e12, 6))
        self.gas_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.currency_input = QLineEdit(self)
        self.currency_input.setPlaceholderText("Enter ISO code")
        self.currency_input.setStyleSheet(self._input_style())
        self.currency_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.calculate_button = QPushButton("Calculate", self)
        self.calculate_button.setStyleSheet(self._button_style())
        self.calculate_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.calculate_button.clicked.connect(self.calculate)

        input_layout.addWidget(self.gas_input, 2)
        input_layout.addWidget(self.currency_input, 1)
        input_layout.addWidget(self.calculate_button, 0)

        main_layout.addLayout(input_layout)

        # table
        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Speed", "Cost (ETH)", "Cost (Currency)"])
        self.table.setFrameShape(QFrame.Shape.NoFrame)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #121212;
                gridline-color: #333;
            }
            QHeaderView::section {
                background-color: #1E1E1E;
                color: white;
                padding: 4px;
                border: none;
            }
        """)
        vertical_header = self.table.verticalHeader()
        if vertical_header is not None:
            vertical_header.setVisible(False)
        header = self.table.horizontalHeader()
        if header is not None:
            header.setStretchLastSection(True)
            for i in range(3):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.table, 1)

    def _input_style(self):
        return (
            "QLineEdit { padding: 6px; font-size: 14px;"
            " background-color: #1E1E1E; color: white; border: 1px solid gray; }"
        )

    def _button_style(self):
        return (
            "QPushButton { background-color: #03DAC6; color: black; font-weight: bold;"
            " padding: 6px 12px; border-radius: 5px; }"
            " QPushButton:hover { background-color: #018786; color: white; }"
        )

    # ---------------- Input handling ----------------
    def calculate(self):
        raw = self.gas_input.text().strip()
        if not raw:
            logging.error("Gas input empty")
            return

        sanitized = raw.replace(",", "").replace(" ", "")
        try:
            self.gas_used = float(sanitized)
            if self.gas_used <= 0:
                raise ValueError
        except Exception:
            logging.error("Invalid gas input: %r", raw)
            return

        self.currency = (self.currency_input.text().strip() or "USD").lower()
        self.timer.stop()
        self.counter = self.min_refresh_interval
        self.countdown_label.setVisible(True)
        self.countdown_label.setText(f"Next refresh in {self.counter}s")
        self.timer.start(1000)
        self.start_fetch()

    # ---------------- Fetch handling ----------------
    def start_fetch(self):
        if self.fetch_thread and self.fetch_thread.isRunning():
            logging.info("Fetch already in progress; skipping new fetch request.")
            return

        self.set_inputs_enabled(False)
        thread = FetchThread(self.gas_used, self.currency)
        thread.finished.connect(self.on_fetch_finished)
        thread.errored.connect(self.on_fetch_error)
        thread.finished.connect(self._cleanup_fetch_thread)
        thread.errored.connect(self._cleanup_fetch_thread)
        self.fetch_thread = thread
        logging.info("Starting fetch thread (gas=%s currency=%s)", self.gas_used, self.currency)
        thread.start()

    def set_inputs_enabled(self, enabled: bool):
        self.gas_input.setEnabled(enabled)
        self.currency_input.setEnabled(enabled)
        self.calculate_button.setEnabled(enabled)

    def on_fetch_finished(self, results):
        logging.info("Fetch finished")
        self.set_inputs_enabled(True)
        self.failure_count = 0

        if not isinstance(results, dict):
            logging.error("Unexpected response type: %r", type(results))
            self.clear_table()
            return

        if "error" in results:
            logging.error("API returned error: %s", results.get("error"))
            self.clear_table()
            return

        if "gas_costs" not in results or "current_gas_prices_gwei" not in results:
            logging.error("API response missing required keys")
            self.clear_table()
            return

        self.populate_table(results)

    def on_fetch_error(self, message: str):
        logging.error("Error fetching gas costs: %s", message)
        self.set_inputs_enabled(True)
        self.failure_count += 1
        self.clear_table()
        if self.failure_count >= 3:
            logging.warning("Multiple consecutive failures (%d). Extending next refresh interval.", self.failure_count)
            self.counter = max(self.counter, 60)

    def _cleanup_fetch_thread(self, *args):
        if self.fetch_thread:
            try:
                self.fetch_thread.deleteLater()
            except Exception:
                pass
            self.fetch_thread = None

    # ---------------- Table handling ----------------
    def clear_table(self):
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(["Speed", "Cost (ETH)", "Cost (Currency)"])

    def populate_table(self, results):
        data = results.get("gas_costs", [])
        if not isinstance(data, list):
            logging.error("Invalid data format for gas_costs")
            self.clear_table()
            return

        prices = results.get("current_gas_prices_gwei", {})
        if not isinstance(prices, dict):
            prices = {}

        self.table.setRowCount(len(data))

        header_currency = "USD" if self.currency == "usd" else (self.currency or "CUR").upper()
        self.table.setHorizontalHeaderLabels(["Speed", "Cost (ETH)", f"Cost ({header_currency})"])

        for row, entry in enumerate(data):
            if not isinstance(entry, dict):
                entry = {}

            speed_raw = str(entry.get("speed", "unknown"))
            speed_key = speed_raw.lower()
            gwei_price = prices.get(speed_raw, prices.get(speed_key, "?"))
            speed_display_label = f"{speed_raw.capitalize()} ({gwei_price} Gwei)"

            eth_cost_val = self._safe_float(entry.get("eth_cost", 0))
            eth_item = QTableWidgetItem(f"{eth_cost_val:.6f} ETH")
            eth_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            if self.currency == "usd":
                val = self._safe_float(entry.get("usd_cost", 0))
                currency_text = f"${val:.2f}"
            else:
                val = self._safe_float(entry.get("currency_cost", 0))
                currency_text = f"{header_currency} {val:.2f}"

            currency_item = QTableWidgetItem(currency_text)
            currency_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            speed_item = QTableWidgetItem(speed_display_label)
            speed_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            color_hex = self.color_map.get(speed_key, "#FFFFFF")
            brush = QBrush(QColor(color_hex))
            for item in (speed_item, eth_item, currency_item):
                item.setForeground(brush)

            self.table.setItem(row, 0, speed_item)
            self.table.setItem(row, 1, eth_item)
            self.table.setItem(row, 2, currency_item)

        viewport = self.table.viewport()
        if viewport is not None:
            viewport.update()
        header = self.table.horizontalHeader()
        if header is not None:
            header.update()

    @staticmethod
    def _safe_float(val):
        try:
            return float(val)
        except Exception:
            return 0.0

    # ---------------- Timer + cleanup ----------------
    def update_timer(self):
        self.counter -= 1
        if self.counter <= 0:
            self.counter = self.min_refresh_interval
            self.start_fetch()
        self.countdown_label.setText(f"Next refresh in {self.counter}s")

    def closeEvent(self, event):
        if self.fetch_thread:
            try:
                self.fetch_thread.quit()
                self.fetch_thread.wait(2000)
            except Exception:
                pass
            try:
                self.fetch_thread.deleteLater()
            except Exception:
                pass
            self.fetch_thread = None
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GasPriceApp()
    window.show()
    sys.exit(app.exec())