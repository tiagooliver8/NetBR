from PySide6.QtCore import QObject, Signal
from nuvem_test.speedtest_worker import SpeedTest
from nuvem_test.config_loader import load_config, get_speedtest_requirements
from nuvem_test.logger import log
from nuvem_test.network import test_connection

class SpeedTestWorker(QObject):
    finished = Signal(dict)
    error = Signal(str)
    progress = Signal(str)  # Adiciona sinal de progresso

    def __init__(self, timeout=40):
        super().__init__()
        self.timeout = timeout
        self.requirements = get_speedtest_requirements()
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            if self._cancelled:
                self.finished.emit({
                    "status": "cancelled",
                    "error": "Teste de velocidade cancelado pelo usuário."
                })
                return
            # Garante que o timeout seja inteiro (ThreadPoolExecutor exige int)
            timeout = int(self.timeout) if self.timeout else 40
            speedtest_instance = SpeedTest(cancel_flag=lambda: self._cancelled, progress_callback=self.progress.emit)
            result = speedtest_instance.run_test(timeout=timeout, requirements=self.requirements)  # type: ignore
            if self._cancelled:
                result["status"] = "cancelled"
                result["error"] = "Teste de velocidade cancelado pelo usuário."
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class NetworkWorker(QObject):
    finished = Signal(list)
    progress = Signal(str)
    result = Signal(list)

    def __init__(self):
        super().__init__()
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run_tests(self):
        self.progress.emit("Executando testes de conexão...")
        config = load_config()
        testes = config["tests"] if isinstance(config, dict) and "tests" in config else config
        resultados = []

        for teste in testes:
            if not isinstance(teste, dict):
                continue  # ignora entradas inválidas
            if self._cancelled:
                self.progress.emit("Testes de conexão cancelados.")
                break
            host = teste["host"]
            port = teste["port"]
            required = teste["required"]
            description = teste.get("description", f"{host}:{port}")

            # Progresso individual com descrição
            self.progress.emit(f"Testando {description}...")

            conectado = test_connection(host, port)
            status = "OK" if conectado else "FALHA"
            resultado = f"{description} - {status}"
            self.progress.emit(resultado)  # Mostra resultado na interface
            log(f"{description} ({host}:{port}) - {status}")

            if not conectado and required:
                resultados.append(f"FALHA CRÍTICA: {description}")
            elif not conectado:
                resultados.append(f"ALERTA: {description} falhou")

        self.result.emit(resultados)
        self.finished.emit(resultados)
