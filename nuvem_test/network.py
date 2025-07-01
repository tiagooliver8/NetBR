# nuvem_test/network.py
import socket
import subprocess
import platform
import ping3
from typing import Dict, List, Any

def ping_host(host: str) -> bool:
    """
    Testa conectividade básica com ping ICMP.
    """
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", host]
    try:
        subprocess.check_output(command)
        return True
    except subprocess.CalledProcessError:
        return False

def test_connection(host: str, port: int, timeout: float = 3.0) -> bool:
    """
    Testa se é possível estabelecer conexão TCP com o host e porta informados.
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, socket.error):
        return False

class NetworkTest:
    def __init__(self):
        self.targets = [
            "google.com",
            "cloudflare.com",
            "aws.amazon.com"
        ]

    def test_connection(self, host: str) -> Dict[str, Any]:
        try:
            # Test DNS resolution
            ip = socket.gethostbyname(host)
            
            # Test ping
            ping_time = ping3.ping(host)
            
            return {
                "host": host,
                "ip": ip,
                "ping": round(ping_time * 1000, 2) if ping_time is not None else None,
                "status": "success"
            }
        except Exception as e:
            return {
                "host": host,
                "status": "failed",
                "error": str(e)
            }

    def test_all(self) -> List[Dict[str, Any]]:
        results = []
        for target in self.targets:
            results.append(self.test_connection(target))
        return results
