# -*- coding: utf-8 -*-
"""
FH6 AutoScript - 熟练度循环模块 (Ctrl+F4)
"""

import time
import win32gui
import core.config as cfg
from core.game_utils import (
    gsend, interrupt_sleep, get_window_pixel_color, log, game_hwnd
)


def run_mastery_body(running_flag, phase_callback=None, countdown_callback=None) -> bool:
    """熟练度单轮循环体（供手动和自动共用）"""
    global game_hwnd

    if phase_callback:
        phase_callback("确认")
    gsend("{Enter down}")
    if not interrupt_sleep(100, running_flag, countdown_callback):
        gsend("{Enter up}")
        return False
    gsend("{Enter up}")

    if phase_callback:
        phase_callback(f"等待进入 {cfg.MA_INIT_WAIT // 1000}s")
    if not interrupt_sleep(cfg.MA_INIT_WAIT, running_flag, countdown_callback):
        return False

    if phase_callback:
        phase_callback(f"W 油门 {cfg.MA_DRIVE_MS // 1000}s")
    gsend("{w down}")
    if not interrupt_sleep(cfg.MA_DRIVE_MS, running_flag, countdown_callback):
        gsend("{w up}")
        gsend("{Enter up}")
        return False
    gsend("{Enter up}")

    if phase_callback:
        phase_callback("等待结算画面")
    wait_start = int(time.time() * 1000)
    got_result = False
    while True:
        if not running_flag():
            return False
        try:
            rect = win32gui.GetClientRect(game_hwnd)
            cw = rect[2] - rect[0]
            ch = rect[3] - rect[1]
        except:
            got_result = True
            break

        col = get_window_pixel_color(game_hwnd, cw // 2, ch - 1)
        r = (col >> 16) & 0xFF
        g = (col >> 8) & 0xFF
        b = col & 0xFF
        avg = (r + g + b) // 3

        if avg > 0x18 and avg < 0x50 and abs(r - g) < 20 and abs(g - b) < 20:
            log(f"  ✓ 检测到结算画面 RGB=({r},{g},{b})")
            got_result = True
            time.sleep(0.2)
            break

        elapsed = int(time.time() * 1000) - wait_start
        if countdown_callback:
            countdown_callback(f"{max(0, (15000 - elapsed) // 1000)}s")
        if elapsed > 15000:
            log("  ⚠ 结算画面等待超时(15s)，跳过X操作直接结算")
            break
        time.sleep(0.1)

    if not running_flag():
        return False

    if got_result:
        if phase_callback:
            phase_callback("X 操作")
        gsend("{x down}")
        if not interrupt_sleep(100, running_flag, countdown_callback):
            gsend("{x up}")
            return False
        gsend("{x up}")
        if not interrupt_sleep(100, running_flag, countdown_callback):
            return False

        if phase_callback:
            phase_callback("连按确认")
        gsend("{Enter down}")
        time.sleep(0.1)
        gsend("{Enter up}")
        time.sleep(0.1)
        gsend("{Enter down}")
        time.sleep(0.1)
        gsend("{Enter up}")
        time.sleep(0.1)

    gsend("{Esc down}")
    time.sleep(0.1)
    gsend("{Esc up}")
    time.sleep(0.8)
    gsend("{Left down}")
    time.sleep(0.1)
    gsend("{Left up}")
    time.sleep(0.4)
    gsend("{Enter down}")
    time.sleep(0.1)
    gsend("{Enter up}")
    time.sleep(0.4)
    gsend("{Enter down}")
    time.sleep(0.1)
    gsend("{Enter up}")

    if phase_callback:
        phase_callback(f"等待结算 {cfg.MA_SETTLE_MS // 1000}s")
    if not interrupt_sleep(cfg.MA_SETTLE_MS, running_flag, countdown_callback):
        gsend("{Enter up}")
        return False
    gsend("{Enter up}")
    time.sleep(0.15)

    if phase_callback:
        phase_callback("等待加载画面消失")
    while True:
        if not running_flag():
            return False
        try:
            rect = win32gui.GetClientRect(game_hwnd)
            cw = rect[2] - rect[0]
            ch = rect[3] - rect[1]
        except:
            break

        px = cw // 2
        py = ch // 2
        on_load_screen = False
        for i in range(5):
            sx = px - 40 + i * 20
            col = get_window_pixel_color(game_hwnd, sx, py)
            r = (col >> 16) & 0xFF
            g = (col >> 8) & 0xFF
            b = col & 0xFF
            is_teal = r < 100 and g > 130 and b > 100
            is_pink = r > 160 and g < 100 and b > 60
            if is_teal or is_pink:
                on_load_screen = True
                log(f"  … 加载画面中 [{i + 1}] RGB=({r},{g},{b})")
                break
        if not on_load_screen:
            log("  ✓ 加载画面已消失，进入下一轮")
            time.sleep(0.2)
            break
        time.sleep(0.1)
    return True