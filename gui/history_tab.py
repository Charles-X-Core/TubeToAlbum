import sys
import os
import json
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QLabel, QMessageBox, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "history.json")


class HistoryTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.history = self.load_history()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 32, 40, 32)
        layout.setSpacing(24)

        header_row = QHBoxLayout()
        title = QLabel("Historial de descargas")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        header_row.addWidget(title)
        header_row.addStretch()

        self.count_label = QLabel(f"{len(self.history)} descargas")
        self.count_label.setFont(QFont("Segoe UI", 13))
        header_row.addWidget(self.count_label)

        clear_btn = QPushButton("Limpiar todo")
        clear_btn.setProperty("class", "danger")
        clear_btn.setMinimumHeight(44)
        clear_btn.setMinimumWidth(140)
        clear_btn.setFont(QFont("Segoe UI", 13))
        clear_btn.clicked.connect(self.clear_history)
        header_row.addWidget(clear_btn)
        layout.addLayout(header_row)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Titulo", "Artista", "Formato", "Tamano", "Fecha", "Ruta"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.setFont(QFont("Segoe UI", 13))
        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(16)
        btn_row.addStretch()

        open_btn = QPushButton("Abrir carpeta")
        open_btn.setMinimumHeight(46)
        open_btn.setMinimumWidth(140)
        open_btn.setFont(QFont("Segoe UI", 13))
        open_btn.clicked.connect(self.open_folder)
        btn_row.addWidget(open_btn)

        redownload_btn = QPushButton("Re-descargar")
        redownload_btn.setMinimumHeight(46)
        redownload_btn.setMinimumWidth(140)
        redownload_btn.setFont(QFont("Segoe UI", 13))
        redownload_btn.clicked.connect(self.redownload)
        btn_row.addWidget(redownload_btn)

        delete_btn = QPushButton("Eliminar")
        delete_btn.setProperty("class", "danger")
        delete_btn.setMinimumHeight(46)
        delete_btn.setMinimumWidth(120)
        delete_btn.setFont(QFont("Segoe UI", 13))
        delete_btn.clicked.connect(self.delete_selected)
        btn_row.addWidget(delete_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.refresh_table()

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_history(self):
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error guardando historial: {e}")

    def add_entry(self, info, filepath, fmt):
        entry = {
            'title': info.get('title', 'Sin titulo'),
            'artist': info.get('artist', 'Desconocido'),
            'format': fmt.upper(),
            'filepath': filepath,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'size': os.path.getsize(filepath) if filepath and os.path.exists(filepath) else 0,
            'url': info.get('url', '')
        }
        self.history.insert(0, entry)
        if len(self.history) > 100:
            self.history = self.history[:100]
        self.save_history()
        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(len(self.history))
        self.count_label.setText(f"{len(self.history)} descargas")
        for i, entry in enumerate(self.history):
            title_item = QTableWidgetItem(entry.get('title', '-'))
            title_item.setFont(QFont("Segoe UI", 13))
            self.table.setItem(i, 0, title_item)

            artist_item = QTableWidgetItem(entry.get('artist', '-'))
            artist_item.setFont(QFont("Segoe UI", 13))
            self.table.setItem(i, 1, artist_item)

            fmt_item = QTableWidgetItem(entry.get('format', '-'))
            fmt_item.setTextAlignment(Qt.AlignCenter)
            fmt_item.setFont(QFont("Segoe UI", 13, QFont.Bold))
            if entry.get('format') == 'MP4':
                fmt_item.setForeground(QColor('#f44336'))
            else:
                fmt_item.setForeground(QColor('#4caf50'))
            self.table.setItem(i, 2, fmt_item)

            size = entry.get('size', 0)
            if size > 1048576:
                size_str = f"{size / 1048576:.1f} MB"
            elif size > 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size} B"
            size_item = QTableWidgetItem(size_str)
            size_item.setTextAlignment(Qt.AlignCenter)
            size_item.setFont(QFont("Segoe UI", 13))
            self.table.setItem(i, 3, size_item)

            date_item = QTableWidgetItem(entry.get('date', '-'))
            date_item.setFont(QFont("Segoe UI", 13))
            self.table.setItem(i, 4, date_item)

            path_item = QTableWidgetItem(entry.get('filepath', '-'))
            path_item.setFont(QFont("Segoe UI", 12))
            self.table.setItem(i, 5, path_item)

    def get_selected_entry(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        return self.history[rows[0].row()]

    def open_folder(self):
        entry = self.get_selected_entry()
        if not entry:
            QMessageBox.information(self, "Info", "Selecciona una entrada del historial.")
            return
        filepath = entry.get('filepath', '')
        if filepath and os.path.exists(filepath):
            os.startfile(os.path.dirname(filepath))
        else:
            QMessageBox.warning(self, "Error", "El archivo no existe.")

    def redownload(self):
        entry = self.get_selected_entry()
        if not entry:
            QMessageBox.information(self, "Info", "Selecciona una entrada del historial.")
            return
        url = entry.get('url', '')
        if not url:
            QMessageBox.warning(self, "Error", "No hay URL guardada.")
            return
        self.main.url_input.setText(url)
        self.main.tabs.setCurrentIndex(0)
        self.main.download_tab.fetch_info()

    def delete_selected(self):
        entry = self.get_selected_entry()
        if not entry:
            QMessageBox.information(self, "Info", "Selecciona una entrada del historial.")
            return
        reply = QMessageBox.question(
            self, "Eliminar",
            f"Eliminar '{entry.get('title', '-')}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            rows = self.table.selectionModel().selectedRows()
            if rows:
                self.history.pop(rows[0].row())
                self.save_history()
                self.refresh_table()

    def clear_history(self):
        if not self.history:
            return
        reply = QMessageBox.question(
            self, "Limpiar historial",
            f"Eliminar las {len(self.history)} descargas?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.history = []
            self.save_history()
            self.refresh_table()
