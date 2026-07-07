import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from qt_material import apply_stylesheet

from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("TubeToAlbum")
    app.setStyle("Fusion")

    extra = {
        'danger': '#dc3545',
        'warning': '#ffc107',
        'success': '#28a745',
        'font_family': 'Segoe UI',
        'font_size': '13px',
        'density_scale': '0',
    }

    apply_stylesheet(app, theme='dark_teal.xml', extra=extra)

    custom_css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'custom.css')
    if os.path.exists(custom_css_path):
        with open(custom_css_path, 'r') as f:
            app.setStyleSheet(app.styleSheet() + f.read())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
