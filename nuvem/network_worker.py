from PySide6.QtCore import QObject, Signal
from nuvem.speedtest import SpeedTest

class SpeedTestWorker(QObject):
    finished = Signal(dict)
    error = Signal(str)

    def run(self):
        try:
            result = SpeedTest().run_test()
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))