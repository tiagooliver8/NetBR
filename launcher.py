import sys
import os
import shutil
import subprocess
import datetime
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QMessageBox, QStackedLayout
from PySide6.QtGui import QPixmap, QFont, QIcon
from PySide6.QtCore import Qt, QTimer
import ctypes
import ctypes.wintypes
user32 = ctypes.windll.user32
EnumWindows = user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
IsWindowVisible = user32.IsWindowVisible
SetForegroundWindow = user32.SetForegroundWindow
GetWindowTextW = user32.GetWindowTextW
GetWindowTextLengthW = user32.GetWindowTextLengthW


# Utilitário para obter caminho de recursos (compatível com PyInstaller)
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base_path, relative_path)

# Criação de diretórios e cópia do conf.json
user_dir = os.path.expandvars(r"%userprofile%/.nuvem")
logs_dir = os.path.join(user_dir, "logs")
conf_dst = os.path.join(user_dir, "conf.json")
conf_src = resource_path("config/conf.json")
try:
    if not os.path.exists(user_dir):
        os.makedirs(user_dir, exist_ok=True)
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir, exist_ok=True)
    if not os.path.exists(conf_dst):
        shutil.copyfile(conf_src, conf_dst)
except Exception as e:
    QMessageBox.critical(None, "Erro", f"Não foi possível preparar ambiente: {e}")
    sys.exit(1)

# SplashScreen Widget
class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowIcon(QIcon(resource_path("resources/cloud.ico")))

        # Imagem de fundo
        pixmap = QPixmap(resource_path("resources/splash.png"))
        self.splash_label = QLabel(self)
        self.splash_label.setPixmap(pixmap)
        self.splash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.splash_label.setGeometry(0, 0, pixmap.width(), pixmap.height())

        # Label sobreposta
        self.text_label = QLabel("carregando ...", self)
        self.text_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.text_label.setStyleSheet("color: #17607a; background: transparent;")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setGeometry(0, 0, pixmap.width(), pixmap.height())

        self.resize(pixmap.width(), pixmap.height())
        self.center()
    def center(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2
        )

def find_executable():
    exe_name = "Nuvem.Test.exe"
    user_dir = os.path.join(os.path.expandvars(r"%userprofile%"), "Nuvem.Test")
    user_app = os.path.join(user_dir, exe_name)
    cwd_app = os.path.join(os.getcwd(), exe_name)
    if os.path.exists(user_app):
        return user_app, [user_app, cwd_app]
    if os.path.exists(cwd_app):
        return cwd_app, [user_app, cwd_app]
    return None, [user_app, cwd_app]


# Função para detectar e trazer a janela do Nuvem.Test para frente por título
def bring_nuvem_to_front_by_title(titles):
    hwnd_found = None
    def callback(hwnd, lParam):
        nonlocal hwnd_found
        if not IsWindowVisible(hwnd):
            return True
        length = GetWindowTextLengthW(hwnd)
        if length == 0:
            return True
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowTextW(hwnd, buff, length + 1)
        win_title = buff.value
        for t in titles:
            if t in win_title or win_title.startswith(t):
                hwnd_found = hwnd
                return False
        return True
    EnumWindows(EnumWindowsProc(callback), 0)
    if hwnd_found:
        SetForegroundWindow(hwnd_found)
        return hwnd_found
    return None

# Verifica se a janela está visível, não minimizada e com área suficiente
def is_window_ready(hwnd):
    if not hwnd:
        return False
    if not IsWindowVisible(hwnd):
        return False
    is_iconic = user32.IsIconic(hwnd)
    if is_iconic:
        return False
    rect = ctypes.wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return False
    width = rect.right - rect.left
    height = rect.bottom - rect.top
    if width < 100 or height < 100:
        return False
    return True

def main():
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    app.processEvents()
    exe_path, checked_paths = find_executable()
    if not exe_path:
        splash.close()
        msg = ("Nuvem.Test.exe não encontrado.\n" +
               "Caminhos verificados:\n" +
               f"- {checked_paths[0]}\n- {checked_paths[1]}")
        QMessageBox.critical(None, "Erro", msg)
        sys.exit(1)
    subprocess.Popen([exe_path], shell=False)
    QTimer.singleShot(20000, app.quit)  # Fecha após 15 segundos
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
