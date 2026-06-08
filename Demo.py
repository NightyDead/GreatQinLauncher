import sys
import os
import winreg
import subprocess
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                               QVBoxLayout, QWidget, QMessageBox, QLabel)
from PySide6.QtCore import Qt

def find_game_path_by_registry(game_name="原神"):
    """
    通过 Windows 注册表寻找游戏安装路径
    注意：不同服（官服/B服/国际服）的注册表键名可能不同
    """
    # 64位系统下，32位和64位程序的常见注册表节点
    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    for path in registry_paths:
        try:
            # 尝试打开对应游戏的注册表项
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, rf"{path}\{game_name}")
            # 读取安装目录
            install_location, _ = winreg.QueryValueEx(key, "InstallLocation")
            winreg.CloseKey(key)

            # 拼接具体的可执行文件路径（以原神国服为例）
            exe_path = os.path.join(install_location, "Genshin Impact Game", "YuanShen.exe")
            
            if os.path.exists(exe_path):
                return exe_path
        except FileNotFoundError:
            continue
            
    return None

class MinimalLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Launcher MVP")
        self.resize(300, 150)

        # UI 布局
        layout = QVBoxLayout()
        
        self.info_label = QLabel("正在检索游戏路径...")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)

        self.btn_launch = QPushButton("启动 原神")
        self.btn_launch.setMinimumHeight(40)
        self.btn_launch.setEnabled(False) # 默认禁用，找到路径再启用
        self.btn_launch.clicked.connect(self.launch_game)
        layout.addWidget(self.btn_launch)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 初始化时执行检索
        self.game_exe_path = find_game_path_by_registry("原神")
        self.update_ui_state()

    def update_ui_state(self):
        if self.game_exe_path:
            self.info_label.setText("已就绪")
            self.info_label.setStyleSheet("color: green;")
            self.btn_launch.setEnabled(True)
        else:
            self.info_label.setText("未能在注册表找到游戏\n请检查是否安装或尝试手动绑定")
            self.info_label.setStyleSheet("color: red;")

    def launch_game(self):
        if not self.game_exe_path:
            return
            
        try:
            # 关键：cwd 参数必须设置，否则游戏找不到自身的 _Data 文件夹
            game_dir = os.path.dirname(self.game_exe_path)
            subprocess.Popen([self.game_exe_path], cwd=game_dir)
            
            # 启动游戏后通常将启动器最小化
            self.showMinimized()
        except Exception as e:
            QMessageBox.critical(self, "启动失败", f"无法启动游戏：{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MinimalLauncher()
    window.show()
    sys.exit(app.exec())