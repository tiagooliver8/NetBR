# nuvem/network.py
import socket
import subprocess
import platform

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
