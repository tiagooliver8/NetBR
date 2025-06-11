# main.py
import sys
import os, json
import time
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QProgressBar, QSpacerItem, QSizePolicy
from PySide6.QtCore import QThread, QTimer, Qt
from PySide6.QtGui import QPixmap, QFont
from nuvem.logger import log
from nuvem.network_worker import SpeedTestWorker, NetworkWorker
from nuvem.alternative_speedtest import AlternativeSpeedTestWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetBR")
        self.setFixedSize(400, 700)  # Tamanho fixo próximo ao mockup
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #b3b3b3, stop:1 #888888);
                border-radius: 32px;
            }
        """)

        # Topo: Caixa laranja com ícone nuvem e texto
        top_box = QWidget()
        top_box.setStyleSheet("""
            background: #ed7d31;
            border-radius: 16px;
            /* border: 2px solid #a65c1a; */
        """)
        top_layout = QVBoxLayout()
        top_layout.setContentsMargins(20, 10, 20, 10)
        top_layout.setSpacing(8)
        cloud_icon = QLabel()
        try:
            cloud_icon.setPixmap(QPixmap("resources/cloud.png").scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        except Exception:
            cloud_icon.setText("☁️")
            cloud_icon.setFont(QFont("Arial", 32))
        cloud_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_label = QLabel("Nuvem")
        top_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        top_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(cloud_icon)
        top_layout.addWidget(top_label)
        top_box.setLayout(top_layout)

        # Botão central
        self.button = QPushButton("TESTAR!")
        self.button.setMinimumHeight(80)
        self.button.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.button.setStyleSheet("""
            QPushButton {
                background: #17607a;
                color: white;
                border-radius: 16px;
                border: 2px solid #0e3c4a;
            }
            QPushButton:pressed {
                background: #10495a;
            }
        """)
        self.button.clicked.connect(self.executar_testes)

        # Rodapé: Caixa laranja com logo Mersen
        bottom_box = QWidget()
        bottom_box.setStyleSheet("""
            background: #ed7d31;
            border-radius: 16px;
            /* border: 2px solid #a65c1a; */
        """)
        bottom_layout = QVBoxLayout()
        bottom_layout.setContentsMargins(20, 10, 20, 10)
        bottom_layout.setSpacing(8)
        mersen_logo = QLabel()
        try:
            mersen_logo.setPixmap(QPixmap("resources/mersen.png").scaled(180, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        except Exception:
            mersen_logo.setText("MERSEN")
            mersen_logo.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        mersen_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bottom_layout.addWidget(mersen_logo)
        bottom_box.setLayout(bottom_layout)

        # Retângulo de exibição dos textos (QWidget com fundo cinza claro)
        self.text_box = QWidget()
        self.text_box.setStyleSheet("background: #e0e0e0; border: 2px solid #444; border-radius: 8px;")
        self.text_box_layout = QVBoxLayout()
        self.text_box_layout.setContentsMargins(18, 18, 18, 18)
        self.text_box_layout.setSpacing(0)
        self.text_box.setLayout(self.text_box_layout)

        # Adiciona barra de rolagem vertical para o label
        from PySide6.QtWidgets import QScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.label = QLabel("")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.label.setStyleSheet("color: #222; font-size: 18px;")
        self.label.hide()
        self.scroll_area.setWidget(self.label)
        self.text_box_layout.addWidget(self.scroll_area)
        self.text_box.hide()
        # Define altura máxima para não encostar no topo/rodapé
        self.text_box.setMinimumHeight(420)
        self.text_box.setMaximumHeight(420)

        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(18)
        self.progress_bar.setStyleSheet("QProgressBar { border-radius: 8px; }")

        # Layout principal
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(top_box)
        # Espaçadores para centralização dinâmica
        self.spacer_top = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.spacer_bottom = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.main_layout.addItem(self.spacer_top)
        self.main_layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addItem(self.spacer_bottom)
        self.main_layout.addWidget(self.text_box)
        self.main_layout.addWidget(self.progress_bar)
        self.main_layout.addWidget(bottom_box)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        # Carrega o conf.json uma vez
        config_path = os.path.join(os.path.dirname(__file__), "config", "conf.json")
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

    def executar_testes(self):
        # Remove o botão e ajusta os spacers para centralizar o text_box
        self.main_layout.removeWidget(self.button)
        self.button.hide()
        self.main_layout.removeItem(self.spacer_top)
        self.main_layout.removeItem(self.spacer_bottom)
        # Adiciona novos spacers para centralizar o text_box
        self.spacer_top_status = QSpacerItem(20, 80, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.spacer_bottom_status = QSpacerItem(20, 80, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.main_layout.insertItem(1, self.spacer_top_status)
        self.main_layout.insertItem(3, self.spacer_bottom_status)
        # Garante que o label está visível dentro do text_box
        self.label.show()
        self.text_box.show()
        self.label.setText("Iniciando testes de Velocidade e Conectividade")
        self.progress_bar.setRange(0, 0)
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
        # Adiciona a mensagem ao texto existente, sem apagar
        if not self.text_box.isVisible():
            self.text_box.show()
        if message.startswith("Testando "):
            self.label.setText(self.label.text() + "\n" + message)
        else:
            self.label.setText(self.label.text() + "\n    " + message)
        QApplication.processEvents()

    def update_results(self, results):
        # Adiciona os resultados ao texto existente, sem apagar
        for result in results:
            self.label.setText(self.label.text() + "\n    " + result)
        QApplication.processEvents()

    def on_network_finished(self, results):
        self.label.setText(self.label.text() + "\nIniciando teste de velocidade...")
        QApplication.processEvents()

        self.speedtest_thread = QThread()
        timeout_seconds = self.config.get("speedtest_timeout", 40)
        self.speedtest_worker = SpeedTestWorker(timeout=timeout_seconds)
        self.speedtest_worker.moveToThread(self.speedtest_thread)
        self.speedtest_thread.started.connect(self.speedtest_worker.run)
        self.speedtest_worker.progress.connect(self.update_speedtest_progress)
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

    def update_speedtest_progress(self, message):
        # Exibe mensagem de progresso do speedtest na interface
        self.label.setText(self.label.text() + "\n" + message)
        QApplication.processEvents()

    def on_speedtest_finished(self, result):
        # Se o fallback já foi aberto, ignore o resultado do speedtest
        if hasattr(self, "alt_window") and self.alt_window.isVisible():
            log("[INFO] Resultado do speedtest ignorado pois o fallback já foi aberto.")
            return
        self.speedtest_timeout_timer.stop()
        self.last_speedtest_update = time.time()  # Marca o momento da última atualização
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        # Não exibe novamente o resumo dos resultados (Download, Upload, Ping, Jitter)

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
        # Cancela o teste de velocidade se estiver rodando
        if hasattr(self, "speedtest_worker"):
            try:
                self.speedtest_worker.cancel()
            except Exception:
                pass
        if hasattr(self, "speedtest_thread") and self.speedtest_thread is not None:
            try:
                if self.speedtest_thread.isRunning():
                    self.speedtest_thread.quit()
                    self.speedtest_thread.wait(2000)
            except RuntimeError:
                pass
        # Cancela o network worker se estiver rodando
        if hasattr(self, "network_worker"):
            try:
                self.network_worker.cancel()
            except Exception:
                pass
        if hasattr(self, "network_thread") and self.network_thread is not None:
            try:
                if self.network_thread.isRunning():
                    self.network_thread.quit()
                    self.network_thread.wait(2000)
            except RuntimeError:
                pass
        self.alt_window = AlternativeSpeedTestWindow()
        self.alt_window.show()
        self.label.setText(self.label.text() + "\nTestes cancelados/interrompidos.")

    def closeEvent(self, event):
        # Cancela todos os workers e threads ao fechar a janela principal
        if hasattr(self, "speedtest_worker"):
            try:
                self.speedtest_worker.cancel()
            except Exception:
                pass
        if hasattr(self, "speedtest_thread") and self.speedtest_thread is not None:
            try:
                if self.speedtest_thread.isRunning():
                    self.speedtest_thread.quit()
                    self.speedtest_thread.wait(2000)
            except RuntimeError:
                pass
        if hasattr(self, "network_worker"):
            try:
                self.network_worker.cancel()
            except Exception:
                pass
        if hasattr(self, "network_thread") and self.network_thread is not None:
            try:
                if self.network_thread.isRunning():
                    self.network_thread.quit()
                    self.network_thread.wait(2000)
            except RuntimeError:
                pass
        event.accept()

if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
