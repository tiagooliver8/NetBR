# nuvem_test/__init__.py
from .network import ping_host
# from .speedtest import medir_velocidade
from .config_loader import load_config
# from .logger import setup_logger
from .network import test_connection
from nuvem_test.speedtest_worker import SpeedTest
from .logger import log