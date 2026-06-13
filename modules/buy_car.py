# -*- coding: utf-8 -*-
"""
FH6 AutoScript - 买车+加点模块 (Ctrl+F1)
"""

import core.config as cfg
from core.game_utils import safe_sleep, press, navigate_to_brand, wait_bottom_left_not_black, log, poll_image, find_image



def run_buy_car_body(running_flag) -> bool:
    """买车单次循环体（供手动和自动共用）"""
    log("--- 买车 ---")

    if not safe_sleep(cfg.BC_INIT_WAIT, running_flag):
        return False
    if not press("Up", 80, 80, running_flag):
        return False
    if not press("Up", 80, 80, running_flag):
        return False
    if not press("Up", 80, 80, running_flag):
        return False
    if not press("Enter", 100, cfg.BC_MENU_ENTER, running_flag):
        return False
    if not poll_image(cfg.IMG_BUY_CAR, 5.0, 300, running_flag):
        log("  !! 超时未检测到购买车辆")
        return False
    if not press("BackSpace", 100, 800, running_flag):
        return False

    if not navigate_to_brand(running_flag):
        return False
    if not press("Enter", 80, 1000, running_flag):
        return False

    if not press("Right", 80, 150, running_flag):
        return False
    if not press("Right", 80, 150, running_flag):
        return False
    if not press("Right", 80, 150, running_flag):
        return False
    if not press("Enter", 80, cfg.BC_CONFIRM_WAIT, running_flag):
        return False
    if not poll_image(cfg.IMG_COLOR, 15.0, 300, running_flag):
        log("  !! 超时未检测到车辆颜色")
        return False
    if not press("y", 80, cfg.BC_PURCHASE_CFM, running_flag):
        return False
    if not press("Enter", 80, 700, running_flag):
        return False
    if not press("Enter", 80, 700, running_flag):
        return False
    if not press("Enter", 80, cfg.BC_AFTER_BUY, running_flag):
        return False

    log("--- 等待购车完成 ---")
    if not wait_bottom_left_not_black(running_flag):
        return False
    if not poll_image(cfg.IMG_PHOTO, 15.0, 300, running_flag):
        log("  !! 超时未检测到拍照模式")
        return False

    log("--- 加点 ---")
    if not press("Esc", 100, cfg.BC_ESC_WAIT, running_flag):
        return False
    if not press("Right", 100, cfg.BC_SKILL_ENTER, running_flag):
        return False
    if not press("Down", 100, 700, running_flag):
        return False
    if not press("Enter", 100, cfg.BC_SKILL_SETTLE, running_flag):
        return False
    for _ in range(7):
        if not press("Down", 80, 180, running_flag):
            return False
    if not press("Enter", 80, cfg.BC_SKILL_APPLY, running_flag):
        return False
    if not poll_image(cfg.IMG_CAR_TEC, 15.0, 300, running_flag):
        log("  !! 超时未检测到车辆熟练度")
        return False
    if not press("Enter", 80, 1200, running_flag):
        return False
    # if not find_image(cfg.IMG_NOT_ENOUGH):
    #     log("  !! 熟练度不足")
    #     return False
    if not press("Right", 80, 250, running_flag):
        return False
    if not press("Enter", 80, 600, running_flag):
        return False
    if not press("Up", 80, 250, running_flag):
        return False
    if not press("Enter", 80, 600, running_flag):
        return False
    if not press("Up", 80, 250, running_flag):
        return False
    if not press("Enter", 80, 600, running_flag):
        return False
    if not press("Up", 80, 250, running_flag):
        return False
    if not press("Enter", 80, 600, running_flag):
        return False
    if not press("Left", 80, 250, running_flag):
        return False
    if not press("Enter", 80, 600, running_flag):
        return False
    if not press("Esc", 80, cfg.BC_ESC_FINAL, running_flag):
        return False
    if not press("Esc", 80, cfg.BC_ESC_FINAL2, running_flag):
        return False
    if not press("Left", 80, 0, running_flag):
        return False
    return True


def buy_car_loop(loop_count: int, running_flag, progress_callback=None) -> bool:
    """买车循环（手动模式）"""
    for i in range(loop_count):
        if not running_flag():
            break
        if progress_callback:
            progress_callback(i + 1, loop_count)
        log(f"=== 第 {i + 1} / {loop_count} 次循环开始 ===")
        if not run_buy_car_body(running_flag):
            break
        log(f"=== 第 {i + 1} 次完成 ===")
    return (i + 1) >= loop_count