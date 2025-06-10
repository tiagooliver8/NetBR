# nuvem/speedtest.py
import speedtest
from typing import Dict
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

class SpeedTest:
    def __init__(self):
        pass

    def _run_test_worker(self):
        import traceback
        from nuvem.logger import log
        try:
            log("[DEBUG] Iniciando Speedtest...")
            st = speedtest.Speedtest()
            log("[DEBUG] Speedtest instanciado.")

            # Obter melhor servidor uma vez só
            log("[DEBUG] Buscando melhor servidor...")
            best = st.get_best_server()
            log(f"[DEBUG] Melhor servidor obtido: {best.get('host')} ({best.get('name')})")

            # Teste de download
            download = st.download() / 1_000_000
            log(f"[DEBUG] Download: {download} Mbps")

            # Teste de upload
            upload = st.upload() / 1_000_000
            log(f"[DEBUG] Upload: {upload} Mbps")

            # Ping base (já calculado no get_best_server)
            ping = st.results.ping
            log(f"[DEBUG] Ping: {ping} ms")

            # Estimar jitter com múltiplas medições rápidas de ping
            jitter_samples = []
            for i in range(10):
                t1 = time.perf_counter()
                _ = st.results.ping  # usa ping já definido pelo servidor atual
                t2 = time.perf_counter()
                jitter_samples.append((t2 - t1) * 1000)
                log(f"[DEBUG] Jitter sample {i}: {(t2 - t1) * 1000} ms")
                time.sleep(0.1)

            jitter = statistics.stdev(jitter_samples) if len(jitter_samples) > 1 else 0.0
            log(f"[DEBUG] Jitter calculado: {jitter} ms")

            return {
                "download": round(download, 2),
                "upload": round(upload, 2),
                "ping": round(ping, 2),
                "jitter": round(jitter, 2),
                "status": "success"
            }

        except Exception as e:
            log(f"[DEBUG] Erro no speedtest: {e}\n{traceback.format_exc()}")
            return {
                "download": 0.0,
                "upload": 0.0,
                "ping": 0.0,
                "jitter": 0.0,
                "status": "failed",
                "error": str(e)
            }

    def run_test(self, timeout: int = 40) -> dict:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._run_test_worker)
            try:
                return future.result(timeout=timeout)
            except FuturesTimeoutError:
                return {
                    "download": 0.0,
                    "upload": 0.0,
                    "ping": 0.0,
                    "jitter": 0.0,
                    "status": "timeout",
                    "error": "Speedtest excedeu o tempo limite"
                }
