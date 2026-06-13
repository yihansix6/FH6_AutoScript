# -*- coding: utf-8 -*-
"""
FH6 AutoScript - UI 样式表
现代化深色主题 QSS
"""

# 全局样式
GLOBAL_QSS = """
/* ── 全局 ── */
QWidget {
    background-color: #0C0C18;
    color: #C8C8D0;
    font-family: "Segoe UI", "Microsoft YaHei", "Consolas", sans-serif;
    font-size: 13px;
}

/* ── 标签 ── */
QLabel#title {
    font-size: 16px;
    font-weight: bold;
    color: #FFFFFF;
    padding: 6px 0px;
    background: transparent;
}
QLabel#section {
    font-size: 12px;
    font-weight: bold;
    padding: 3px 0px;
    background: transparent;
}
QLabel#hint {
    font-size: 11px;
    color: #6A6A80;
    padding: 1px 0px;
    background: transparent;
}
QLabel#hint_key {
    font-size: 11px;
    color: #7A7A90;
    padding: 1px 0px;
    background: transparent;
}
QLabel#label {
    font-size: 11px;
    color: #5A5A70;
    background: transparent;
}
QLabel#value {
    font-size: 11px;
    background: transparent;
}

/* ── 输入框 ── */
QLineEdit {
    background-color: #12121F;
    color: #D0D0D8;
    border: 1px solid #2A2A40;
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 11px;
    max-height: 24px;
    selection-background-color: #3A5AFF;
}
QLineEdit:focus {
    border: 1px solid #4A6AFF;
    background-color: #141422;
}
QLineEdit:disabled {
    background-color: #10101A;
    color: #404055;
    border: 1px solid #1A1A2A;
}

/* ── 文本框 ── */
QTextEdit {
    background-color: #0E0E1A;
    color: #38E090;
    border: 1px solid #1A1A30;
    border-radius: 5px;
    font-size: 12px;
    padding: 6px;
    selection-background-color: #1A3A2A;
}

/* ── 按钮 ── */
QPushButton {
    background-color: #181828;
    color: #808090;
    border: 1px solid #282840;
    border-radius: 5px;
    padding: 4px 12px;
    font-size: 11px;
    min-height: 24px;
}
QPushButton:hover {
    background-color: #242440;
    color: #C0C0D0;
    border: 1px solid #4A6AFF;
}
QPushButton:pressed {
    background-color: #1A1A35;
    color: #FFFFFF;
}

/* ── 单选框 ── */
QRadioButton {
    color: #A0A0B0;
    font-size: 11px;
    spacing: 4px;
    background: transparent;
}
QRadioButton::indicator {
    width: 14px;
    height: 14px;
    border-radius: 7px;
    border: 1px solid #3A3A55;
    background-color: #12121F;
}
QRadioButton::indicator:checked {
    background-color: #4A6AFF;
    border: 1px solid #4A6AFF;
}
QRadioButton::indicator:hover {
    border: 1px solid #5A5A75;
}

/* ── 水平分隔线 ── */
QFrame#sep {
    background-color: #181828;
    max-height: 1px;
    margin: 5px 0px;
}

/* ── 垂直分隔线 ── */
QFrame#vsep {
    background-color: #181828;
    max-width: 1px;
    margin: 0px 6px;
}

/* ── 卡片容器 ── */
QFrame#card {
    background-color: #0E0E1C;
    border: 1px solid #181830;
    border-radius: 7px;
    padding: 8px;
    margin: 2px 0px;
}

/* ── 滚动条 ── */
QScrollBar:vertical {
    background: #0A0A14;
    width: 6px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #2A2A45;
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: #3A3A55;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}
"""

# 状态颜色
STATUS_COLORS = {
    "idle":      "#6A6A80",
    "running":   "#38E090",
    "stopped":   "#888888",
    "warning":   "#FF8866",
    "accent":    "#FFA940",
    "cyan":      "#38C0E0",
    "yellow":    "#FFD700",
    "white":     "#FFFFFF",
    "gray":      "#888888",
    "red":       "#FF4444",
    "green":     "#00FF88",
    "gold":      "#F9E2AF",
    "orange":    "#FF8800",
    "blue":      "#00CFFF",
    "purple":    "#B44CFF",
    "muted":     "#444455",
    "dark":      "#666677",
}