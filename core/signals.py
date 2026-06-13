# -*- coding: utf-8 -*-
"""
FH6 AutoScript - 线程安全信号模块
"""

from PyQt6.QtCore import QObject, pyqtSignal


class AppSignals(QObject):
    """集中管理所有跨线程信号"""

    # 日志信号
    log_signal = pyqtSignal(str)

    # 通用状态更新 (label_name, text, color)
    status_signal = pyqtSignal(str, str, str)

    # 完成弹窗 (title, message)
    completion_signal = pyqtSignal(str, str)

    # 热键触发信号（将 keyboard 回调从后台线程转到主线程）
    hotkey_buy_car = pyqtSignal()
    hotkey_delete_car = pyqtSignal()
    hotkey_award = pyqtSignal()
    hotkey_mastery = pyqtSignal()
    hotkey_auto = pyqtSignal()

    # 按钮运行状态信号（工作线程安全更新按钮状态）
    button_running_signal = pyqtSignal(str, bool)