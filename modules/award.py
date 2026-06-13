# -*- coding: utf-8 -*-
"""
FH6 AutoScript - 抽奖模块 (Ctrl+F3)
"""

import core.config as cfg
from core.game_utils import (
    press, find_image, safe_sleep, log, poll_image
)


def run_award_body(running_flag, is_last: bool = False) -> bool:
    """抽奖单次循环体（供手动和自动共用）"""

    # 2. 检测跳过按钮
    log("  查找跳过按钮...")
    if not poll_image(cfg.IMG_AWARD_SKIP, 5.0, 300, running_flag):
        log("  !! 超时未检测到跳过按钮")
        return False
    if press("Enter", 80, 150, running_flag):
        log("  ✓ 跳过动画")

    # 3. 等待继续按钮，按 ENTER 继续下一抽 / 最后一次按 ESC
    log("  等待继续界面...")
    if not poll_image(cfg.IMG_AWARD_CONTINUE, 15.0, 500, running_flag):
        log("  !! 超时未检测到继续按钮")
        return False
    if is_last:
        if press("Esc", 80, 150, running_flag):
            log("  ✓ 最后一次，按 ESC 退出")
    else:
        if press("Enter", 80, 150, running_flag):
            log("  ✓ 继续下一抽")

    # 4. 处理重复车辆弹窗
    for i in range(3):
        if not running_flag():
            return False
        if not safe_sleep(300, running_flag):
            return False
        if find_image(cfg.IMG_AWARD_CAR):
            log(f"  ✓ 检测到重复车辆 #{i + 1}，按 ENTER 确认")
            press("Enter", 80, 150, running_flag)
        else:
            break
    return True


def award_loop(loop_count: int, running_flag, progress_callback=None) -> bool:
    """抽奖循环（手动模式）"""
    completed = 0
    for i in range(loop_count):
        if not running_flag():
            break
        if progress_callback:
            progress_callback(i + 1, loop_count)
        log(f"=== 第 {i + 1} / {loop_count} 次抽奖开始 ===")
        if not run_award_body(running_flag, is_last=(i == loop_count - 1)):
            break
        completed = i + 1
        log(f"=== 第 {i + 1} 次抽奖完成 ===")

    # 循环结束后，在继续界面按 ESC 领取奖励并退出
    if completed > 0:
        log("--- 退出抽奖入口 ---")
        if poll_image(cfg.IMG_AWARD_CONTINUE, 10.0, 500, running_flag):
            if press("Esc", 80, 0, running_flag):
                log("  ✓ 按 ESC 领取奖励并退出")
            safe_sleep(1500, running_flag)
    return completed >= loop_count