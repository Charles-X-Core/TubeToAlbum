import sys
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox,
    QLineEdit, QCheckBox, QPushButton, QLabel, QGroupBox,
    QFileDialog, QMessageBox, QSpinBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_utils import load_config, save_config, DEFAULT_CONFIG


class SettingsTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.config = load_config()
        self.config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 32, 40, 32)
        layout.setSpacing(24)

        title = QLabel("Configuracion")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        layout.addWidget(title)

        defaults_group = QGroupBox("  Valores por defecto  ")
        defaults_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        defaults_layout = QFormLayout(defaults_group)
        defaults_layout.setSpacing(16)
        defaults_layout.setContentsMargins(24, 32, 24, 24)
        defaults_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["128", "192", "256", "320"])
        self.quality_combo.setMinimumHeight(48)
        self.quality_combo.setFont(QFont("Segoe UI", 14))
        current_quality = self.config.get('default_quality', '192')
        idx = self.quality_combo.findText(current_quality)
        if idx >= 0:
            self.quality_combo.setCurrentIndex(idx)
        defaults_layout.addRow("Calidad por defecto:", self.quality_combo)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp3", "m4a", "mp4"])
        self.format_combo.setMinimumHeight(48)
        self.format_combo.setFont(QFont("Segoe UI", 14))
        current_format = self.config.get('default_format', 'mp3')
        idx = self.format_combo.findText(current_format)
        if idx >= 0:
            self.format_combo.setCurrentIndex(idx)
        defaults_layout.addRow("Formato por defecto:", self.format_combo)
        layout.addWidget(defaults_group)

        paths_group = QGroupBox("  Carpetas de destino  ")
        paths_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        paths_layout = QFormLayout(paths_group)
        paths_layout.setSpacing(16)
        paths_layout.setContentsMargins(24, 32, 24, 24)
        paths_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        music_row = QHBoxLayout()
        music_row.setSpacing(12)
        self.music_input = QLineEdit()
        self.music_input.setText(os.path.expanduser(self.config.get('default_output_dir', '~/Music')))
        self.music_input.setMinimumHeight(48)
        self.music_input.setFont(QFont("Segoe UI", 13))
        music_row.addWidget(self.music_input)
        music_browse = QPushButton("Examinar")
        music_browse.setMinimumHeight(48)
        music_browse.setMinimumWidth(110)
        music_browse.setFont(QFont("Segoe UI", 13))
        music_browse.clicked.connect(lambda: self.browse_folder(self.music_input))
        music_row.addWidget(music_browse)
        paths_layout.addRow("Musica:", music_row)

        other_row = QHBoxLayout()
        other_row.setSpacing(12)
        self.other_input = QLineEdit()
        self.other_input.setText(os.path.expanduser(
            self.config.get('non_music_output_dir', '~/Downloads/TubeToAlbum')))
        self.other_input.setMinimumHeight(48)
        self.other_input.setFont(QFont("Segoe UI", 13))
        other_row.addWidget(self.other_input)
        other_browse = QPushButton("Examinar")
        other_browse.setMinimumHeight(48)
        other_browse.setMinimumWidth(110)
        other_browse.setFont(QFont("Segoe UI", 13))
        other_browse.clicked.connect(lambda: self.browse_folder(self.other_input))
        other_row.addWidget(other_browse)
        paths_layout.addRow("Otros contenidos:", other_row)
        layout.addWidget(paths_group)

        metadata_group = QGroupBox("  Metadata  ")
        metadata_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        metadata_layout = QVBoxLayout(metadata_group)
        metadata_layout.setSpacing(14)
        metadata_layout.setContentsMargins(24, 32, 24, 24)

        self.embed_thumb_check = QCheckBox("Embeber portada del video en MP3")
        self.embed_thumb_check.setChecked(self.config.get('embed_thumbnail', True))
        self.embed_thumb_check.setFont(QFont("Segoe UI", 14))
        metadata_layout.addWidget(self.embed_thumb_check)

        self.embed_meta_check = QCheckBox("Embeber metadata (artista, titulo, etc.)")
        self.embed_meta_check.setChecked(self.config.get('embed_metadata', True))
        self.embed_meta_check.setFont(QFont("Segoe UI", 14))
        metadata_layout.addWidget(self.embed_meta_check)

        self.clean_title_check = QCheckBox("Limpiar titulos (remover Official Video, etc.)")
        self.clean_title_check.setChecked(self.config.get('metadata', {}).get('clean_title', True))
        self.clean_title_check.setFont(QFont("Segoe UI", 14))
        metadata_layout.addWidget(self.clean_title_check)

        self.overwrite_check = QCheckBox("Sobrescribir archivos existentes")
        self.overwrite_check.setChecked(self.config.get('overwrite_existing', False))
        self.overwrite_check.setFont(QFont("Segoe UI", 14))
        metadata_layout.addWidget(self.overwrite_check)
        layout.addWidget(metadata_group)

        download_group = QGroupBox("  Descarga  ")
        download_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        download_layout = QFormLayout(download_group)
        download_layout.setSpacing(16)
        download_layout.setContentsMargins(24, 32, 24, 24)
        download_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.concurrent_spin = QSpinBox()
        self.concurrent_spin.setRange(1, 10)
        self.concurrent_spin.setMinimumHeight(48)
        self.concurrent_spin.setFont(QFont("Segoe UI", 14))
        self.concurrent_spin.setValue(self.config.get('download', {}).get('max_concurrent', 3))
        download_layout.addRow("Descargas simultaneas:", self.concurrent_spin)

        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(0, 10)
        self.retry_spin.setMinimumHeight(48)
        self.retry_spin.setFont(QFont("Segoe UI", 14))
        self.retry_spin.setValue(self.config.get('download', {}).get('retry_count', 3))
        download_layout.addRow("Reintentos:", self.retry_spin)
        layout.addWidget(download_group)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(20)
        btn_row.addStretch()

        save_btn = QPushButton("Guardar Configuracion")
        save_btn.setProperty("class", "success")
        save_btn.setMinimumHeight(56)
        save_btn.setMinimumWidth(240)
        save_btn.setFont(QFont("Segoe UI", 16, QFont.Bold))
        save_btn.clicked.connect(self.save_settings)
        btn_row.addWidget(save_btn)

        reset_btn = QPushButton("Restablecer por defecto")
        reset_btn.setMinimumHeight(56)
        reset_btn.setMinimumWidth(220)
        reset_btn.setFont(QFont("Segoe UI", 14))
        reset_btn.clicked.connect(self.reset_defaults)
        btn_row.addWidget(reset_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        layout.addStretch()

    def browse_folder(self, line_edit):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        if folder:
            line_edit.setText(folder)

    def save_settings(self):
        self.config['default_quality'] = self.quality_combo.currentText()
        self.config['default_format'] = self.format_combo.currentText()
        self.config['default_output_dir'] = self.music_input.text()
        self.config['non_music_output_dir'] = self.other_input.text()
        self.config['embed_thumbnail'] = self.embed_thumb_check.isChecked()
        self.config['embed_metadata'] = self.embed_meta_check.isChecked()
        self.config['overwrite_existing'] = self.overwrite_check.isChecked()

        if 'metadata' not in self.config:
            self.config['metadata'] = {}
        self.config['metadata']['clean_title'] = self.clean_title_check.isChecked()

        if 'download' not in self.config:
            self.config['download'] = {}
        self.config['download']['max_concurrent'] = self.concurrent_spin.value()
        self.config['download']['retry_count'] = self.retry_spin.value()

        try:
            save_config(self.config, self.config_path)
            self.main.config = self.config
            QMessageBox.information(self, "Guardado", "Configuracion guardada correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar:\n{e}")

    def reset_defaults(self):
        reply = QMessageBox.question(
            self, "Restablecer",
            "Restablecer toda la configuracion?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.config = DEFAULT_CONFIG.copy()
            self.quality_combo.setCurrentText(self.config.get('default_quality', '192'))
            self.format_combo.setCurrentText(self.config.get('default_format', 'mp3'))
            self.music_input.setText(os.path.expanduser(self.config.get('default_output_dir', '~/Music')))
            self.other_input.setText(
                os.path.expanduser(self.config.get('non_music_output_dir', '~/Downloads/TubeToAlbum')))
            self.embed_thumb_check.setChecked(self.config.get('embed_thumbnail', True))
            self.embed_meta_check.setChecked(self.config.get('embed_metadata', True))
            self.clean_title_check.setChecked(self.config.get('metadata', {}).get('clean_title', True))
            self.overwrite_check.setChecked(self.config.get('overwrite_existing', False))
            self.concurrent_spin.setValue(self.config.get('download', {}).get('max_concurrent', 3))
            self.retry_spin.setValue(self.config.get('download', {}).get('retry_count', 3))
            QMessageBox.information(self, "Restablecido", "Configuracion restablecida.")
