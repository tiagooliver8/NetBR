import sys
if sys.stdout is None:
    import io
    sys.stdout = io.StringIO()
if sys.stderr is None:
    import io
    sys.stderr = io.StringIO()

# main.py
import os, json
import time
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QProgressBar, QSpacerItem, QSizePolicy, QScrollArea
from PySide6.QtCore import QThread, QTimer, Qt
from PySide6.QtGui import QPixmap, QFont, QIcon
from PySide6.QtCore import QSize
from ui_main import Ui_MainWindow
from nuvem_test.logger import log
from nuvem_test.network_worker import SpeedTestWorker, NetworkWorker
from nuvem_test.alternative_speedtest import AlternativeSpeedTestWindow

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base_path, relative_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(resource_path("resources/cloud.png")))
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Nuvem.Test - Mersen do Brasil")
        self.setFixedSize(400, 700)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #b3b3b3, stop:1 #888888);
                border-radius: 32px;
            }
        """)
        # Centraliza a janela na tela
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # Acesso direto aos widgets
        self.button = self.ui.button
        self.label = self.ui.label
        self.text_box = self.ui.text_box
        self.progress_bar = self.ui.progress_bar
        self.scroll_area = self.ui.scroll_area
        self.top_label = self.ui.top_label
        self.cloud_icon = self.ui.cloud_icon
        self.mersen_logo = self.ui.mersen_logo
        self.main_layout = self.ui.main_layout
        self.spacer_top = self.ui.spacer_top
        self.spacer_bottom = self.ui.spacer_bottom

        # Ajusta propriedades dos widgets
        try:
            self.cloud_icon.setPixmap(QPixmap(resource_path("resources/cloud.png")).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        except Exception:
            self.cloud_icon.setText("☁️")
            self.cloud_icon.setFont(QFont("Arial", 32))
        self.cloud_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Aplica cor PANTONE 1655C (hex #FF3C00) em 'Nuvem.' e mantém 'Test' branco
        self.top_label.setText('<span style="color:#FF3C00;">Nuvem.</span><span style="color:#FFFFFF;">Test</span>')
        self.top_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.top_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        try:
            self.mersen_logo.setPixmap(QPixmap(resource_path("resources/mersen.png")).scaled(180, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        except Exception:
            self.mersen_logo.setText("MERSEN")
            self.mersen_logo.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.mersen_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.label.setStyleSheet("color: #222; font-size: 18px;")
        self.label.hide()
        self.text_box.hide()
        self.text_box.setMinimumHeight(420)
        self.text_box.setMaximumHeight(420)
        # Retângulo de status
        
        self.label.setStyleSheet("color: white; font-size: 14px; font-family: Arial, sans-serif;")
        # Estiliza a barra de rolagem do QScrollArea
        self.scroll_area.setStyleSheet("""
            QScrollBar:vertical {
                background: #17607a;
                width: 16px;
                margin: 2px 2px 2px 2px;
                border-radius: 8px;
            }
            QScrollBar::handle:vertical {
                background: #22262a;
                min-height: 40px;
                border-radius: 8px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        # Função para rolar para o final
        def scroll_to_bottom():
            self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
        self._scroll_to_bottom = scroll_to_bottom  # Referência para uso posterior

        # Carrega o conf.json do diretório do usuário
        config_path = resource_path("config/conf.json")
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        # Ajusta layout do topo para imagem e texto centralizados na tela
        from PySide6.QtWidgets import QHBoxLayout, QSpacerItem, QSizePolicy
        # Remove widgets antigos do layout vertical
        try:
            self.ui.top_layout.removeWidget(self.cloud_icon)
        except Exception:
            pass
        try:
            self.ui.top_layout.removeWidget(self.top_label)
        except Exception:
            pass
        # Remove todos os itens do top_layout
        while self.ui.top_layout.count():
            item = self.ui.top_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        # Cria layout horizontal centralizado
        self.top_hbox = QHBoxLayout()
        self.top_hbox.setSpacing(12)
        self.top_hbox.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.top_hbox.addWidget(self.cloud_icon)
        self.top_hbox.addWidget(self.top_label)
        self.top_hbox.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.cloud_icon.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        self.top_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.ui.top_layout.addLayout(self.top_hbox)

        # Botão de reiniciar (inicialmente oculto)
        from PySide6.QtWidgets import QPushButton, QLabel
        self.restart_button = QPushButton()
        self.restart_button.setFixedSize(40, 40)
        self.restart_button.setToolTip("Reiniciar teste")
        self.restart_button.setStyleSheet("""
            QPushButton {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.7, fx:0.5, fy:0.5, stop:0 #e0e0e0, stop:1 #888888);
                border: 2px solid #22262a;
                border-radius: 20px;
                padding: 0px;
            }
            QPushButton:hover {
                background: #b3b3b3;
            }
        """)
        self.restart_button.setIcon(QIcon(resource_path("resources/restart.png")))
        self.restart_button.setIconSize(QSize(32, 32))
        self.restart_button.setVisible(False)
        self.restart_button.clicked.connect(self.reiniciar_testes)
        self.main_layout.replaceWidget(self.progress_bar, self.restart_button)
        self.main_layout.addWidget(self.progress_bar)  # Mantém a barra para manipulação, mas ela ficará oculta

        # Label de status ao lado do botão reiniciar
        self.status_label = QLabel("Teste concluído")
        self.status_label.setStyleSheet("color: #17607a; font-size: 16px; font-family: Arial, sans-serif;")
        self.status_label.setVisible(False)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        # Layout para barra de progresso + botão de reinício + status centralizado
        from PySide6.QtWidgets import QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QLabel
        self.progress_bar.setFixedHeight(24)
        self.progress_bar.setFixedWidth(0)  # width controlado pelo layout
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border-radius: 8px;
                background: #e0e0e0;
                height: 24px;
                font-size: 1px; /* Oculta percentual */
            }
            QProgressBar::chunk {
                background-color: #17607a;
                border-radius: 8px;
            }
        """)
        self.progress_restart_hbox = QHBoxLayout()
        self.progress_restart_hbox.setSpacing(8)
        self.progress_restart_hbox.addWidget(self.progress_bar, stretch=1)
        self.progress_restart_hbox.addWidget(self.restart_button)
        # Adiciona expansores para centralizar a label
        self.progress_restart_hbox.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.progress_restart_hbox.addWidget(self.status_label)
        self.progress_restart_hbox.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.main_layout.removeWidget(self.progress_bar)
        self.main_layout.removeWidget(self.restart_button)
        self.main_layout.addLayout(self.progress_restart_hbox)
        self.progress_bar.setVisible(True)
        self.restart_button.setVisible(False)
        self.status_label.setVisible(False)

        # Remove barra de progresso do layout
        self.progress_bar.setVisible(False)
        self.main_layout.removeWidget(self.progress_bar)
        # Remove restart_button do layout se já existir
        self.main_layout.removeWidget(self.restart_button)
        # Garante que o mersen_logo fique sempre no rodapé
        self.main_layout.removeWidget(self.mersen_logo)
        self.main_layout.addWidget(self.restart_button)
        self.main_layout.addWidget(self.mersen_logo, alignment=Qt.AlignmentFlag.AlignBottom)
        self.restart_button.setVisible(False)

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
        self._scroll_to_bottom()

    def update_results(self, results):
        # Adiciona os resultados ao texto existente, sem apagar
        for result in results:
            self.label.setText(self.label.text() + "\n    " + result)
        QApplication.processEvents()
        self._scroll_to_bottom()

    def on_network_finished(self, results):
        self.label.setText(self.label.text() + "\nIniciando teste de velocidade...")
        QApplication.processEvents()
        self._scroll_to_bottom()

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
        self._scroll_to_bottom()

    def on_speedtest_finished(self, result):
        # Se o fallback já foi aberto, ignore o resultado do speedtest
        if hasattr(self, "fallback_ativo") and self.fallback_ativo:
            log("[INFO] Resultado do speedtest ignorado pois o fallback já foi aberto.")
            return
        self.speedtest_timeout_timer.stop()
        self.last_speedtest_update = time.time()  # Marca o momento da última atualização
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(True)
        self.restart_button.setVisible(True)
        self.status_label.setVisible(True)
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
        self.restart_button.setVisible(True)
        self.status_label.setVisible(True)

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
            self.restart_button.setVisible(True)
        else:
            # Reagenda o timeout para o tempo restante
            restante = int(timeout_seconds - (now - self.last_speedtest_update))
            self.speedtest_timeout_timer.start(restante * 1000)

    def abrir_speedtest_alternativo(self):
        # Marca que o fallback foi acionado
        self.fallback_ativo = True
        # Cancela o teste de velocidade se estiver rodando
        if hasattr(self, "speedtest_worker"):
            try:
                self.speedtest_worker.cancel()
            except Exception:
                pass
        # Não espera a thread do speedtest terminar, apenas ignora o resultado
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
        # Abre a janela alternativa
        self.alt_window = AlternativeSpeedTestWindow()
        self.alt_window.show()
        self.label.setText(self.label.text() + "\nTestes cancelados/interrompidos.")
        self.restart_button.setVisible(True)

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

    def reiniciar_testes(self):
        # Fecha a janela alternativa se estiver aberta (mas não mexe em threads do speedtest)
        if hasattr(self, "alt_window"):
            try:
                if self.alt_window.isVisible():
                    self.alt_window.close()
                delattr(self, "alt_window")
            except Exception:
                pass
        # Limpa flag de fallback
        if hasattr(self, "fallback_ativo"):
            delattr(self, "fallback_ativo")
        # NÃO cancela nem espera threads de speedtest/network aqui!
        # Apenas limpa e restaura a interface
        self.label.clear()
        self.restart_button.setVisible(False)
        self.status_label.setVisible(False)
        self.button.setVisible(True)
        self.button.setEnabled(True)
        self.text_box.hide()
        self.label.hide()
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        # Remove spacers de status se existirem
        if hasattr(self, 'spacer_top_status'):
            self.main_layout.removeItem(self.spacer_top_status)
            delattr(self, 'spacer_top_status')
        if hasattr(self, 'spacer_bottom_status'):
            self.main_layout.removeItem(self.spacer_bottom_status)
            delattr(self, 'spacer_bottom_status')
        # Restaura os spacers originais
        self.main_layout.insertItem(1, self.spacer_top)
        self.main_layout.insertItem(3, self.spacer_bottom)
        # Garante que o botão está no layout correto
        self.main_layout.insertWidget(2, self.button)

if __name__ == "__main__":
    print("[DEBUG] Iniciando NetBR...")
    app = QApplication()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
