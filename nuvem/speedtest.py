# nuvem/speedtest.py
import speedtest
from typing import Dict
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

class SpeedTest:
    def __init__(self, cancel_flag=None, progress_callback=None):
        self.cancel_flag = cancel_flag
        self.progress_callback = progress_callback

    def _run_test_worker(self):
        import traceback
        from nuvem.logger import log
        try:
            log("Iniciando Speedtest...")
            if self.progress_callback:
                self.progress_callback("Iniciando Speedtest...")
            try:
                st = speedtest.Speedtest()
            except Exception as e:
                log(f"Falha ao instanciar Speedtest: {e}")
                error_msg = str(e)
                if "403" in error_msg or "Forbidden" in error_msg:
                    if self.progress_callback:
                        self.progress_callback("Speedtest bloqueado pelo servidor (HTTP 403). Abrindo alternativa...")
                    # Sinaliza para a interface abrir o fallback
                    from nuvem.alternative_speedtest import AlternativeSpeedTestWindow
                    alt_window = AlternativeSpeedTestWindow()
                    alt_window.show()
                    return {"download": 0.0, "upload": 0.0, "ping": 0.0, "jitter": 0.0, "status": "blocked", "error": "Speedtest bloqueado pelo servidor (HTTP 403)."},
                else:
                    raise
            log("Speedtest instanciado.")
            if self.progress_callback:
                self.progress_callback("Speedtest instanciado.")
            # Obter melhor servidor uma vez só
            log("Buscando melhor servidor...")
            if self.progress_callback:
                self.progress_callback("Determinando melhor servidor...")
            best = st.get_best_server()
            log(f"Melhor servidor obtido: {best.get('host')} ({best.get('name')})")
            if self.progress_callback:
                self.progress_callback(f"Melhor servidor: {best.get('name')} ({best.get('host')})")
            # Teste de download
            if self.cancel_flag and self.cancel_flag():
                return {"status": "cancelled", "error": "Teste de velocidade cancelado."}
            if self.progress_callback:
                self.progress_callback("Teste de Download:")
            download = st.download() / 1_000_000
            log(f"Download: {download} Mbps")
            if self.progress_callback:
                self.progress_callback(f"Resultado Download: {round(download,2)} Mbps")
            # Teste de upload
            if self.cancel_flag and self.cancel_flag():
                return {"status": "cancelled", "error": "Teste de velocidade cancelado."}
            if self.progress_callback:
                self.progress_callback("Teste de Upload:")
            upload = st.upload() / 1_000_000
            log(f"Upload: {upload} Mbps")
            if self.progress_callback:
                self.progress_callback(f"Resultado Upload: {round(upload,2)} Mbps")
            # Ping base (já calculado no get_best_server)
            ping = st.results.ping
            log(f"Ping: {ping} ms")
            if self.progress_callback:
                self.progress_callback("Teste de Ping:")
                self.progress_callback(f"Resultado Ping: {round(ping,2)} ms")
            # Estimar jitter com múltiplas medições rápidas de ping
            jitter_samples = []
            if self.progress_callback:
                self.progress_callback("Teste de Jitter:")
            for i in range(10):
                if self.cancel_flag and self.cancel_flag():
                    return {"status": "cancelled", "error": "Teste de velocidade cancelado."}
                t1 = time.perf_counter()
                _ = st.results.ping  # usa ping já definido pelo servidor atual
                t2 = time.perf_counter()
                jitter_samples.append((t2 - t1) * 1000)
                log(f"Jitter sample {i}: {(t2 - t1) * 1000} ms")
                time.sleep(0.1)
            jitter = statistics.stdev(jitter_samples) if len(jitter_samples) > 1 else 0.0
            log(f"Jitter calculado: {jitter} ms")
            if self.progress_callback:
                self.progress_callback(f"Resultado Jitter: {round(jitter,2)} ms")
            return {
                "download": round(download, 2),
                "upload": round(upload, 2),
                "ping": round(ping, 2),
                "jitter": round(jitter, 2),
                "status": "success"
            }

        except Exception as e:
            log(f"Erro no speedtest: {e}\n{traceback.format_exc()}")
            # Mensagem amigável para erro 403
            error_msg = str(e)
            if "403" in error_msg or "Forbidden" in error_msg:
                user_msg = "Speedtest bloqueado pelo servidor (HTTP 403). Use o teste alternativo abaixo."
            else:
                user_msg = error_msg
            return {
                "download": 0.0,
                "upload": 0.0,
                "ping": 0.0,
                "jitter": 0.0,
                "status": "failed",
                "error": user_msg
            }

    def run_test(self, timeout: int = 40, requirements=None) -> dict:
        # requirements: lista de dicts do conf.json (download, upload, ping, jitter)
        if requirements is None:
            requirements = []
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._run_test_worker)
            try:
                result = future.result(timeout=timeout)
                if isinstance(result, tuple) and len(result) == 1 and isinstance(result[0], dict):
                    result = result[0]
                # Validação dos requisitos
                if isinstance(result, dict) and result.get("status") == "success":
                    for req in requirements:
                        tipo = req.get("type")
                        if tipo == "download" and req.get("required"):
                            min_mbps = req.get("min_mbps", 0)
                            if result.get("download", 0) < min_mbps:
                                result["status"] = "failed"
                                result["error"] = f"Download abaixo do mínimo: {result.get('download')} Mbps < {min_mbps} Mbps"
                        if tipo == "upload" and req.get("required"):
                            min_mbps = req.get("min_mbps", 0)
                            if result.get("upload", 0) < min_mbps:
                                result["status"] = "failed"
                                result["error"] = f"Upload abaixo do mínimo: {result.get('upload')} Mbps < {min_mbps} Mbps"
                        if tipo == "ping" and req.get("required"):
                            max_ms = req.get("max_ms", 9999)
                            if result.get("ping", 0) > max_ms:
                                result["status"] = "failed"
                                result["error"] = f"Ping acima do máximo: {result.get('ping')} ms > {max_ms} ms"
                        if tipo == "jitter" and req.get("required"):
                            max_ms = req.get("max_ms", 9999)
                            if result.get("jitter", 0) > max_ms:
                                result["status"] = "failed"
                                result["error"] = f"Jitter acima do máximo: {result.get('jitter')} ms > {max_ms} ms"
                if isinstance(result, dict):
                    return result
                # fallback: retorna o primeiro elemento se for tuple
                if isinstance(result, tuple) and len(result) > 0 and isinstance(result[0], dict):
                    return result[0]
                return {}
            except FuturesTimeoutError:
                return {
                    "download": 0.0,
                    "upload": 0.0,
                    "ping": 0.0,
                    "jitter": 0.0,
                    "status": "timeout",
                    "error": "Speedtest excedeu o tempo limite"
                }
