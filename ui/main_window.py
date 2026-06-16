# -*- coding: utf-8 -*-
"""
FH6 AutoScript - 主窗口 (PyQt6 现代化界面)
"""

import time
import threading
import sys
import ctypes
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QMessageBox,
    QFrame, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QTextCursor, QIcon

import core.config as cfg
from core.game_utils import (
    find_game, gsend, set_log_callback
)
from core.signals import AppSignals
from ui.styles import GLOBAL_QSS, STATUS_COLORS as SC
from ui.widgets import (
    SectionLabel, HintLabel, KeyLabel, ValueLabel,
    Separator, CardLayout, RowLayout, NumericEntry, SmallButton, ToggleButton
)


class AppGUI(QWidget):
    """FH6 AutoScript 主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Forza Horizon 6 AutoScript")
        self.setFixedSize(680, 800)
        self.setStyleSheet(GLOBAL_QSS)

        # 设置窗口图标
        import os
        ico_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "FH6.ico")
        self.setWindowIcon(QIcon(ico_path))

        # ── 全局状态变量 ──
        self.bc_running = False
        self.bc_loop_count = 0
        self.bc_total = 0
        self.bc_start_time = 0

        self.dc_running = False
        self.dc_loop_count = 0
        self.dc_total = 0
        self.dc_start_time = 0

        self.aw_running = False
        self.aw_loop_count = 0
        self.aw_total = 0
        self.aw_start_time = 0

        self.b_running = False
        self.b_loop_count = 0
        self.b_total = 0
        self.b_start_time = 0

        self.auto_running = False
        self.auto_cycle = 0
        self.auto_mode = "contain"  # 默认：包括删车和抽奖

        # 线程引用
        self.bc_thread = None
        self.dc_thread = None
        self.aw_thread = None
        self.b_thread = None
        self.auto_thread = None

        # 开始/停止按钮
        self.btn_bc = None
        self.btn_dc = None
        self.btn_aw = None
        self.btn_b = None
        self.btn_auto = None

        # ── 信号系统 ──
        self._signals = AppSignals()
        self._signals.log_signal.connect(self._append_log)
        self._signals.status_signal.connect(self._apply_status)
        self._signals.completion_signal.connect(self._show_completion)
        self._signals.hotkey_buy_car.connect(self.toggle_buy_car)
        self._signals.hotkey_delete_car.connect(self.toggle_delete_car)
        self._signals.hotkey_award.connect(self.toggle_award)
        self._signals.hotkey_mastery.connect(self.toggle_mastery)
        self._signals.hotkey_auto.connect(self.toggle_auto)
        self._signals.button_running_signal.connect(self._on_button_running)

        # 标签引用存储
        self._labels = {}

        # ── 构建 UI ──
        self._build_ui()

        # ── 设置日志回调 ──
        set_log_callback(self._log)

        # ── 定时器 ──
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

        # 初始化窗口
        self._on_refresh()
        self._dark_title_applied = False

    # ══════════════════════════════════════════════════════════
    #  窗口事件
    # ══════════════════════════════════════════════════════════
    def showEvent(self, event):
        super().showEvent(event)
        if sys.platform == "win32" and not self._dark_title_applied:
            self._apply_dark_title_bar()
            self._dark_title_applied = True

    def _apply_dark_title_bar(self):
        """为 Windows 10/11 设置暗色标题栏，与 UI 深色主题保持一致"""
        try:
            hwnd = int(self.winId())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                ctypes.wintypes.HWND(hwnd),
                ctypes.wintypes.DWORD(DWMWA_USE_IMMERSIVE_DARK_MODE),
                ctypes.pointer(ctypes.wintypes.BOOL(True)),
                ctypes.sizeof(ctypes.wintypes.BOOL)
            )
        except Exception:
            pass

    # ══════════════════════════════════════════════════════════
    #  UI 构建
    # ══════════════════════════════════════════════════════════
    def _build_ui(self):
        outer_layout = QHBoxLayout(self)
        outer_layout.setContentsMargins(12, 10, 12, 10)
        outer_layout.setSpacing(0)

        # ── 左侧面板 ──
        left_panel = QVBoxLayout()
        left_panel.setContentsMargins(0, 0, 4, 0)
        left_panel.setSpacing(0)

        # ── 按键说明 ──
        left_panel.addWidget(SectionLabel("[ 按键说明 ]", SC["yellow"]))
        hints = [
            ("Ctrl+F1", "买车和加点","在【购买与出售】页面启动"),
            ("Ctrl+F2", "移除车辆","在【车辆】页面启动"),
            ("Ctrl+F3", "抽奖","在【我的地平线】页面启动"),
            ("Ctrl+F4", "熟练度循环","在【开始竞赛赛事】页面启动"),
            ("Ctrl+F5", "自动大循环","在【漫游模式】界面启动"),
        ]
        for key, name, desc in hints:
            row = RowLayout()
            key_lbl = QLabel(f"{key}\t\t{name}")
            key_lbl.setObjectName("hint_key")
            key_lbl.setFixedWidth(160)
            row.addWidget(key_lbl)
            desc_lbl = HintLabel(desc)
            row.addWidget(desc_lbl)
            row.addStretch()
            left_panel.addLayout(row)
        left_panel.addWidget(Separator())

        # ── 买车+加点 ──
        lay = CardLayout()
        bc_header = RowLayout()
        bc_header.addWidget(SectionLabel("[ 买车和加点  Ctrl+F1 ]", SC["green"]))
        bc_header.addStretch()
        self.btn_bc = ToggleButton("green")
        self.btn_bc.clicked.connect(self.toggle_buy_car)
        bc_header.addWidget(self.btn_bc)
        lay.addLayout(bc_header)
        lay.addLayout(self._row("状态:", self._val("bc_status", "■ 待机", SC["gray"])))
        lay.addLayout(self._row("进度:", self._val("bc_progress", "0 / 0", SC["white"])))
        lay.addLayout(self._row("运行:", self._val("bc_timer", "--:--", SC["gold"])))
        self.entry_bc_loop = NumericEntry("1")
        lay.addLayout(self._row("手动次数:", self.entry_bc_loop))
        left_panel.addLayout(lay)
        left_panel.addWidget(Separator())

        # ── 移除车辆 ──
        lay = CardLayout()
        dc_header = RowLayout()
        dc_header.addWidget(SectionLabel("[ 移除车辆  Ctrl+F2 ]", SC["orange"]))
        dc_header.addStretch()
        self.btn_dc = ToggleButton("orange")
        self.btn_dc.clicked.connect(self.toggle_delete_car)
        dc_header.addWidget(self.btn_dc)
        lay.addLayout(dc_header)
        lay.addLayout(self._row("状态:", self._val("dc_status", "■ 待机", SC["gray"])))
        lay.addLayout(self._row("进度:", self._val("dc_progress", "0 / 0", SC["white"])))
        lay.addLayout(self._row("运行:", self._val("dc_timer", "--:--", SC["gold"])))
        self.entry_dc_loop = NumericEntry("1")
        lay.addLayout(self._row("手动次数:", self.entry_dc_loop))
        left_panel.addLayout(lay)
        left_panel.addWidget(Separator())

        # ── 抽奖 ──
        lay = CardLayout()
        aw_header = RowLayout()
        aw_header.addWidget(SectionLabel("[ 抽奖  Ctrl+F3 ]", SC["purple"]))
        aw_header.addStretch()
        self.btn_aw = ToggleButton("purple")
        self.btn_aw.clicked.connect(self.toggle_award)
        aw_header.addWidget(self.btn_aw)
        lay.addLayout(aw_header)
        lay.addLayout(self._row("状态:", self._val("aw_status", "■ 待机", SC["gray"])))
        lay.addLayout(self._row("进度:", self._val("aw_progress", "0 / 0", SC["white"])))
        lay.addLayout(self._row("运行:", self._val("aw_timer", "--:--", SC["gold"])))
        self.entry_aw_loop = NumericEntry("1")
        lay.addLayout(self._row("手动次数:", self.entry_aw_loop))
        # 抽奖类型单选框
        self.aw_type_group = QButtonGroup(self)
        self.rb_super_award = QRadioButton("超级抽奖")
        self.rb_general_award = QRadioButton("普通抽奖")
        self.rb_super_award.setChecked(True)
        self.aw_type_group.addButton(self.rb_super_award, 0)
        self.aw_type_group.addButton(self.rb_general_award, 1)
        aw_type_row = RowLayout()
        aw_type_row.addWidget(KeyLabel("类型:"))
        aw_type_row.addWidget(self.rb_super_award)
        aw_type_row.addWidget(self.rb_general_award)
        aw_type_row.addStretch()
        lay.addLayout(aw_type_row)
        left_panel.addLayout(lay)
        left_panel.addWidget(Separator())

        # ── 熟练度循环 ──
        lay = CardLayout()
        b_header = RowLayout()
        b_header.addWidget(SectionLabel("[ 熟练度循环  Ctrl+F4 ]", SC["blue"]))
        b_header.addStretch()
        self.btn_b = ToggleButton("blue")
        self.btn_b.clicked.connect(self.toggle_mastery)
        b_header.addWidget(self.btn_b)
        lay.addLayout(b_header)
        lay.addLayout(self._row("状态:", self._val("b_status", "■ 待机", SC["gray"])))
        lay.addLayout(self._row("进度:", self._val("b_progress", "0 / 0", SC["white"])))
        lay.addLayout(self._row("运行:", self._val("b_timer", "--:--", SC["gold"])))
        hbox = RowLayout()
        hbox.addWidget(KeyLabel("阶段:"))
        hbox.addWidget(self._val("phase", "—", SC["yellow"]))
        hbox.addWidget(KeyLabel("剩余:"))
        hbox.addWidget(self._val("countdown", "—", SC["cyan"]))
        hbox.addStretch()
        lay.addLayout(hbox)
        self.entry_b_loop = NumericEntry("1")
        lay.addLayout(self._row("手动次数:", self.entry_b_loop))
        left_panel.addLayout(lay)
        left_panel.addWidget(Separator())

        # ── 后台发键状态 ──
        lay = CardLayout()
        lay.addWidget(SectionLabel("[ 后台发键状态 ]", SC["cyan"]))
        hbox = RowLayout()
        hbox.addWidget(KeyLabel("游戏进程:"))
        self.lbl_hwnd = ValueLabel("未找到", SC["red"])
        self._labels["lbl_hwnd"] = self.lbl_hwnd
        hbox.addWidget(self.lbl_hwnd)
        hbox.addStretch()
        btn_refresh = SmallButton("刷新窗口")
        btn_refresh.clicked.connect(self._on_refresh)
        hbox.addWidget(btn_refresh)
        lay.addLayout(hbox)
        left_panel.addLayout(lay)

        # ── 添加左侧面板到外层布局 ──
        outer_layout.addLayout(left_panel, stretch=5)

        # ── 垂直分隔线 ──
        vsep = QFrame()
        vsep.setObjectName("vsep")
        vsep.setFixedWidth(1)
        outer_layout.addWidget(vsep)

        # ── 右侧面板 ──
        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(4, 0, 0, 0)
        right_panel.setSpacing(0)

        # ── 自动大循环 ──
        lay = CardLayout()
        auto_header = RowLayout()
        auto_header.addWidget(SectionLabel("[ 自动大循环  Ctrl+F5 ]", SC["gold"]))
        auto_header.addStretch()
        self.btn_auto = ToggleButton("gold")
        self.btn_auto.clicked.connect(self.toggle_auto)
        auto_header.addWidget(self.btn_auto)
        lay.addLayout(auto_header)
        lay.addLayout(self._row("状态:", self._val("auto_status", "■ 待机", SC["gray"])))
        lay.addLayout(self._row("阶段:", self._val("auto_phase", "—", SC["yellow"])))
        self.entry_auto_loop = NumericEntry(str(cfg.AUTO_CYCLE_COUNT))
        lay.addLayout(self._row("手动次数:", self.entry_auto_loop))
        # 各子功能循环次数
        self.entry_auto_mastery = NumericEntry(str(cfg.AUTO_MASTERY_LOOPS))
        lay.addLayout(self._row("熟练度:", self.entry_auto_mastery))
        self.entry_auto_buycar = NumericEntry(str(cfg.AUTO_BUYCAR_TIMES))
        lay.addLayout(self._row("买车加点:", self.entry_auto_buycar))
        self.entry_auto_delcar = NumericEntry(str(cfg.AUTO_DELCAR_TIMES))
        lay.addLayout(self._row("移除车辆:", self.entry_auto_delcar))
        self.entry_auto_award = NumericEntry(str(cfg.AUTO_AWARD_TIMES))
        lay.addLayout(self._row("抽奖:", self.entry_auto_award))
        # 模式单选框
        self.auto_mode_group = QButtonGroup(self)
        self.rb_auto_contain = QRadioButton("包括删车和抽奖")
        self.rb_auto_simple = QRadioButton("仅刷点买车加点")
        self.rb_auto_contain.setChecked(True)
        self.auto_mode_group.addButton(self.rb_auto_contain, 0)
        self.auto_mode_group.addButton(self.rb_auto_simple, 1)
        self.rb_auto_contain.toggled.connect(self._on_auto_mode_changed)
        self.rb_auto_simple.toggled.connect(self._on_auto_mode_changed)
        auto_mode_row = RowLayout()
        auto_mode_row.addWidget(KeyLabel("模式:"))
        auto_mode_row.addWidget(self.rb_auto_contain)
        auto_mode_row.addWidget(self.rb_auto_simple)
        auto_mode_row.addStretch()
        lay.addLayout(auto_mode_row)
        lay.addLayout(self._row("当前进度:", self._val("auto_cycle", "0 / 0", SC["orange"])))
        right_panel.addLayout(lay)
        right_panel.addWidget(Separator())

        # ── 效率监控 ──
        lay = CardLayout()
        lay.addWidget(SectionLabel("[ 效率监控 ]", SC["muted"]))
        hbox = RowLayout()
        hbox.addWidget(KeyLabel("运行时长:"))
        hbox.addWidget(self._val("elapsed", "—", SC["white"]))
        hbox.addWidget(KeyLabel("总点数:"))
        hbox.addWidget(self._val("points", "—", SC["green"]))
        hbox.addStretch()
        lay.addLayout(hbox)
        lay.addLayout(self._row("预期效率:", self._val("eff", "—", SC["yellow"])))
        right_panel.addLayout(lay)
        right_panel.addWidget(Separator())

        # ── 日志记录 ──
        log_header = RowLayout()
        log_header.addWidget(SectionLabel("[ 日志记录 ]", SC["yellow"]))
        log_header.addStretch()
        btn_clear = SmallButton("清空日志")
        btn_clear.clicked.connect(lambda: self.log_text.clear())
        log_header.addWidget(btn_clear)
        right_panel.addLayout(log_header)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        right_panel.addWidget(self.log_text, stretch=1)

        outer_layout.addLayout(right_panel, stretch=5)

    # ══════════════════════════════════════════════════════════
    #  UI 辅助方法
    # ══════════════════════════════════════════════════════════
    def _val(self, name: str, text: str, color: str) -> ValueLabel:
        lbl = ValueLabel(text, color)
        self._labels[name] = lbl
        return lbl

    def _row(self, label_text: str, widget):
        hbox = RowLayout()
        hbox.addWidget(KeyLabel(label_text))
        if isinstance(widget, (QLabel, NumericEntry)):
            hbox.addWidget(widget)
        else:
            hbox.addWidget(widget)
        hbox.addStretch()
        return hbox

    # ══════════════════════════════════════════════════════════
    #  日志
    # ══════════════════════════════════════════════════════════
    def _log(self, msg: str):
        self._signals.log_signal.emit(msg)

    def _append_log(self, msg: str):
        line = f"[{time.strftime('%H:%M:%S')}] {msg}"
        self.log_text.append(line)
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)

    def _show_completion(self, title: str, message: str):
        msg = QMessageBox(QMessageBox.Icon.Information, title, message, parent=self)
        msg.setWindowIcon(self.windowIcon())
        msg.exec()

    # ══════════════════════════════════════════════════════════
    #  窗口查找
    # ══════════════════════════════════════════════════════════
    def _on_refresh(self):
        hwnd = find_game()
        import core.game_utils as gu
        gu.game_hwnd = hwnd
        self._update_hwnd_label()

    def _update_hwnd_label(self):
        hwnd = find_game()
        import core.game_utils as gu
        gu.game_hwnd = hwnd
        if hwnd:
            self.lbl_hwnd.set(f"已找到 (hwnd={hwnd})", SC["green"])
        else:
            self.lbl_hwnd.set("未找到 ← 先启动游戏", SC["red"])

    # ══════════════════════════════════════════════════════════
    #  状态更新（线程安全）
    # ══════════════════════════════════════════════════════════
    def _apply_status(self, name: str, text: str, color: str):
        lbl = self._labels.get(name)
        if lbl:
            lbl.set(text, color)

    def _set_status(self, name: str, text: str, color: str):
        self._signals.status_signal.emit(name, text, color)

    def _on_button_running(self, name: str, running: bool):
        """安全地从工作线程更新按钮状态"""
        btn = getattr(self, f'btn_{name}', None)
        if btn:
            btn.set_running(running)

    def set_bc_status(self, t, c):       self._set_status("bc_status", t, c)
    def set_dc_status(self, t, c):       self._set_status("dc_status", t, c)
    def set_aw_status(self, t, c):       self._set_status("aw_status", t, c)
    def set_b_status(self, t, c):        self._set_status("b_status", t, c)
    def set_auto_status(self, t, c):     self._set_status("auto_status", t, c)
    def set_phase(self, t):              self._set_status("phase", t, SC["yellow"])
    def set_countdown(self, t):          self._set_status("countdown", t, SC["cyan"])
    def set_auto_phase(self, t):         self._set_status("auto_phase", t, SC["yellow"])
    def set_auto_cycle(self, v, total=0):
        if total > 0:
            self._set_status("auto_cycle", f"{v} / {total}", SC["orange"])
        else:
            self._set_status("auto_cycle", str(v), SC["orange"])
    def set_bc_progress(self, c, t):     self._set_status("bc_progress", f"{c} / {t}", SC["white"])
    def set_dc_progress(self, c, t):     self._set_status("dc_progress", f"{c} / {t}", SC["white"])
    def set_aw_progress(self, c, t):     self._set_status("aw_progress", f"{c} / {t}", SC["white"])
    def set_b_progress(self, c, t):      self._set_status("b_progress", f"{c} / {t}", SC["white"])
    def update_efficiency(self, loop_count=None, points_per_loop=None):
        if self.b_start_time == 0:
            self._set_status("elapsed", "—", SC["white"])
            self._set_status("points", "—", SC["green"])
            self._set_status("eff", "—", SC["yellow"])
            return
        if loop_count is not None:
            self.b_loop_count = loop_count
        sec = (int(time.time() * 1000) - self.b_start_time) / 1000.0
        total = self.b_loop_count * (points_per_loop or cfg.POINTS_PER_LOOP)
        eff = round(total / sec * 3600) if sec > 0 else 0
        self._set_status("elapsed", f"{round(sec)} s", SC["white"])
        self._set_status("points", f"{total} 个", SC["green"])
        self._set_status("eff", f"{eff} 个/小时", SC["yellow"])

    def update_bc_timer(self):
        if not self.bc_running:
            return
        e = int(time.time() * 1000) - self.bc_start_time
        self._set_status("bc_timer", f"{e // 60000:02d}:{(e // 1000) % 60:02d}", SC["gold"])

    def update_dc_timer(self):
        if not self.dc_running:
            return
        e = int(time.time() * 1000) - self.dc_start_time
        self._set_status("dc_timer", f"{e // 60000:02d}:{(e // 1000) % 60:02d}", SC["gold"])

    def update_aw_timer(self):
        if not self.aw_running:
            return
        e = int(time.time() * 1000) - self.aw_start_time
        self._set_status("aw_timer", f"{e // 60000:02d}:{(e // 1000) % 60:02d}", SC["gold"])

    def update_b_timer(self):
        if not self.b_running:
            return
        e = int(time.time() * 1000) - self.b_start_time
        self._set_status("b_timer", f"{e // 60000:02d}:{(e // 1000) % 60:02d}", SC["gold"])

    # ══════════════════════════════════════════════════════════
    #  定时器
    # ══════════════════════════════════════════════════════════
    def _tick(self):
        self.update_bc_timer()
        self.update_dc_timer()
        self.update_aw_timer()
        self.update_b_timer()

    # ══════════════════════════════════════════════════════════
    #  运行状态检查
    # ══════════════════════════════════════════════════════════
    def any_running(self) -> bool:
        return (self.bc_running or self.dc_running or self.aw_running or
                self.b_running or self.auto_running)

    def _ensure_game(self) -> bool:
        import core.game_utils as gu
        if not gu.game_hwnd:
            self._on_refresh()
            if not gu.game_hwnd:
                self._log("!!! 未找到游戏窗口，无法启动")
                return False
        return True

    # ══════════════════════════════════════════════════════════
    #  F1: 买车+加点
    # ══════════════════════════════════════════════════════════
    def toggle_buy_car(self):
        if self.bc_running:
            self.bc_running = False
            self.btn_bc.set_running(False)
            self.set_bc_status("■ 待机", SC["gray"])
            self._log("<<< 买车循环 手动停止")
            return
        if self.any_running():
            self._log("!!! 有其他循环运行中，请先停止")
            return
        if not self._ensure_game():
            return

        try:
            self.bc_total = int(self.entry_bc_loop.text())
        except ValueError:
            self.bc_total = 1
        if self.bc_total < 1:
            self.bc_total = 1

        self.bc_running = True
        self.btn_bc.set_running(True)
        self.bc_loop_count = 0
        self.bc_start_time = int(time.time() * 1000)
        self._set_status("bc_timer", "00:00", SC["gold"])
        self.set_bc_progress(0, self.bc_total)
        self.set_bc_status("▶ 后台运行", SC["green"])
        self._log(f">>> 买车循环 启动（手动），共 {self.bc_total} 次")

        self.bc_thread = threading.Thread(target=self._buy_car_loop, daemon=True)
        self.bc_thread.start()

    def _buy_car_loop(self):
        from modules.buy_car import run_buy_car_body

        for i in range(self.bc_total):
            if not self.bc_running:
                break
            self.bc_loop_count = i + 1
            self.set_bc_progress(self.bc_loop_count, self.bc_total)
            self._log(f"=== 第 {self.bc_loop_count} / {self.bc_total} 次循环开始 ===")
            if not run_buy_car_body(lambda: self.bc_running):
                break
            self._log(f"=== 第 {self.bc_loop_count} 次完成 ===")

        done = self.bc_loop_count >= self.bc_total
        self.bc_running = False
        self._signals.button_running_signal.emit('bc', False)
        self.set_bc_status("■ 待机", SC["gray"])
        self.set_bc_progress(self.bc_loop_count, self.bc_total)
        self._log(">>> 买车循环 全部完成！" if done else ">>> 买车循环 已停止")
        if done:
            self._signals.completion_signal.emit("完成", f"全部完成！\n共执行 {self.bc_total} 次循环。")

    # ══════════════════════════════════════════════════════════
    #  F2: 移除车辆
    # ══════════════════════════════════════════════════════════
    def toggle_delete_car(self):
        if self.dc_running:
            self.dc_running = False
            self.btn_dc.set_running(False)
            self.set_dc_status("■ 待机", SC["gray"])
            self._log("<<< 移除车辆循环 手动停止")
            return
        if self.any_running():
            self._log("!!! 有其他循环运行中，请先停止")
            return
        if not self._ensure_game():
            return

        try:
            self.dc_total = int(self.entry_dc_loop.text())
        except ValueError:
            self.dc_total = 1
        if self.dc_total < 1:
            self.dc_total = 1

        self.dc_running = True
        self.btn_dc.set_running(True)
        self.dc_loop_count = 0
        self.dc_start_time = int(time.time() * 1000)
        self._set_status("dc_timer", "00:00", SC["gold"])
        self.set_dc_progress(0, self.dc_total)
        self.set_dc_status("▶ 后台运行", SC["green"])
        self._log(f">>> 移除车辆循环 启动（手动），共 {self.dc_total} 次")

        self.dc_thread = threading.Thread(target=self._delete_car_loop, daemon=True)
        self.dc_thread.start()

    def _delete_car_loop(self):
        from modules.delete_car import run_delete_car_body
        from core.game_utils import press, safe_sleep, navigate_to_brand, poll_image

        self._log("--- 导航至制造商 ---")
        if not safe_sleep(cfg.DC_INIT_WAIT, lambda: self.dc_running):
            return
        if not press("Up", 80, 80, lambda: self.dc_running):
            return
        if not press("Up", 80, 80, lambda: self.dc_running):
            return
        if not press("Up", 80, 80, lambda: self.dc_running):
            return
        if not press("Enter", 100, cfg.DC_MENU_ENTER, lambda: self.dc_running):
            return
        if not poll_image(cfg.IMG_MY_CAR, 5.0, 300, lambda: self.dc_running):
            self._log("  !! 超时未检测到我的车辆")
            return False
        
        if not press("BackSpace", 100, 800, lambda: self.dc_running):
            return

        if not navigate_to_brand(lambda: self.dc_running):
            return
        if not press("Enter", 80, 1000, lambda: self.dc_running):
            return

        for i in range(self.dc_total):
            if not self.dc_running:
                break
            self.dc_loop_count = i + 1
            self.set_dc_progress(self.dc_loop_count, self.dc_total)
            self._log(f"=== 第 {self.dc_loop_count} / {self.dc_total} 次移除车辆开始 ===")
            if not run_delete_car_body(lambda: self.dc_running):
                break
            self._log(f"=== 第 {self.dc_loop_count} 次移除车辆完成 ===")

        if not press("Esc", 80, cfg.DC_ESC_FINAL, lambda: self.dc_running):
            return

        done = self.dc_loop_count >= self.dc_total
        self.dc_running = False
        self._signals.button_running_signal.emit('dc', False)
        self.set_dc_status("■ 待机", SC["gray"])
        self.set_dc_progress(self.dc_loop_count, self.dc_total)
        self._log(">>> 移除车辆循环 全部完成！" if done else ">>> 移除车辆循环 已停止")
        if done:
            self._signals.completion_signal.emit("完成", f"移除车辆完成！\n共执行 {self.dc_total} 次。")

    # ══════════════════════════════════════════════════════════
    #  F3: 抽奖
    # ══════════════════════════════════════════════════════════
    def toggle_award(self):
        if self.aw_running:
            self.aw_running = False
            self.btn_aw.set_running(False)
            self.set_aw_status("■ 待机", SC["gray"])
            self._log("<<< 抽奖循环 手动停止")
            return
        if self.any_running():
            self._log("!!! 有其他循环运行中，请先停止")
            return
        if not self._ensure_game():
            return

        try:
            self.aw_total = int(self.entry_aw_loop.text())
        except ValueError:
            self.aw_total = 1
        if self.aw_total < 1:
            self.aw_total = 1

        self.aw_running = True
        self.btn_aw.set_running(True)
        self.aw_loop_count = 0
        self.aw_start_time = int(time.time() * 1000)
        self._set_status("aw_timer", "00:00", SC["gold"])
        self.set_aw_progress(0, self.aw_total)
        self.set_aw_status("▶ 后台运行", SC["green"])
        # 读取抽奖类型（必须在主线程中读取 GUI 控件）
        award_img = cfg.IMG_GENERAL_AWARD_ENTER if self.rb_general_award.isChecked() else cfg.IMG_AWARD_ENTER
        award_type_name = "普通抽奖" if self.rb_general_award.isChecked() else "超级抽奖"
        self._log(f">>> 抽奖循环 启动（手动）- {award_type_name}，共 {self.aw_total} 次")

        self.aw_thread = threading.Thread(target=self._award_loop, args=(award_img,), daemon=True)
        self.aw_thread.start()

    def _award_loop(self, award_img):
        from modules.award import run_award_body
        from core.game_utils import find_and_click_image, safe_sleep

        # 点击抽奖入口（首次需要）
        if find_and_click_image(award_img):
            self._log("  ✓ 点击抽奖入口")
            if not safe_sleep(300, lambda: self.aw_running):
                return
            for i in range(self.aw_total):
                if not self.aw_running:
                    break
                self.aw_loop_count = i + 1
                self.set_aw_progress(self.aw_loop_count, self.aw_total)
                self._log(f"=== 第 {self.aw_loop_count} / {self.aw_total} 次抽奖开始 ===")
                if not run_award_body(lambda: self.aw_running, is_last=(i == self.aw_total - 1)):
                    break
                self._log(f"=== 第 {self.aw_loop_count} 次抽奖完成 ===")
        else:
            self._log("  !! 未检测到抽奖入口")

        done = self.aw_loop_count >= self.aw_total
        self.aw_running = False
        self._signals.button_running_signal.emit('aw', False)
        self.set_aw_status("■ 待机", SC["gray"])
        self.set_aw_progress(self.aw_loop_count, self.aw_total)
        self._log(">>> 抽奖循环 全部完成！" if done else ">>> 抽奖循环 已停止")
        if done:
            self._signals.completion_signal.emit("完成", f"抽奖完成！\n共执行 {self.aw_total} 次。")

    # ══════════════════════════════════════════════════════════
    #  F4: 熟练度循环
    # ══════════════════════════════════════════════════════════
    def toggle_mastery(self):
        if self.b_running:
            self.b_running = False
            self.btn_b.set_running(False)
            self.b_start_time = 0
            gsend("{w up}")
            gsend("{Enter up}")
            gsend("{x up}")
            self.set_b_status("■ 待机", SC["gray"])
            self.set_phase("—")
            self.set_countdown("—")
            self.update_efficiency(0)
            self._log("<<< 熟练度循环 手动停止")
            return
        if self.any_running():
            self._log("!!! 有其他循环运行中，请先停止")
            return
        if not self._ensure_game():
            return

        try:
            self.b_total = int(self.entry_b_loop.text())
        except ValueError:
            self.b_total = 1
        if self.b_total < 1:
            self.b_total = 1

        self.b_loop_count = 0
        self.b_start_time = int(time.time() * 1000)
        self.b_running = True
        self.btn_b.set_running(True)
        self._set_status("b_timer", "00:00", SC["gold"])
        self.set_b_progress(0, self.b_total)
        self.update_efficiency(0)
        self.set_b_status("▶ 后台运行", SC["green"])
        self._log(f">>> 熟练度循环 启动（手动），共 {self.b_total} 次")

        self.b_thread = threading.Thread(target=self._mastery_loop, daemon=True)
        self.b_thread.start()

    def _mastery_loop(self):
        from modules.mastery import run_mastery_body

        try:
            for i in range(self.b_total):
                if not self.b_running:
                    break
                self.b_loop_count = i + 1
                self.set_b_progress(self.b_loop_count, self.b_total)
                self._log(f"── 第 {self.b_loop_count} / {self.b_total} 轮 ──")
                if not run_mastery_body(
                    lambda: self.b_running,
                    lambda t: self.set_phase(t),
                    lambda t: self.set_countdown(t)
                ):
                    break
                self.update_efficiency()
        finally:
            gsend("{w up}")
            gsend("{Enter up}")
            gsend("{x up}")
            self.set_phase("—")
            self.set_countdown("—")
            final_count = self.b_loop_count
            self.update_efficiency(0)
            done = final_count >= self.b_total
            self.b_running = False
            self._signals.button_running_signal.emit('b', False)
            self.set_b_status("■ 待机", SC["gray"])
            self.set_b_progress(final_count, self.b_total)
            self._log(">>> 熟练度循环 全部完成！" if done else "<<< 熟练度循环 已停止")
            if done:
                self._signals.completion_signal.emit("完成", f"熟练度循环完成！\n共执行 {final_count} 次。")

    # ══════════════════════════════════════════════════════════
    #  F5: 自动大循环
    # ══════════════════════════════════════════════════════════
    def _on_auto_mode_changed(self, checked):
        if not checked:
            return
        if self.rb_auto_contain.isChecked():
            self.auto_mode = "contain"
            self.entry_auto_delcar.setEnabled(True)
            self.entry_auto_award.setEnabled(True)
        else:
            self.auto_mode = "simple"
            self.entry_auto_delcar.setEnabled(False)
            self.entry_auto_award.setEnabled(False)

    def toggle_auto(self):
        if self.auto_running:
            self.auto_running = False
            self.b_running = False
            self.bc_running = False
            self.dc_running = False
            self.aw_running = False
            self.b_start_time = 0
            self.btn_auto.set_running(False)
            self.btn_b.set_running(False)
            self.btn_bc.set_running(False)
            self.btn_dc.set_running(False)
            self.btn_aw.set_running(False)
            gsend("{w up}")
            gsend("{Enter up}")
            gsend("{x up}")
            self.set_auto_status("■ 已停止", SC["gray"])
            self.set_auto_phase("—")
            self.set_b_status("■ 待机", SC["gray"])
            self.set_bc_status("■ 待机", SC["gray"])
            self.set_dc_status("■ 待机", SC["gray"])
            self.set_aw_status("■ 待机", SC["gray"])
            self.set_b_progress(0, 0)
            self.set_bc_progress(0, 0)
            self.set_dc_progress(0, 0)
            self.set_aw_progress(0, 0)
            self.update_efficiency(0)
            self._log("<<< 自动大循环 手动停止")
            return
        if self.any_running():
            self._log("!!! 有其他循环运行中，请先停止")
            return
        if not self._ensure_game():
            return

        self.auto_running = True
        # 读取各子功能自定义次数
        try:
            self.auto_mastery = int(self.entry_auto_mastery.text())
        except ValueError:
            self.auto_mastery = cfg.AUTO_MASTERY_LOOPS
        if self.auto_mastery < 1:
            self.auto_mastery = 1
        try:
            self.auto_buycar = int(self.entry_auto_buycar.text())
        except ValueError:
            self.auto_buycar = cfg.AUTO_BUYCAR_TIMES
        if self.auto_buycar < 1:
            self.auto_buycar = 1
        try:
            self.auto_delcar = int(self.entry_auto_delcar.text())
        except ValueError:
            self.auto_delcar = cfg.AUTO_DELCAR_TIMES
        if self.auto_delcar < 1:
            self.auto_delcar = 1
        try:
            self.auto_award = int(self.entry_auto_award.text())
        except ValueError:
            self.auto_award = cfg.AUTO_AWARD_TIMES
        if self.auto_award < 1:
            self.auto_award = 1
        self.b_total = self.auto_mastery
        self.bc_total = self.auto_buycar
        try:
            self.auto_total = int(self.entry_auto_loop.text())
        except ValueError:
            self.auto_total = 0
        if self.auto_total < 0:
            self.auto_total = 0
        self.btn_auto.set_running(True)
        self.set_auto_cycle(0, self.auto_total)
        self.set_auto_phase("启动中...")
        self.set_auto_status("▶ 运行中", SC["green"])
        self.set_b_progress(0, self.b_total)
        self.set_bc_progress(0, self.bc_total)
        mode_label = "（包括删车和抽奖）" if self.auto_mode == "contain" else "（仅刷点买车加点）"
        self._log(f">>> 自动大循环 启动 {mode_label}")
        suffix = " → 车库→蓝图 → 循环"
        if self.auto_mode == "contain":
            suffix = " → 车库→我的地平线 → 买车加点 → 删车 → 抽奖 → 循环"
        self._log(f"    熟练度 {self.auto_mastery} 轮 → 蓝图→车库 → "
                  f"买车 {self.auto_buycar} 次{suffix}"
                  + (f"（共 {self.auto_total} 轮）" if self.auto_total > 0 else "（无限循环）"))

        self.auto_thread = threading.Thread(target=self._auto_big_loop, daemon=True)
        self.auto_thread.start()

    def _auto_big_loop(self):
        from modules.auto_cycle import run_auto_big_loop_contain, run_auto_big_loop

        if self.auto_mode == "contain":
            run_auto_big_loop_contain(
                running_flag=lambda: self.auto_running,
                max_cycles=self.auto_total,
                mastery_loops=self.auto_mastery,
                buycar_times=self.auto_buycar,
                delcar_times=self.auto_delcar,
                award_times=self.auto_award,
                mastery_phase_callback=lambda t: self.set_phase(t),
                mastery_countdown_callback=lambda t: self.set_countdown(t),
                auto_phase_callback=lambda t: self.set_auto_phase(t),
                auto_cycle_callback=lambda v: self.set_auto_cycle(v, self.auto_total),
                b_status_callback=lambda t, c: self.set_b_status(t, c),
                bc_status_callback=lambda t, c: self.set_bc_status(t, c),
                dc_status_callback=lambda t, c: self.set_dc_status(t, c),
                aw_status_callback=lambda t, c: self.set_aw_status(t, c),
                b_loop_count_callback=lambda v: setattr(self, 'b_loop_count', v),
                b_progress_callback=lambda c, t: self.set_b_progress(c, t),
                bc_progress_callback=lambda c, t: self.set_bc_progress(c, t),
                dc_progress_callback=lambda c, t: self.set_dc_progress(c, t),
                aw_progress_callback=lambda c, t: self.set_aw_progress(c, t),
                b_timer_start_callback=self._auto_b_timer_start,
                b_timer_stop_callback=self._auto_b_timer_stop,
                efficiency_update_callback=lambda lc, ppl: self.update_efficiency(lc, ppl),
                bc_timer_start_callback=self._auto_bc_timer_start,
                bc_timer_stop_callback=self._auto_bc_timer_stop,
                dc_timer_start_callback=self._auto_dc_timer_start,
                dc_timer_stop_callback=self._auto_dc_timer_stop,
                aw_timer_start_callback=self._auto_aw_timer_start,
                aw_timer_stop_callback=self._auto_aw_timer_stop,
            )
        else:
            run_auto_big_loop(
                running_flag=lambda: self.auto_running,
                max_cycles=self.auto_total,
                mastery_loops=self.auto_mastery,
                buycar_times=self.auto_buycar,
                mastery_phase_callback=lambda t: self.set_phase(t),
                mastery_countdown_callback=lambda t: self.set_countdown(t),
                auto_phase_callback=lambda t: self.set_auto_phase(t),
                auto_cycle_callback=lambda v: self.set_auto_cycle(v, self.auto_total),
                b_status_callback=lambda t, c: self.set_b_status(t, c),
                bc_status_callback=lambda t, c: self.set_bc_status(t, c),
                b_loop_count_callback=lambda v: setattr(self, 'b_loop_count', v),
                b_progress_callback=lambda c, t: self.set_b_progress(c, t),
                bc_progress_callback=lambda c, t: self.set_bc_progress(c, t),
                b_timer_start_callback=self._auto_b_timer_start,
                b_timer_stop_callback=self._auto_b_timer_stop,
                efficiency_update_callback=lambda lc, ppl: self.update_efficiency(lc, ppl),
                bc_timer_start_callback=self._auto_bc_timer_start,
                bc_timer_stop_callback=self._auto_bc_timer_stop,
            )

        self.auto_running = False
        self.b_running = False
        self.bc_running = False
        self.dc_running = False
        self.aw_running = False
        self.b_start_time = 0
        self._signals.button_running_signal.emit('auto', False)
        self._signals.button_running_signal.emit('b', False)
        self._signals.button_running_signal.emit('bc', False)
        self._signals.button_running_signal.emit('dc', False)
        self._signals.button_running_signal.emit('aw', False)
        gsend("{w up}")
        gsend("{Enter up}")
        gsend("{x up}")
        self.set_phase("—")
        self.set_countdown("—")
        self.update_efficiency(0)
        self.set_b_status("■ 待机", SC["gray"])
        self.set_bc_status("■ 待机", SC["gray"])
        self.set_dc_status("■ 待机", SC["gray"])
        self.set_aw_status("■ 待机", SC["gray"])
        self.set_b_progress(0, 0)
        self.set_bc_progress(0, 0)
        self.set_dc_progress(0, 0)
        self.set_aw_progress(0, 0)
        self.set_auto_phase("—")
        self.set_auto_status("■ 待机", SC["gray"])

    def _auto_b_timer_start(self):
        """熟练度阶段计时器启动"""
        self.b_running = True
        self.b_start_time = int(time.time() * 1000)
        self._set_status("b_timer", "00:00", SC["gold"])
        self._signals.button_running_signal.emit('b', True)

    def _auto_b_timer_stop(self):
        """熟练度阶段计时器停止"""
        self.b_running = False
        self._signals.button_running_signal.emit('b', False)
        self.update_efficiency(0)
        self.set_phase("—")
        self.set_countdown("—")
        self._cleanup_mastery_keys()

    def _auto_bc_timer_start(self):
        """买车加点阶段计时器启动"""
        self.bc_running = True
        self.bc_start_time = int(time.time() * 1000)
        self._set_status("bc_timer", "00:00", SC["gold"])
        self._signals.button_running_signal.emit('bc', True)

    def _auto_bc_timer_stop(self):
        """买车加点阶段计时器停止"""
        self.bc_running = False
        self._signals.button_running_signal.emit('bc', False)

    def _auto_dc_timer_start(self):
        """移除车辆阶段计时器启动"""
        self.dc_running = True
        self.dc_start_time = int(time.time() * 1000)
        self._set_status("dc_timer", "00:00", SC["gold"])
        self._signals.button_running_signal.emit('dc', True)

    def _auto_dc_timer_stop(self):
        """移除车辆阶段计时器停止"""
        self.dc_running = False
        self._signals.button_running_signal.emit('dc', False)

    def _auto_aw_timer_start(self):
        """抽奖阶段计时器启动"""
        self.aw_running = True
        self.aw_start_time = int(time.time() * 1000)
        self._set_status("aw_timer", "00:00", SC["gold"])
        self._signals.button_running_signal.emit('aw', True)

    def _auto_aw_timer_stop(self):
        """抽奖阶段计时器停止"""
        self.aw_running = False
        self._signals.button_running_signal.emit('aw', False)

    @staticmethod
    def _cleanup_mastery_keys():
        """释放熟练度相关的按键"""
        gsend("{w up}")
        gsend("{Enter up}")
        gsend("{x up}")
