# main.py
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from core.network import ping_host

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetBR")
        self.setGeometry(100, 100, 300, 200)

        self.label = QLabel("Clique para testar conexão")
        self.button = QPushButton("Testar")
        self.button.clicked.connect(self.testar_conexao)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def testar_conexao(self):
        if ping_host("8.8.8.8"):
            self.label.setText("Conectado à Internet")
        else:
            self.label.setText("Sem conexão")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
