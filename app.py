import sys
import logging
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor, QBrush, QColor, QDoubleValidator
from main import get_gas_costs_json

logging.basicConfig(level=logging.INFO)


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

        # ---- Layout ----
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

        # Countdown label (hidden until first calculate)
        self.countdown_label = QLabel("", self)
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setStyleSheet("font-size: 16px; margin-top: 5px;")
        self.countdown_label.setVisible(False)
        main_layout.addWidget(self.countdown_label)

        # Input area
        input_layout = QHBoxLayout()

        self.gas_input = QLineEdit(self)
        self.gas_input.setPlaceholderText("Enter Gas Used (e.g. 21000)")
        self.gas_input.setStyleSheet(self._input_style())
        self.gas_input.setValidator(QDoubleValidator(0.0, 1e9, 2))  # prevent invalid input

        self.currency_input = QLineEdit(self)
        self.currency_input.setPlaceholderText("Enter ISO code: example - USD for $")
        self.currency_input.setStyleSheet(self._input_style())

        self.calculate_button = QPushButton("Calculate", self)
        self.calculate_button.setStyleSheet(self._button_style())
        self.calculate_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.calculate_button.clicked.connect(self.calculate)

        input_layout.addWidget(self.gas_input)
        input_layout.addWidget(self.currency_input)
        input_layout.addWidget(self.calculate_button)
        main_layout.addLayout(input_layout)

        # Table widget
        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Speed", "Cost (ETH)", "Cost (Currency)"])
        self.table.setStyleSheet("""
            QTableWidget { background-color: #1E1E1E; gridline-color: gray; }
            QHeaderView::section { background-color: #333; color: white; }
        """)
        self.table.verticalHeader().setVisible(False)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        for i in range(3):
            header.setSectionResizeMode(i, header.ResizeMode.Stretch)

        main_layout.addWidget(self.table)

        # Add a spacer to ensure table reaches bottom
        main_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Timer setup (will start after calculate)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

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
        try:
            self.gas_used = float(self.gas_input.text())
            if self.gas_used <= 0:
                raise ValueError
        except ValueError:
            logging.error("Invalid gas input")
            return

        self.currency = self.currency_input.text().strip().lower() or "usd"

        # Reset and start timer
        self.timer.stop()
        self.counter = 30
        self.countdown_label.setVisible(True)
        self.countdown_label.setText("Next refresh in 30s")
        self.timer.start(1000)

        self.refresh_table()

    # ---------- Populate Table ----------
    def refresh_table(self):
        if not self.gas_used or not self.currency:
            return

        results = get_gas_costs_json(self.gas_used, self.currency)

        # Validate API response
        if not results or "gas_costs" not in results or "current_gas_prices_gwei" not in results:
            logging.error("Unexpected API response format")
            return
        if "error" in results:
            logging.error(results["error"])
            return

        data = results["gas_costs"]
        self.table.setRowCount(len(data))

        # Set headers once
        if self.currency == "usd":
            self.table.setHorizontalHeaderLabels(["Speed", "Cost (ETH)", "Cost (USD)"])
        else:
            self.table.setHorizontalHeaderLabels(
                ["Speed", "Cost (ETH)", f"Cost ({self.currency.upper()})"]
            )

        color_map = {
            "safe": "#00FF00",      # Green
            "average": "#33CFFF",   # Slightly lighter blue for readability
            "fast": "#FF6347"       # Softer red
        }

        for row, entry in enumerate(data):
            speed = entry.get("speed", "unknown")
            gwei_price = results["current_gas_prices_gwei"].get(speed, "?")
            speed_text = f"{speed.capitalize()} ({gwei_price} Gwei)"

            # Create table items
            eth_item = QTableWidgetItem(f"{entry.get('eth_cost', 0):.6f} ETH")
            eth_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            if self.currency == "usd":
                currency_item = QTableWidgetItem(f"${entry.get('usd_cost', 0):.2f}")
            else:
                currency_item = QTableWidgetItem(
                    f"{self.currency.upper()} {entry.get('currency_cost', 0):.2f}"
                )
            currency_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            speed_item = QTableWidgetItem(speed_text)
            speed_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Set colors
            brush = QBrush(QColor(color_map.get(speed, "#FFFFFF")))
            speed_item.setForeground(brush)
            eth_item.setForeground(brush)
            currency_item.setForeground(brush)

            # Add to table
            self.table.setItem(row, 0, speed_item)
            self.table.setItem(row, 1, eth_item)
            self.table.setItem(row, 2, currency_item)

    # ---------- Countdown ----------
    def update_timer(self):
        self.counter -= 1
        if self.counter <= 0:
            self.counter = 30
            self.refresh_table()
        self.countdown_label.setText(f"Next refresh in {self.counter}s")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GasPriceApp()
    window.show()
    sys.exit(app.exec())
