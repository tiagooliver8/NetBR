# nuvem/speedtest.py
import speedtest
from typing import Dict

class SpeedTest:
    def __init__(self):
        self.st = speedtest.Speedtest()

    def run_test(self) -> dict:
        try:
            # Get best server
            self.st.get_best_server()
            
            # Test download speed
            download = self.st.download() / 1_000_000  # Convert to Mbps
            
            # Test upload speed
            upload = self.st.upload() / 1_000_000  # Convert to Mbps
            
            # Get ping (must use self.st.results.ping after upload)
            ping = self.st.results.ping
            
            return {
                "download": round(download, 2),
                "upload": round(upload, 2),
                "ping": round(ping, 2),
                "status": "success"
            }
        except Exception as e:
            return {
                "download": 0.0,
                "upload": 0.0,
                "ping": 0.0,
                "status": "failed",
                "error": str(e)
            }
