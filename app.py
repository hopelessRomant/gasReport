import sys
import logging
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor, QBrush, QColor
from main import get_gas_costs_json

logging.basicConfig(level=logging.INFO)

class GasPriceApp(QWidget):
    def __init__(self):
        super().__init__()

        # ---- Window Settings ----
        self.setWindowTitle("Gas Price Calculator")
        self.setStyleSheet("background-color: #121212; color: white; font-family: Roboto;")
        self.resize(800, 500)

        # ---- Variables ----
        self.gas_used = None
        self.currency = None
        self.counter = 30  # refresh interval (seconds)

        # ---- Layout ----
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

        # Countdown label (hidden initially)
        self.countdown_label = QLabel("")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setStyleSheet("font-size: 16px; margin-top: 5px;")
        self.countdown_label.setVisible(False)
        main_layout.addWidget(self.countdown_label)

        # ---- Input Fields ----
        input_layout = QHBoxLayout()

        self.gas_input = QLineEdit()
        self.gas_input.setPlaceholderText("Enter Gas Used (e.g. 21000)")
        self.gas_input.setStyleSheet(self._input_style())

        self.currency_input = QLineEdit()
        self.currency_input.setPlaceholderText("Enter ISO code: example - USD for $")
        self.currency_input.setStyleSheet(self._input_style())

        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.setStyleSheet(self._button_style())
        self.calculate_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.calculate_button.clicked.connect(self.calculate)

        input_layout.addWidget(self.gas_input)
        input_layout.addWidget(self.currency_input)
        input_layout.addWidget(self.calculate_button)

        main_layout.addLayout(input_layout)

        # ---- Table ----
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Speed", "Cost (ETH)", "Cost (Currency)"])
        self.table.setStyleSheet("""
            QTableWidget { background-color: #1E1E1E; gridline-color: gray; }
            QHeaderView::section { background-color: #333; color: white; }
        """)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        for i in range(3):
            header.setSectionResizeMode(i, header.ResizeMode.Stretch)

        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

        # ---- Timer (starts only after pressing Calculate) ----
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

    # ---------- Styles ----------
    def _input_style(self):
        return (
            "QLineEdit { padding: 6px; font-size: 14px; "
            "background-color: #1E1E1E; color: white; border: 1px solid gray; }"
        )

    def _button_style(self):
        return (
            "QPushButton { background-color: #03DAC6; color: black; font-weight: bold; "
            "padding: 6px 12px; border-radius: 5px; } "
            "QPushButton:hover { background-color: #018786; color: white; }"
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

        # Start countdown
        self.counter = 30
        self.countdown_label.setVisible(True)
        self.countdown_label.setText("Next refresh in 30s")

        self.refresh_table()
        self.timer.start(1000)

    # ---------- Table Update ----------
    def refresh_table(self):
        if not self.gas_used or not self.currency:
            return

        results = get_gas_costs_json(self.gas_used, self.currency)
        if "error" in results:
            logging.error(results["error"])
            return

        data = results["gas_costs"]
        self.table.setRowCount(len(data))

        # Color map for rows
        color_map = {
            "safe": "#00FF00",      # Green
            "average": "#00BFFF",   # Blue
            "fast": "#FF4500"       # Red
        }

        for row, entry in enumerate(data):
            speed_text = f"{entry['speed'].capitalize()} ({results['current_gas_prices_gwei'][entry['speed']]} Gwei)"
            self.table.setItem(row, 0, QTableWidgetItem(speed_text))
            self.table.setItem(row, 1, QTableWidgetItem(f"{entry['eth_cost']:.6f} ETH"))

            if self.currency == "usd":
                self.table.setHorizontalHeaderLabels(["Speed", "Cost (ETH)", "Cost (USD)"])
                self.table.setItem(row, 2, QTableWidgetItem(f"${entry['usd_cost']:.2f}"))
            else:
                self.table.setHorizontalHeaderLabels(["Speed", "Cost (ETH)", f"Cost ({self.currency.upper()})"])
                self.table.setItem(row, 2, QTableWidgetItem(f"{self.currency.upper()} {entry['currency_cost']:.2f}"))

            # Apply row color
            row_color = QColor(color_map.get(entry["speed"], "white"))
            for col in range(3):
                self.table.item(row, col).setForeground(QBrush(row_color))

    # ---------- Countdown Update ----------
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
