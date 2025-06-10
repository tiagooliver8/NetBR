# nuvem/speedtest.py
import speedtest
from typing import Dict
import time
import statistics
import multiprocessing

class SpeedTest:
    def __init__(self):
        
        self.st = speedtest.Speedtest()

    def _run_test_worker(self, queue):
        try:
            self.st.get_best_server()
            download = self.st.download() / 1_000_000
            upload = self.st.upload() / 1_000_000
            ping = self.st.results.ping
            jitter_samples = []
            for _ in range(10):
                t1 = time.perf_counter()
                self.st.get_best_server()
                self.st.results.ping
                t2 = time.perf_counter()
                jitter_samples.append((t2 - t1) * 1000)
                time.sleep(0.1)
            jitter = statistics.stdev(jitter_samples) if len(jitter_samples) > 1 else 0.0
            queue.put({
                "download": round(download, 2),
                "upload": round(upload, 2),
                "ping": round(ping, 2),
                "jitter": round(jitter, 2),
                "status": "success"
            })
        except Exception as e:
            queue.put({
                "download": 0.0,
                "upload": 0.0,
                "ping": 0.0,
                "jitter": 0.0,
                "status": "failed",
                "error": str(e)
            })

    def run_test(self, timeout: int = 40) -> dict:
        queue = multiprocessing.Queue()
        p = multiprocessing.Process(target=self._run_test_worker, args=(queue,))
        p.start()
        p.join(timeout)
        if p.is_alive():
            p.terminate()
            p.join()
            return {
                "download": 0.0,
                "upload": 0.0,
                "ping": 0.0,
                "jitter": 0.0,
                "status": "timeout",
                "error": "Speedtest excedeu o tempo limite"
            }
        if not queue.empty():
            return queue.get()
        return {
            "download": 0.0,
            "upload": 0.0,
            "ping": 0.0,
            "jitter": 0.0,
            "status": "failed",
            "error": "Speedtest falhou sem resultado"
        }
