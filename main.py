# main.py
import sys
import os, json
import time
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QProgressBar
from PySide6.QtCore import QThread, QTimer
from nuvem.logger import log
from nuvem.network_worker import SpeedTestWorker, NetworkWorker
from nuvem.alternative_speedtest import AlternativeSpeedTestWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetBR")
        self.setGeometry(100, 100, 400, 300)

        self.label = QLabel("Clique para testar conexão")
        self.button = QPushButton("Executar Testes")
        self.button.clicked.connect(self.executar_testes)
        self.progress_bar = QProgressBar()

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        layout.addWidget(self.progress_bar)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Carrega o conf.json uma vez
        config_path = os.path.join(os.path.dirname(__file__), "config", "conf.json")
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

    def executar_testes(self):
        self.label.setText("")
        self.progress_bar.setRange(0, 0)
        self.button.setEnabled(False)
        QApplication.processEvents()

        self.network_thread = QThread()
        self.network_worker = NetworkWorker()
        self.network_worker.moveToThread(self.network_thread)
        self.network_thread.started.connect(self.network_worker.run_tests)
        self.network_worker.progress.connect(self.update_progress)
        self.network_worker.result.connect(self.update_results)
        self.network_worker.finished.connect(self.on_network_finished)
        self.network_worker.finished.connect(self.network_thread.quit)
        self.network_worker.finished.connect(self.network_worker.deleteLater)
        self.network_thread.finished.connect(self.network_thread.deleteLater)
        self.network_thread.start()

    def update_progress(self, message):
        self.label.setText(message)

    def update_results(self, results):
        self.label.setText("\n".join(results))

    def on_network_finished(self, results):
        self.label.setText(self.label.text() + "\nIniciando teste de velocidade...")
        QApplication.processEvents()

        self.speedtest_thread = QThread()
        timeout_seconds = self.config.get("speedtest_timeout", 40)
        self.speedtest_worker = SpeedTestWorker(timeout=timeout_seconds)
        self.speedtest_worker.moveToThread(self.speedtest_thread)
        self.speedtest_thread.started.connect(self.speedtest_worker.run)
        self.speedtest_worker.finished.connect(self.on_speedtest_finished)
        self.speedtest_worker.error.connect(self.on_speedtest_error)
        self.speedtest_worker.finished.connect(self.speedtest_thread.quit)
        self.speedtest_worker.finished.connect(self.speedtest_worker.deleteLater)
        self.speedtest_thread.finished.connect(self.speedtest_thread.deleteLater)

        self.speedtest_timeout_timer = QTimer()
        self.speedtest_timeout_timer.setSingleShot(True)
        self.speedtest_timeout_timer.timeout.connect(self.on_speedtest_timeout)
        self.speedtest_thread.start()
        self.speedtest_timeout_timer.start(timeout_seconds * 1000)

    def on_speedtest_finished(self, result):
        self.speedtest_timeout_timer.stop()
        self.last_speedtest_update = time.time()  # Marca o momento da última atualização
        download = result.get("download")
        upload = result.get("upload")
        ping = result.get("ping")
        jitter = result.get("jitter")

        msg = (
            f"Download: {download} Mbps\n"
            f"Upload: {upload} Mbps\n"
            f"Ping: {ping} ms\n"
            f"Jitter: {jitter} ms"
        )
        log(msg)
        self.label.setText(self.label.text() + "\n" + msg)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.button.setEnabled(True)

    def on_speedtest_error(self, error_msg):
        self.speedtest_timeout_timer.stop()
        self.last_speedtest_update = time.time()  # Marca o momento da última atualização
        log(f"Speedtest falhou: {error_msg}")
        self.label.setText(self.label.text() + "\nSpeedtest falhou. Abrindo alternativa...")
        self.abrir_speedtest_alternativo()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.button.setEnabled(True)

    def on_speedtest_timeout(self):
        # Só aciona o alternative_speedtest se o tempo desde a última atualização for maior que o timeout
        timeout_seconds = self.config.get("speedtest_timeout", 40)
        now = time.time()
        if not hasattr(self, "last_speedtest_update") or (now - self.last_speedtest_update) >= timeout_seconds:
            log("Speedtest demorou demais. Abrindo alternativa.")
            self.label.setText(self.label.text() + "\nSpeedtest demorou demais. Abrindo alternativa...")
            self.abrir_speedtest_alternativo()
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            self.button.setEnabled(True)
        else:
            # Reagenda o timeout para o tempo restante
            restante = int(timeout_seconds - (now - self.last_speedtest_update))
            self.speedtest_timeout_timer.start(restante * 1000)

    def abrir_speedtest_alternativo(self):
        self.alt_window = AlternativeSpeedTestWindow()
        self.alt_window.show()

if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
