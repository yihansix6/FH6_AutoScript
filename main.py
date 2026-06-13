# -*- coding: utf-8 -*-
"""
FH6 AutoScript

项目结构:
    rebuild/
    ├── main.py              # 程序入口
    ├── requirements.txt     # 依赖清单
    ├── images/              # 图片资源
    ├── assets/              # 其他静态资源
    ├── core/                # 核心模块
    │   ├── config.py        # 配置参数
    │   ├── game_utils.py    # 窗口查找、后台发键、cv2识图
    │   └── signals.py       # 线程安全信号
    ├── modules/             # 功能模块
    │   ├── buy_car.py       # 买车和加点 (Ctrl+F1)
    │   ├── delete_car.py    # 删车 (Ctrl+F2)
    │   ├── award.py         # 抽奖 (Ctrl+F3)
    │   ├── mastery.py       # 熟练度循环 (Ctrl+F4)
    │   └── auto_cycle.py    # 自动大循环 (Ctrl+F5)
    └── ui/                  # 界面模块
        ├── main_window.py   # 主窗口
        ├── styles.py        # QSS 样式表
        └── widgets.py       # 自定义组件

使用方式:
    pip install -r requirements.txt
    python main.py
"""

import sys
import os
import ctypes
import traceback
import keyboard
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
import core.config as cfg
from ui.main_window import AppGUI


def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """以管理员权限重新启动程序"""
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{__file__}"', None, 1
    )
    sys.exit(0)


def main():
    # 设置工作目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Windows: 设置独立 AppUserModelID，让任务栏显示自定义图标而非 Python 默认图标
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ForzaHorizon.6.AutoScript")

    # 高 DPI 支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)

    # # 如果不是管理员权限，自动提权重启
    if not is_admin():
        run_as_admin()

    try:
        # 创建 GUI
        window = AppGUI()
        window.show()

        # 注册全局热键（通过信号转到主线程，避免跨线程操作 UI 导致崩溃）
        keyboard.add_hotkey(cfg.HOT_BUYCAR,   window._signals.hotkey_buy_car.emit,    suppress=False)
        keyboard.add_hotkey(cfg.HOT_DELCAR,   window._signals.hotkey_delete_car.emit, suppress=False)
        keyboard.add_hotkey(cfg.HOT_GETAWARD, window._signals.hotkey_award.emit,      suppress=False)
        keyboard.add_hotkey(cfg.HOT_MASTERY,  window._signals.hotkey_mastery.emit,    suppress=False)
        keyboard.add_hotkey(cfg.HOT_AUTO,     window._signals.hotkey_auto.emit,       suppress=False)

        exit_code = app.exec()
    except Exception as e:
        QMessageBox.critical(
            None, "程序错误",
            f"程序运行时发生错误:\n\n{str(e)}\n\n{traceback.format_exc()}"
        )
        exit_code = 1
    finally:
        try:
            keyboard.unhook_all()
        except:
            pass

    sys.exit(exit_code)


if __name__ == "__main__":
    main()