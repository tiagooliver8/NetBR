from PySide6.QtCore import QObject, Signal
from .network import NetworkTest
from .speedtest import SpeedTest

class NetworkWorker(QObject):
    finished = Signal()
    progress = Signal(str)
    result = Signal(dict)

    def __init__(self):
        super().__init__()
        self.network = NetworkTest()
        self.speedtest = SpeedTest()

    def run_tests(self):
        try:
            # Emit progress for network test
            self.progress.emit("Iniciando testes de conectividade...")
            network_results = self.network.test_all()
            
            # Emit progress for speed test
            self.progress.emit("Iniciando teste de velocidade...")
            speed_results = self.speedtest.run_test()
            
            # Combine results
            results = {
                "network": network_results,
                "speed": speed_results
            }
            self.result.emit(results)
            
        except Exception as e:
            self.progress.emit(f"Erro: {str(e)}")
        finally:
            self.finished.emit()