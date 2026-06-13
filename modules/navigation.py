# -*- coding: utf-8 -*-
"""
FH6 AutoScript - 导航模块
蓝图→车库、车库→蓝图、漫游界面→蓝图 导航序列
"""

import time
import core.config as cfg
from core.game_utils import gsend, log


def nav_k(key: str, hold_ms: int, delay_ms: int, running_flag) -> bool:
    """导航按键：按下 hold_ms 毫秒，等待 delay_ms 毫秒"""
    if not running_flag():
        return False
    deadline = int(time.time() * 1000) + hold_ms + delay_ms

    gsend("{" + key + " down}")
    # 等待 hold_ms
    while int(time.time() * 1000) < deadline - delay_ms:
        if not running_flag():
            gsend("{" + key + " up}")
            return False
        time.sleep(0.03)
    gsend("{" + key + " up}")
    # 等待 delay_ms
    while int(time.time() * 1000) < deadline:
        if not running_flag():
            return False
        time.sleep(0.03)
    return True


def run_nav_seq(seq: list, running_flag) -> bool:
    """执行导航序列"""
    for i, step in enumerate(seq):
        key, hold_ms, delay_ms = step
        log(f"  导航步骤 {i + 1}/{len(seq)} → [{key}]")
        if not nav_k(key, hold_ms, delay_ms, running_flag):
            log(f"  !!! 导航步骤 {i + 1} 中断")
            return False
    return True


def nav_blueprint_to_garage(running_flag) -> bool:
    """蓝图 → 车库"""
    return run_nav_seq(cfg.SEQ_MTG, running_flag)


def nav_garage_to_blueprint(running_flag) -> bool:
    """车库 → 蓝图"""
    return run_nav_seq(cfg.SEQ_GTM, running_flag)


def nav_freeroam_to_blueprint(running_flag) -> bool:
    """漫游界面 → 蓝图"""
    return run_nav_seq(cfg.SEQ_BTB, running_flag)


def nav_garage_to_myhorizon(running_flag) -> bool:
    """车库 → 我的地平线"""
    return run_nav_seq(cfg.SEQ_GTA, running_flag)


def nav_myhorizon_to_blueprint(running_flag) -> bool:
    """我的地平线 → 蓝图"""
    return run_nav_seq(cfg.SEQ_ATB, running_flag)
