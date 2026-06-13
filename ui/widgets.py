# -*- coding: utf-8 -*-
"""
FH6 AutoScript - 自定义 Widget 组件
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
)
from PyQt6.QtCore import Qt


class SectionLabel(QLabel):
    """分区标题标签"""
    def __init__(self, text: str, color: str):
        super().__init__(text)
        self.setObjectName("section")
        self.setStyleSheet(f"color: {color}; background: transparent;")


class HintLabel(QLabel):
    """提示信息标签"""
    def __init__(self, text: str):
        super().__init__(text)
        self.setObjectName("hint")


class KeyLabel(QLabel):
    """键值标签（固定宽度）"""
    def __init__(self, text: str, color: str = "#5A5A70"):
        super().__init__(text)
        self.setObjectName("label")
        self.setStyleSheet(f"color: {color}; background: transparent;")
        self.setFixedWidth(50)


class ValueLabel(QLabel):
    """动态值标签"""
    def __init__(self, text: str, color: str = "#FFFFFF"):
        super().__init__(text)
        self.setObjectName("value")
        self.setStyleSheet(f"color: {color}; background: transparent;")

    def set_color(self, color: str):
        self.setStyleSheet(f"color: {color}; background: transparent;")

    def set(self, text: str, color: str = None):
        self.setText(text)
        if color:
            self.set_color(color)


class Separator(QFrame):
    """分隔线"""
    def __init__(self):
        super().__init__()
        self.setObjectName("sep")
        self.setFixedHeight(1)


class CardFrame(QFrame):
    """卡片容器"""
    def __init__(self):
        super().__init__()
        self.setObjectName("card")


class CardLayout(QVBoxLayout):
    """卡片布局"""
    def __init__(self):
        super().__init__()
        self.setContentsMargins(10, 5, 10, 5)
        self.setSpacing(3)


class RowLayout(QHBoxLayout):
    """行布局"""
    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(5)


class NumericEntry(QLineEdit):
    """数字输入框"""
    def __init__(self, default: str = "1"):
        super().__init__()
        self.setText(default)
        self.setFixedWidth(80)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class SmallButton(QPushButton):
    """小按钮"""
    def __init__(self, text: str):
        super().__init__(text)
        self.setFixedHeight(24)


class ToggleButton(QPushButton):
    """开始/停止切换按钮，扁长风格，颜色跟随功能模块"""

    # 颜色预设: (文字色, 背景色, 边框色, hover背景色, hover边框色)
    _COLORS = {
        "green":  ("#38E090", "#1A2A20", "#2A4A35", "#204028", "#38E090"),
        "orange": ("#FF8800", "#2A1A10", "#4A3020", "#352418", "#FF8800"),
        "purple": ("#B44CFF", "#1C1028", "#382050", "#281838", "#B44CFF"),
        "blue":   ("#00CFFF", "#102028", "#203848", "#182838", "#00CFFF"),
        "gold":   ("#F9E2AF", "#282010", "#403820", "#302818", "#F9E2AF"),
    }

    def __init__(self, color: str = "green"):
        super().__init__("开始")
        self._color = color
        self.setFixedSize(108, 40)
        self._apply_idle()

    def _apply_idle(self):
        c = self._COLORS.get(self._color)
        if c is None:
            c = self._COLORS["green"]
        text, bg, border, hover_bg, hover_border = c
        self.setText("开始")
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {text};
                border: 1px solid {border};
                border-radius: 5px;
                font-size: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
            }}
            QPushButton:pressed {{
                background-color: {bg};
            }}
        """)

    def _apply_running(self):
        self.setText("停止")
        self.setStyleSheet("""
            QPushButton {
                background-color: #2A1515;
                color: #FF4444;
                border: 1px solid #4A2525;
                border-radius: 5px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #351A1A;
            }
            QPushButton:pressed {
                background-color: #1A1010;
            }
        """)

    def set_running(self, running: bool):
        if running:
            self._apply_running()
        else:
            self._apply_idle()