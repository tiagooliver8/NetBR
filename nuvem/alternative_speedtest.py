# nuvem/alternative_speedtest.py
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl

class AlternativeSpeedTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Teste Alternativo de Velocidade")
        self.setGeometry(150, 150, 800, 600)

        self.webview = QWebEngineView()
        self.webview.load(QUrl("https://openspeedtest.com/speedtest"))

        layout = QVBoxLayout()
        layout.addWidget(self.webview)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
