# main.py
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QProgressBar
from PySide6.QtCore import QThread
from nuvem.config_loader import load_config
from nuvem.logger import log
from nuvem.network import test_connection
from nuvem.speedtest import SpeedTest
from nuvem.network_worker import NetworkWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetBR")
        self.setGeometry(100, 100, 400, 300)

        self.label = QLabel("Clique para testar conexão")
        self.button = QPushButton("Executar Testes")
        self.button.clicked.connect(self.executar_testes)

        # Adicione uma barra de progresso
        self.progress_bar = QProgressBar()
        self.statusBar().addWidget(self.progress_bar)

        # Configure o worker e thread
        self.worker_thread = QThread()
        self.worker = NetworkWorker()
        self.worker.moveToThread(self.worker_thread)

        # Conecte os sinais
        self.worker_thread.started.connect(self.worker.run_tests)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker.progress.connect(self.update_progress)
        self.worker.result.connect(self.update_results)

        # Instancie o SpeedTest para uso posterior
        self.speedtest = SpeedTest()

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def executar_testes(self):
        self.label.setText("Executando testes de conexão...")
        QApplication.processEvents()

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
            self.label.setText("Todos os testes obrigatórios passaram!\nIniciando teste de velocidade...")
        else:
            self.label.setText("\n".join(resultados) + "\nIniciando teste de velocidade...")
        QApplication.processEvents()

        # Corrigido: usar SpeedTest ao invés de medir_velocidade
        speed_result = self.speedtest.run_test()
        download = speed_result.get("download")
        upload = speed_result.get("upload")

        if download is not None:
            resultado_velocidade = f"Download: {download} Mbps\nUpload: {upload} Mbps"
        else:
            resultado_velocidade = "Erro ao medir velocidade."

        log(resultado_velocidade)

        self.label.setText(self.label.text() + "\n" + resultado_velocidade)

    def start_tests(self):
        # Desabilite o botão durante os testes
        self.button.setEnabled(False)
        self.progress_bar.setRange(0, 0)  # Modo indeterminado
        self.worker_thread.start()

    def update_progress(self, message):
        self.statusBar().showMessage(message)

    def update_results(self, results):
        # Atualize a interface com os resultados
        # ...existing code...
        self.button.setEnabled(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
