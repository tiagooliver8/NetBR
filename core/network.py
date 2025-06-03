# core/network.py
import subprocess
import platform

def ping_host(host: str) -> bool:
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", host]
    try:
        subprocess.check_output(command)
        return True
    except subprocess.CalledProcessError:
        return False
