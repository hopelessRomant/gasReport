import sys
import logging
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QSizePolicy, QFrame, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QCursor, QBrush, QColor, QDoubleValidator

# Import your API / logic function (assumes main.py provides this)
from main import get_gas_costs_json

logging.basicConfig(level=logging.INFO)


class FetchThread(QThread):
    """Run get_gas_costs_json in a background thread to avoid blocking the UI."""
    finished = pyqtSignal(object)   # emits the results dict (or None)
    errored = pyqtSignal(str)       # emits error message

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

        # ---- Window Settings ----
        self.setWindowTitle("Gas Price Calculator")
        self.setStyleSheet("background-color: #121212; color: white; font-family: Roboto;")
        self.resize(700, 400)

        # ---- Internal Variables ----
        self.gas_used = None
        self.currency = None
        self.counter = 30  # refresh interval in seconds
        self.fetch_thread = None  # placeholder for the background thread
        self.failure_count = 0    # track consecutive failures (optional use)
        self.min_refresh_interval = 30

        # ---- Layout ----
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        # Countdown label (hidden until first calculate)
        self.countdown_label = QLabel("", self)
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setStyleSheet("font-size: 16px; padding: 8px;")
        self.countdown_label.setVisible(False)
        main_layout.addWidget(self.countdown_label)

        # Input area
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(6, 6, 6, 6)
        input_layout.setSpacing(8)

        self.gas_input = QLineEdit(self)
        self.gas_input.setPlaceholderText("Enter Gas Used (e.g. 21000)")
        self.gas_input.setStyleSheet(self._input_style())
        self.gas_input.setValidator(QDoubleValidator(0.0, 1e12, 6))
        self.gas_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.currency_input = QLineEdit(self)
        self.currency_input.setPlaceholderText("Enter ISO code (e.g. USD)")
        self.currency_input.setStyleSheet(self._input_style())
        self.currency_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.calculate_button = QPushButton("Calculate", self)
        self.calculate_button.setStyleSheet(self._button_style())
        self.calculate_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.calculate_button.clicked.connect(self.calculate)
        self.calculate_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        input_layout.addWidget(self.gas_input, 2)
        input_layout.addWidget(self.currency_input, 1)
        input_layout.addWidget(self.calculate_button, 0)

        main_layout.addLayout(input_layout)

        # Table widget
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
        self.table.verticalHeader().setVisible(False)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        for i in range(3):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(self.table, 1)

        # Timer setup
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        # Color map for speeds (keys are lowercase)
        self.color_map = {
            "safe": "#00FF00",
            "average": "#33CFFF",
            "fast": "#FF6347"
        }

    # ---------- Styles ----------
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

    # ---------- Button Logic ----------
    def calculate(self):
        """Validate inputs, start countdown, and trigger the first fetch (in background)."""
        # Sanitize and parse gas input (strip thousands separators like commas/spaces)
        raw = self.gas_input.text().strip()
        if not raw:
            logging.error("Gas input empty")
            return

        # Remove common thousands separators so float() won't choke on "21,000" or "21 000"
        sanitized = raw.replace(",", "").replace(" ", "")
        try:
            self.gas_used = float(sanitized)
            if self.gas_used <= 0:
                raise ValueError("Gas must be > 0")
        except Exception:
            logging.error("Invalid gas input: %r", raw)
            return

        self.currency = (self.currency_input.text().strip() or "USD").lower()

        # Reset and start timer (countdown)
        self.timer.stop()
        self.counter = self.min_refresh_interval
        self.countdown_label.setVisible(True)
        self.countdown_label.setText(f"Next refresh in {self.counter}s")
        self.timer.start(1000)

        # Start background fetch (non-blocking)
        self.start_fetch()

    def start_fetch(self):
        """Start a background thread to fetch the gas cost JSON safely."""
        # Prevent repeated parallel fetches
        if getattr(self, "fetch_thread", None) and self.fetch_thread.isRunning():
            logging.info("Fetch already in progress; skipping new fetch request.")
            return

        # Disable inputs while fetching
        self.set_inputs_enabled(False)

        # Create and store thread reference
        self.fetch_thread = FetchThread(self.gas_used, self.currency)
        # Connect signals
        self.fetch_thread.finished.connect(self.on_fetch_finished)
        self.fetch_thread.errored.connect(self.on_fetch_error)
        # Ensure the QThread object is cleaned up when finished
        self.fetch_thread.finished.connect(self.fetch_thread.deleteLater)
        logging.info("Starting fetch thread (gas=%s currency=%s)", self.gas_used, self.currency)
        self.fetch_thread.start()

    def set_inputs_enabled(self, enabled: bool):
        """Enable/disable the input fields and button (UI nicety)."""
        self.gas_input.setEnabled(enabled)
        self.currency_input.setEnabled(enabled)
        self.calculate_button.setEnabled(enabled)

    # ---------- Fetch callbacks ----------
    def on_fetch_finished(self, results):
        """Called in the main thread when the FetchThread finishes successfully."""
        logging.info("Fetch finished")
        self.set_inputs_enabled(True)
        self.failure_count = 0  # reset consecutive-failure counter

        if not results:
            logging.error("Empty response from get_gas_costs_json")
            self.clear_table()
            return

        if isinstance(results, dict) and "error" in results:
            logging.error("API returned error: %s", results.get("error"))
            self.clear_table()
            return

        # Validate expected structure
        if not isinstance(results, dict) or "gas_costs" not in results or "current_gas_prices_gwei" not in results:
            logging.error("Unexpected API response format: missing expected keys")
            self.clear_table()
            return

        # Good to go: populate table
        self.populate_table(results)

    def on_fetch_error(self, message: str):
        """Called in the main thread when the FetchThread raised an exception."""
        logging.error(f"Error fetching gas costs: {message}")
        self.set_inputs_enabled(True)
        self.failure_count += 1
        # Clear table so stale data isn't shown
        self.clear_table()

        # Optional simple backoff logic: after 3 consecutive failures, extend next refresh
        if self.failure_count >= 3:
            logging.warning("Multiple consecutive failures (%d). Extending next refresh interval.", self.failure_count)
            self.counter = max(self.counter, 60)

    # ---------- Populate / Clear Table ----------
    def clear_table(self):
        """Clear table rows so stale data is not displayed."""
        self.table.setRowCount(0)
        # Optionally reset headers to generic labels
        self.table.setHorizontalHeaderLabels(["Speed", "Cost (ETH)", "Cost (Currency)"])

    def populate_table(self, results):
        data = results.get("gas_costs", [])
        prices = results.get("current_gas_prices_gwei", {})

        self.table.setRowCount(len(data))

        # Update header label once according to currency
        if self.currency == "usd":
            self.table.setHorizontalHeaderLabels(["Speed", "Cost (ETH)", "Cost (USD)"])
        else:
            self.table.setHorizontalHeaderLabels(
                ["Speed", "Cost (ETH)", f"Cost ({self.currency.upper()})"]
            )

        for row, entry in enumerate(data):
            # defensive defaults
            if not isinstance(entry, dict):
                entry = {}

            speed_raw = str(entry.get("speed", "unknown"))
            speed_key = speed_raw.lower()
            # try several ways to get a gwei price
            gwei_price = prices.get(speed_raw, prices.get(speed_key, "?"))
            speed_display_label = f"{speed_raw.capitalize()} ({gwei_price} Gwei)"

            # ETH cost
            try:
                eth_cost_val = float(entry.get("eth_cost", 0))
            except Exception:
                eth_cost_val = 0.0
            eth_text = f"{eth_cost_val:.6f} ETH"
            eth_item = QTableWidgetItem(eth_text)
            eth_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Currency cost
            if self.currency == "usd":
                try:
                    usd_val = float(entry.get("usd_cost", 0))
                except Exception:
                    usd_val = 0.0
                currency_text = f"${usd_val:.2f}"
            else:
                try:
                    other_val = float(entry.get("currency_cost", 0))
                except Exception:
                    other_val = 0.0
                currency_text = f"{self.currency.upper()} {other_val:.2f}"

            currency_item = QTableWidgetItem(currency_text)
            currency_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Speed item
            speed_item = QTableWidgetItem(speed_display_label)
            speed_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Apply color using lowercase key lookup
            color_hex = self.color_map.get(speed_key, "#FFFFFF")
            brush = QBrush(QColor(color_hex))
            speed_item.setForeground(brush)
            eth_item.setForeground(brush)
            currency_item.setForeground(brush)

            # Insert into table
            self.table.setItem(row, 0, speed_item)
            self.table.setItem(row, 1, eth_item)
            self.table.setItem(row, 2, currency_item)

        # Force UI refresh
        self.table.viewport().update()
        self.table.horizontalHeader().update()

    # ---------- Countdown ----------
    def update_timer(self):
        self.counter -= 1
        if self.counter <= 0:
            # reset to min refresh interval and trigger a background fetch
            self.counter = self.min_refresh_interval
            self.start_fetch()
        self.countdown_label.setText(f"Next refresh in {self.counter}s")

    # ---------- Cleanup ----------
    def closeEvent(self, event):
        """
        Ensure thread is cleaned up before closing the app to avoid
        delivering signals to deleted objects (which can segfault).
        """
        try:
            if getattr(self, "fetch_thread", None):
                # If a fetch is running, disconnect signals and stop the thread
                if self.fetch_thread.isRunning():
                    try:
                        self.fetch_thread.finished.disconnect(self.on_fetch_finished)
                    except Exception:
                        pass
                    try:
                        self.fetch_thread.errored.disconnect(self.on_fetch_error)
                    except Exception:
                        pass

                    # Request thread to quit and wait for it to finish
                    self.fetch_thread.quit()
                    self.fetch_thread.wait(2000)  # wait up to 2s for cleanup
                    # Ensure deletion scheduling
                    try:
                        self.fetch_thread.deleteLater()
                    except Exception:
                        pass
        except Exception as e:
            logging.exception("Error while cleaning up thread on close: %s", e)
        finally:
            super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GasPriceApp()
    window.show()
    sys.exit(app.exec())
