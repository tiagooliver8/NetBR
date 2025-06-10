from PySide6.QtCore import QObject, Signal
from nuvem.speedtest import SpeedTest
from nuvem.config_loader import load_config
from nuvem.logger import log
from nuvem.network import test_connection

class SpeedTestWorker(QObject):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, timeout=40):
        super().__init__()
        self.timeout = timeout

    def run(self):
        try:
            # Garante que o timeout seja inteiro (ThreadPoolExecutor exige int)
            timeout = int(self.timeout) if self.timeout else 40
            speedtest_instance = SpeedTest()
            result = speedtest_instance.run_test(timeout=timeout)  # type: ignore
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class NetworkWorker(QObject):
    finished = Signal(list)
    progress = Signal(str)
    result = Signal(list)

    def run_tests(self):
        self.progress.emit("Executando testes de conexão...")
        testes = load_config()
        resultados = []

        for teste in testes:
            host = teste["host"]
            port = teste["port"]
            required = teste["required"]

            # Progresso individual
            self.progress.emit(f"Testando {host}:{port}...")

            conectado = test_connection(host, port)
            status = "OK" if conectado else "FALHA"
            resultado = f"{host}:{port} - {status}"
            log(resultado)

            if not conectado and required:
                resultados.append(f"FALHA CRÍTICA: {host}:{port}")
            elif not conectado:
                resultados.append(f"ALERTA: {host}:{port} falhou")

        self.result.emit(resultados)
        self.finished.emit(resultados)
