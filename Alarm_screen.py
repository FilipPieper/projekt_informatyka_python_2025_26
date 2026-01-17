from PyQt5.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor

from alarm_list import AlarmType


class AlarmScreen(QWidget):
    def __init__(self, alarmy):
        super().__init__()
        self.alarmy = alarmy

        self._setup_window()
        self._setup_table()
        self._setup_buttons()
        self._setup_layout()
        self._setup_timer()

        self.refresh()

    # --------------------------------------------------
    # SETUP
    # --------------------------------------------------

    def _setup_window(self):
        self.setWindowTitle("ALARMY")
        self.setFixedSize(700, 400)
        self.setStyleSheet("background-color: #1e1e1e;")

    def _setup_table(self):
        self.table = QTableWidget(0, 4, self)
        self.table.setHorizontalHeaderLabels(["Czas", "Źródło", "Opis", "Typ"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)

    def _setup_buttons(self):
        self.btn_clear = QPushButton("Wyczyść", self)
        self.btn_clear.clicked.connect(self.on_clear)

        self.btn_close = QPushButton("Zamknij", self)
        self.btn_close.clicked.connect(self.close)

    def _setup_layout(self):
        buttons = QHBoxLayout()
        buttons.addWidget(self.btn_clear)
        buttons.addStretch()
        buttons.addWidget(self.btn_close)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addLayout(buttons)
        self.setLayout(layout)

    def _setup_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(500)

    # --------------------------------------------------
    # LOGIKA
    # --------------------------------------------------

    def on_clear(self):
        self.alarmy.clear_all()
        self.refresh()

    def refresh(self):
        alarms = self.alarmy.active_alarms()
        self.table.setRowCount(len(alarms))

        for row, alarm in enumerate(alarms):
            self._set_row(row, alarm)

    def _set_row(self, row, alarm):
        self.table.setItem(row, 0, QTableWidgetItem(alarm.time.strftime("%H:%M:%S")))
        self.table.setItem(row, 1, QTableWidgetItem(alarm.source))
        self.table.setItem(row, 2, QTableWidgetItem(alarm.message))
        self.table.setItem(row, 3, QTableWidgetItem(alarm.alarm_type.value))

        color = (
            QColor(255, 200, 0)
            if alarm.alarm_type == AlarmType.WARNING
            else QColor(255, 80, 80)
        )

        for col in range(4):
            item = self.table.item(row, col)
            if item:
                item.setBackground(color)
