import sys
import os
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QProgressBar,
    QFrame, QHBoxLayout, QFileDialog, QMessageBox, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.download_worker import DownloadWorker, InfoWorker
from gui.history_tab import HistoryTab
from gui.settings_tab import SettingsTab
from utils.config_utils import load_config
from utils.url_utils import is_youtube_url, sanitize_youtube_url
from core.content_detector import ContentDetector


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TubeToAlbum")
        self.setMinimumSize(1000, 750)
        self.resize(1080, 820)

        self.config = load_config()
        self.detector = ContentDetector()
        self.current_info = None
        self.current_analysis = None
        self.download_worker = None
        self.info_worker = None

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(70)
        header.setStyleSheet("background-color: #004d40; border-bottom: 1px solid #00695c;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(40, 0, 40, 0)

        brand = QLabel("TubeToAlbum")
        brand.setFont(QFont("Segoe UI", 22, QFont.Bold))
        brand.setStyleSheet("color: #00e5ff;")
        header_layout.addWidget(brand)

        header_layout.addStretch()

        tagline = QLabel("Descarga profesional de YouTube a MP3/MP4")
        tagline.setFont(QFont("Segoe UI", 13))
        tagline.setStyleSheet("color: #80cbc4;")
        header_layout.addWidget(tagline)

        layout.addWidget(header)

        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(self.tabs)

        self.download_tab = DownloadTab(self)
        self.history_tab = HistoryTab(self)
        self.settings_tab = SettingsTab(self)

        self.tabs.addTab(self.download_tab, "   Descargar   ")
        self.tabs.addTab(self.history_tab, "   Historial   ")
        self.tabs.addTab(self.settings_tab, "   Configuracion   ")

        self.statusBar().setStyleSheet("font-size: 12px; padding: 4px;")
        self.statusBar().showMessage("Listo")

    def closeEvent(self, event):
        if self.download_worker and self.download_worker.isRunning():
            reply = QMessageBox.question(
                self, "Descarga en curso",
                "Hay una descarga en curso. Seguro que quieres cerrar?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
            self.download_worker.cancel()
        event.accept()


class DownloadTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 32, 40, 32)
        layout.setSpacing(24)

        url_group = QGroupBox("  URL de YouTube  ")
        url_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        url_layout = QHBoxLayout(url_group)
        url_layout.setSpacing(16)
        url_layout.setContentsMargins(24, 32, 24, 24)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        self.url_input.setMinimumHeight(52)
        self.url_input.setFont(QFont("Segoe UI", 15))
        self.url_input.returnPressed.connect(self.fetch_info)
        url_layout.addWidget(self.url_input)

        self.fetch_btn = QPushButton("Obtener Info")
        self.fetch_btn.setMinimumHeight(52)
        self.fetch_btn.setMinimumWidth(160)
        self.fetch_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.fetch_btn.clicked.connect(self.fetch_info)
        url_layout.addWidget(self.fetch_btn)
        layout.addWidget(url_group)

        preview_group = QGroupBox("  Vista previa  ")
        preview_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        preview_layout = QHBoxLayout(preview_group)
        preview_layout.setSpacing(28)
        preview_layout.setContentsMargins(24, 32, 24, 24)

        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(280, 158)
        self.thumb_label.setStyleSheet("background-color: #263238; border-radius: 10px;")
        self.thumb_label.setAlignment(Qt.AlignCenter)
        self.thumb_label.setText("Sin imagen")
        self.thumb_label.setFont(QFont("Segoe UI", 12))
        preview_layout.addWidget(self.thumb_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(10)

        self.title_label = QLabel("Titulo: -")
        self.title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.title_label.setWordWrap(True)
        info_layout.addWidget(self.title_label)

        self.artist_label = QLabel("Canal: -")
        self.artist_label.setFont(QFont("Segoe UI", 14))
        info_layout.addWidget(self.artist_label)

        self.type_label = QLabel("Tipo: -")
        self.type_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        info_layout.addWidget(self.type_label)

        self.duration_label = QLabel("Duracion: -")
        self.duration_label.setFont(QFont("Segoe UI", 13))
        self.duration_label.setStyleSheet("color: #b0bec5;")
        info_layout.addWidget(self.duration_label)

        self.reason_label = QLabel("")
        self.reason_label.setFont(QFont("Segoe UI", 12))
        self.reason_label.setStyleSheet("color: #78909c;")
        self.reason_label.setWordWrap(True)
        info_layout.addWidget(self.reason_label)

        info_layout.addStretch()
        preview_layout.addLayout(info_layout, 1)
        layout.addWidget(preview_group)

        options_group = QGroupBox("  Opciones de descarga  ")
        options_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        options_layout = QHBoxLayout(options_group)
        options_layout.setSpacing(32)
        options_layout.setContentsMargins(24, 32, 24, 24)

        fmt_layout = QVBoxLayout()
        fmt_layout.setSpacing(8)
        fmt_label = QLabel("Formato")
        fmt_label.setFont(QFont("Segoe UI", 12))
        fmt_layout.addWidget(fmt_label)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP3", "M4A", "MP4"])
        self.format_combo.setMinimumHeight(48)
        self.format_combo.setFont(QFont("Segoe UI", 14))
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        fmt_layout.addWidget(self.format_combo)
        options_layout.addLayout(fmt_layout)

        qual_layout = QVBoxLayout()
        qual_layout.setSpacing(8)
        qual_label = QLabel("Calidad")
        qual_label.setFont(QFont("Segoe UI", 12))
        qual_layout.addWidget(qual_label)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["128 kbps", "192 kbps", "256 kbps", "320 kbps"])
        self.quality_combo.setMinimumHeight(48)
        self.quality_combo.setFont(QFont("Segoe UI", 14))
        qual_layout.addWidget(self.quality_combo)
        options_layout.addLayout(qual_layout)

        dir_layout = QVBoxLayout()
        dir_layout.setSpacing(8)
        dir_label = QLabel("Guardar en")
        dir_label.setFont(QFont("Segoe UI", 12))
        dir_layout.addWidget(dir_label)
        dir_row = QHBoxLayout()
        dir_row.setSpacing(12)
        self.output_input = QLineEdit()
        self.output_input.setText(os.path.expanduser("~/Music"))
        self.output_input.setMinimumHeight(48)
        self.output_input.setFont(QFont("Segoe UI", 13))
        dir_row.addWidget(self.output_input)
        browse_btn = QPushButton("Examinar")
        browse_btn.setMinimumHeight(48)
        browse_btn.setMinimumWidth(110)
        browse_btn.setFont(QFont("Segoe UI", 13))
        browse_btn.clicked.connect(self.browse_folder)
        dir_row.addWidget(browse_btn)
        dir_layout.addLayout(dir_row)
        options_layout.addLayout(dir_layout, 1)
        layout.addWidget(options_group)

        progress_group = QGroupBox("  Progreso  ")
        progress_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setSpacing(12)
        progress_layout.setContentsMargins(24, 32, 24, 24)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(28)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFont(QFont("Segoe UI", 12, QFont.Bold))
        progress_layout.addWidget(self.progress_bar)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(32)
        self.status_label = QLabel("Esperando URL...")
        self.status_label.setFont(QFont("Segoe UI", 13))
        stats_row.addWidget(self.status_label)
        stats_row.addStretch()
        self.speed_label = QLabel("")
        self.speed_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        stats_row.addWidget(self.speed_label)
        self.eta_label = QLabel("")
        self.eta_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        stats_row.addWidget(self.eta_label)
        progress_layout.addLayout(stats_row)
        layout.addWidget(progress_group)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        btn_layout.addStretch()

        self.download_btn = QPushButton("Descargar")
        self.download_btn.setProperty("class", "success")
        self.download_btn.setMinimumHeight(56)
        self.download_btn.setMinimumWidth(200)
        self.download_btn.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setEnabled(False)
        btn_layout.addWidget(self.download_btn)

        self.queue_btn = QPushButton("Agregar a Cola")
        self.queue_btn.setMinimumHeight(56)
        self.queue_btn.setMinimumWidth(180)
        self.queue_btn.setFont(QFont("Segoe UI", 14))
        self.queue_btn.setEnabled(False)
        btn_layout.addWidget(self.queue_btn)

        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setProperty("class", "danger")
        self.cancel_btn.setMinimumHeight(56)
        self.cancel_btn.setMinimumWidth(140)
        self.cancel_btn.setFont(QFont("Segoe UI", 14))
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_download)
        btn_layout.addWidget(self.cancel_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        layout.addStretch()

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        if folder:
            self.output_input.setText(folder)

    def on_format_changed(self, fmt):
        self.quality_combo.clear()
        if fmt == "MP4":
            self.quality_combo.addItems(["360p", "480p", "720p", "1080p", "Mejor calidad"])
            self.output_input.setText(os.path.expanduser("~/Downloads/TubeToAlbum"))
        else:
            self.quality_combo.addItems(["128 kbps", "192 kbps", "256 kbps", "320 kbps"])
            self.output_input.setText(os.path.expanduser("~/Music"))

    def fetch_info(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Pega una URL de YouTube primero.")
            return
        if not is_youtube_url(url):
            QMessageBox.warning(self, "Error", "La URL no es valida.")
            return

        self.fetch_btn.setEnabled(False)
        self.fetch_btn.setText("Obteniendo...")
        self.title_label.setText("Buscando informacion...")
        self.artist_label.setText("Canal: ...")
        self.type_label.setText("Tipo: analizando...")
        self.type_label.setStyleSheet("")
        self.duration_label.setText("Duracion: ...")
        self.reason_label.setText("")
        self.thumb_label.setText("Cargando...")
        self.main.statusBar().showMessage("Obteniendo informacion del video...")

        self.info_worker = InfoWorker(url)
        self.info_worker.finished.connect(self.on_info_ready)
        self.info_worker.error.connect(self.on_info_error)
        self.info_worker.start()

    def on_info_ready(self, info, analysis):
        self.main.current_info = info
        self.main.current_analysis = analysis

        self.title_label.setText(f"Titulo: {info.get('title', '-')}")
        self.artist_label.setText(f"Canal: {info.get('artist', '-')}")

        duration = info.get('duration', 0)
        mins = int(duration) // 60
        secs = int(duration) % 60
        self.duration_label.setText(f"Duracion: {mins}:{secs:02d}")

        if analysis['is_music']:
            self.type_label.setText("MUSICA")
            self.type_label.setStyleSheet("color: #4caf50; font-weight: bold; font-size: 14px;")
        else:
            self.type_label.setText("OTRO CONTENIDO")
            self.type_label.setStyleSheet("color: #f44336; font-weight: bold; font-size: 14px;")

        reasons = " | ".join(analysis['reasons'])
        self.reason_label.setText(reasons)

        if analysis['suggested_artist']:
            self.artist_label.setText(f"Canal: {analysis['suggested_artist']}")

        if analysis['is_music']:
            self.format_combo.setCurrentText("MP3")
            self.output_input.setText(os.path.expanduser("~/Music"))
        else:
            self.format_combo.setCurrentText("MP4")
            self.output_input.setText(os.path.expanduser("~/Downloads/TubeToAlbum"))

        thumb_url = info.get('thumbnail')
        if thumb_url:
            try:
                import requests
                resp = requests.get(thumb_url, timeout=5)
                if resp.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(resp.content)
                    self.thumb_label.setPixmap(
                        pixmap.scaled(280, 158, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                else:
                    self.thumb_label.setText("Sin imagen")
            except Exception:
                self.thumb_label.setText("Sin imagen")
        else:
            self.thumb_label.setText("Sin imagen")

        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("Obtener Info")
        self.download_btn.setEnabled(True)
        self.main.statusBar().showMessage("Informacion obtenida - listo para descargar")

    def on_info_error(self, error):
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("Obtener Info")
        self.title_label.setText("Error al obtener informacion")
        self.artist_label.setText("")
        self.type_label.setText("")
        self.type_label.setStyleSheet("")
        self.duration_label.setText("")
        self.reason_label.setText(str(error))
        self.thumb_label.setText("Sin imagen")
        self.main.statusBar().showMessage("Error al obtener informacion")
        QMessageBox.critical(self, "Error", f"No se pudo obtener la informacion:\n{error}")

    def start_download(self):
        url = self.url_input.text().strip()
        if not url or not self.main.current_info:
            return

        url = sanitize_youtube_url(url)
        fmt = self.format_combo.currentText().lower()
        quality_text = self.quality_combo.currentText()

        if fmt == "mp4":
            quality_map = {
                "360p": "360", "480p": "480", "720p": "720",
                "1080p": "1080", "Mejor calidad": "best"
            }
            quality = quality_map.get(quality_text, "720")
        else:
            quality = quality_text.replace(" kbps", "")

        output_dir = self.output_input.text().strip()
        is_music = self.main.current_analysis['is_music'] if self.main.current_analysis else True

        self.download_btn.setEnabled(False)
        self.queue_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Iniciando descarga...")
        self.speed_label.setText("")
        self.eta_label.setText("")

        self.download_worker = DownloadWorker(
            url=url, fmt=fmt, quality=quality,
            output_dir=output_dir, is_music=is_music,
            config=self.main.config
        )
        self.download_worker.progress_updated.connect(self.on_progress)
        self.download_worker.download_finished.connect(self.on_download_finished)
        self.download_worker.download_error.connect(self.on_download_error)
        self.download_worker.start()

        self.main.statusBar().showMessage(f"Descargando: {self.main.current_info.get('title', '')}")

    def cancel_download(self):
        if self.download_worker and self.download_worker.isRunning():
            self.download_worker.cancel()
            self.status_label.setText("Cancelado")
            self.speed_label.setText("")
            self.eta_label.setText("")
            self.main.statusBar().showMessage("Descarga cancelada")
            self.reset_buttons()

    def on_progress(self, percent, speed, eta):
        self.progress_bar.setValue(int(percent))
        self.speed_label.setText(speed)
        self.eta_label.setText(f"ETA: {eta}")
        self.status_label.setText(f"Descargando... {percent:.1f}%")

    def on_download_finished(self, filepath):
        self.status_label.setText("Descarga completada!")
        self.progress_bar.setValue(100)
        self.speed_label.setText("")
        self.eta_label.setText("")
        self.main.statusBar().showMessage(f"Guardado en: {filepath}")
        self.reset_buttons()

        self.main.history_tab.add_entry(
            self.main.current_info, filepath,
            self.format_combo.currentText().lower()
        )

        QMessageBox.information(
            self, "Completado",
            f"Archivo guardado en:\n{filepath}"
        )

    def on_download_error(self, error):
        self.status_label.setText("Error en la descarga")
        self.speed_label.setText("")
        self.eta_label.setText("")
        self.main.statusBar().showMessage("Error en la descarga")
        self.reset_buttons()
        QMessageBox.critical(self, "Error", f"Error en la descarga:\n{error}")

    def reset_buttons(self):
        self.download_btn.setEnabled(True)
        self.queue_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
