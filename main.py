# main.py
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from nuvem.config_loader import load_config
from nuvem.logger import log
from nuvem.network import test_connection

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetBR")
        self.setGeometry(100, 100, 400, 300)

        self.label = QLabel("Clique para testar conexão")
        self.button = QPushButton("Executar Testes")
        self.button.clicked.connect(self.executar_testes)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def executar_testes(self):
        testes = load_config()
        resultados = []

        for teste in testes:
            host = teste["host"]
            port = teste["port"]
            required = teste["required"]
            conectado = test_connection(host, port)

            status = "OK" if conectado else "FALHA"
            resultado = f"{host}:{port} - {status}"
            log(resultado)

            if not conectado and required:
                resultados.append(f"FALHA CRÍTICA: {host}:{port}")
            elif not conectado:
                resultados.append(f"ALERTA: {host}:{port} falhou")

        if not resultados:
            self.label.setText("Todos os testes obrigatórios passaram!")
        else:
            self.label.setText("\n".join(resultados))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
