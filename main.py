# main.py
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QProgressBar
from PySide6.QtCore import QThread, QTimer
from nuvem.config_loader import load_config
from nuvem.logger import log
from nuvem.network import test_connection
from nuvem.speedtest import SpeedTest
from nuvem.network_worker import SpeedTestWorker
from nuvem.alternative_speedtest import AlternativeSpeedTestWindow  # Fallback visual

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetBR")
        self.setGeometry(100, 100, 400, 300)

        self.label = QLabel("Clique para testar conexão")
        self.button = QPushButton("Executar Testes")
        self.button.clicked.connect(self.executar_testes)

        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.statusBar().addWidget(self.progress_bar)

        # Instância do SpeedTest
        self.speedtest = SpeedTest()

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def executar_testes(self):
        self.label.setText("Executando testes de conexão...")
        self.progress_bar.setRange(0, 0)  # Mostra barra indeterminada durante os testes
        self.button.setEnabled(False)
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
            # Mensagem removida para não indicar sucesso antes do teste de velocidade
            pass
        else:
            self.label.setText("\n".join(resultados) + "\nIniciando teste de velocidade...")

        QApplication.processEvents()

        # Inicie o teste de velocidade em uma thread separada
        self.speedtest_thread = QThread()
        self.speedtest_worker = SpeedTestWorker()
        self.speedtest_worker.moveToThread(self.speedtest_thread)
        self.speedtest_thread.started.connect(self.speedtest_worker.run)
        self.speedtest_worker.finished.connect(self.on_speedtest_finished)
        self.speedtest_worker.error.connect(self.on_speedtest_error)
        self.speedtest_worker.finished.connect(self.speedtest_thread.quit)
        self.speedtest_worker.finished.connect(self.speedtest_worker.deleteLater)
        self.speedtest_thread.finished.connect(self.speedtest_thread.deleteLater)

        # Timer para timeout de 10 segundos
        self.speedtest_timeout_timer = QTimer()
        self.speedtest_timeout_timer.setSingleShot(True)
        self.speedtest_timeout_timer.timeout.connect(self.on_speedtest_timeout)

        self.speedtest_thread.start()
        self.speedtest_timeout_timer.start(40000)  # 30 segundos

    def on_speedtest_finished(self, result):
        self.speedtest_timeout_timer.stop()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.button.setEnabled(True)
        download = result.get("download")
        upload = result.get("upload")
        ping = result.get("ping")
        jitter = result.get("jitter")

        # Carrega requisitos de velocidade
        import os, json
        config_path = os.path.join(os.path.dirname(__file__), "config", "conf.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        req = config.get("speed_requirements", {})
        ok = True
        mensagens = []
        if req.get("required", False):
            if download is not None and download < req.get("download_min_mbps", 0):
                ok = False
                mensagens.append(f"Download abaixo do mínimo: {download} Mbps < {req.get('download_min_mbps')} Mbps")
            if upload is not None and upload < req.get("upload_min_mbps", 0):
                ok = False
                mensagens.append(f"Upload abaixo do mínimo: {upload} Mbps < {req.get('upload_min_mbps')} Mbps")
            if ping is not None and ping > req.get("ping_max_ms", 9999):
                ok = False
                mensagens.append(f"Ping acima do máximo: {ping} ms > {req.get('ping_max_ms')} ms")
            if jitter is not None and jitter > req.get("jitter_max_ms", 9999):
                ok = False
                mensagens.append(f"Jitter acima do máximo: {jitter} ms > {req.get('jitter_max_ms')} ms")

        if download is not None:
            resultado_velocidade = (
                f"Download: {download} Mbps\n"
                f"Upload: {upload} Mbps\n"
                f"Ping: {ping} ms\n"
                f"Jitter: {jitter} ms"
            )
        else:
            resultado_velocidade = "Erro ao medir velocidade."
        log(resultado_velocidade)

        if req.get("required", False):
            if ok:
                resultado_velocidade += "\nTodos os requisitos mínimos de velocidade foram atendidos!"
            else:
                resultado_velocidade += "\n" + "\n".join(mensagens)

        self.label.setText(self.label.text() + "\n" + resultado_velocidade)

    def on_speedtest_error(self, error_msg):
        self.speedtest_timeout_timer.stop()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.button.setEnabled(True)
        log(f"Speedtest falhou: {error_msg}")
        self.label.setText(self.label.text() + "\nSpeedtest falhou. Abrindo alternativa...")
        self.abrir_speedtest_alternativo()

    def on_speedtest_timeout(self):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.button.setEnabled(True)
        log("Speedtest demorou demais. Abrindo alternativa.")
        self.label.setText(self.label.text() + "\nSpeedtest demorou demais. Abrindo alternativa...")
        self.abrir_speedtest_alternativo()
        # Opcional: você pode tentar cancelar a thread, mas QThread não cancela facilmente threads Python.

    def abrir_speedtest_alternativo(self):
        self.alt_window = AlternativeSpeedTestWindow()
        self.alt_window.show()

    def start_tests(self):
        self.button.setEnabled(False)
        self.progress_bar.setRange(0, 0)
        # self.worker_thread.start()  # Removido, pois não há mais worker_thread

    def update_progress(self, message):
        self.statusBar().showMessage(message)

    def update_results(self, results):
        # Atualize conforme necessidade
        self.button.setEnabled(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
