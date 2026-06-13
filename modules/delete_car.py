# -*- coding: utf-8 -*-
"""
FH6 AutoScript - 删车模块 (Ctrl+F2)
"""

import time
import core.config as cfg
from core.game_utils import (
    press, find_image, find_and_click_image, log
)


def run_delete_car_body(running_flag) -> bool:
    """删车单次循环体"""
    log("--- 一次确认待删除车辆性能 ---")
    if not find_image(cfg.IMG_DEL_CONFIRM):
        log("--- 查找待删除车辆 ---")
        found = False
        for _ in range(5):
            if find_and_click_image(cfg.IMG_DEL_CAR):
                found = True
                break
            log("  未找到，按 Right 切换")
            if not press("Right", 80, 500, running_flag):
                return False

        if not found:
            log("!!! 未找到车辆")
            return False

    time.sleep(1)
    log("--- 二次确认待删除车辆性能 ---")
    if not find_image(cfg.IMG_DEL_CONFIRM):
        log("!!! 待删除车辆性能不匹配")
        return False
    
    time.sleep(1)
    log("--- 三次确认待删除车辆选择框 ---")
    if not find_image(cfg.IMG_DEL_CHOICE):
        log("!!! 待删除车辆确认选择不匹配")
        return False

    time.sleep(1)
    log("--- 执行删除序列 ---")
    if not press("Enter", 80, 500, running_flag):
        return False
    for _ in range(4):
        if not press("Down", 80, 300, running_flag):
            return False
    if not press("Enter", 80, 500, running_flag):
        return False
    if not press("Down", 80, 300, running_flag):
        return False
    if not press("Enter", 80, 1500, running_flag):
        return False
    return True


def delete_car_loop(loop_count: int, running_flag, progress_callback=None) -> bool:
    """删车循环（手动模式）"""
    for i in range(loop_count):
        if not running_flag():
            break
        if progress_callback:
            progress_callback(i + 1, loop_count)
        log(f"=== 第 {i + 1} / {loop_count} 次删车开始 ===")
        if not run_delete_car_body(running_flag):
            break
        log(f"=== 第 {i + 1} 次删车完成 ===")

    press("Esc", 80, cfg.DC_ESC_FINAL, lambda: True)
    return (i + 1) >= loop_count