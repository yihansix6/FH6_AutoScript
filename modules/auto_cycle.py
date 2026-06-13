# -*- coding: utf-8 -*-
"""
FH6 AutoScript - 自动大循环模块 (Ctrl+F5)
两种模式：
  仅刷点买车加点：熟练度 → 蓝图→车库 → 买车加点 → 车库→蓝图 → 循环
  包括删车和抽奖：熟练度 → 蓝图→车库 → 买车加点 → 删车 → 抽奖 → 蓝图 → 循环
"""

import time
import core.config as cfg
from core.game_utils import gsend, log, press, safe_sleep, poll_image, navigate_to_brand, find_and_click_image
from modules.navigation import (
    nav_blueprint_to_garage, nav_garage_to_blueprint, nav_freeroam_to_blueprint, nav_garage_to_myhorizon, nav_myhorizon_to_blueprint
)
from modules.mastery import run_mastery_body
from modules.buy_car import run_buy_car_body
from modules.delete_car import run_delete_car_body
from modules.award import run_award_body

def run_auto_big_loop_contain(
    running_flag,
    max_cycles=0,
    mastery_loops=None,
    buycar_times=None,
    delcar_times=None,
    award_times=None,
    mastery_phase_callback=None,
    mastery_countdown_callback=None,
    auto_phase_callback=None,
    auto_cycle_callback=None,
    b_status_callback=None,
    bc_status_callback=None,
    dc_status_callback=None,
    aw_status_callback=None,
    b_loop_count_callback=None,
    bc_progress_callback=None,
    dc_progress_callback=None,
    aw_progress_callback=None,
    b_progress_callback=None,
    b_timer_start_callback=None,
    b_timer_stop_callback=None,
    efficiency_update_callback=None,
    bc_timer_start_callback=None,
    bc_timer_stop_callback=None,
    dc_timer_start_callback=None,
    dc_timer_stop_callback=None,
    aw_timer_start_callback=None,
    aw_timer_stop_callback=None,
):
    """自动大循环主函数包括删车和抽奖（max_cycles=0 表示无限循环）"""
    if mastery_loops is None:
        mastery_loops = cfg.AUTO_MASTERY_LOOPS
    if buycar_times is None:
        buycar_times = cfg.AUTO_BUYCAR_TIMES
    if delcar_times is None:
        delcar_times = cfg.AUTO_DELCAR_TIMES
    if award_times is None:
        award_times = cfg.AUTO_AWARD_TIMES
    cycle = 0

    # Phase 0: 漫游界面 → 蓝图
    log(">>> Phase 0: 导航 漫游界面→蓝图")
    if auto_phase_callback:
        auto_phase_callback("导航: 漫游界面→蓝图")
    ok = nav_freeroam_to_blueprint(running_flag)
    if not ok:
        _cleanup()
        return False
    log("✓ 导航完成 漫游界面→蓝图")

    while running_flag():
        if max_cycles > 0 and cycle >= max_cycles:
            log(f"已达到手动次数上限 {max_cycles}，停止循环")
            break
        cycle += 1
        if auto_cycle_callback:
            auto_cycle_callback(cycle)
        log(f"╔══ 自动大循环 第 {cycle} 轮开始 ══╗")

        if cycle > 1:
            if auto_phase_callback:
                auto_phase_callback("等待蓝图页面稳定...")
            log("  等待蓝图页面稳定 5s（防止首圈打空）")
            time.sleep(5)
            if not running_flag():
                break

        # Phase 1: 刷熟练度
        log(f">>> Phase 1: 刷熟练度 {mastery_loops} 轮")
        if b_status_callback:
            b_status_callback("▶ 后台运行", "#00FF88")
        if b_timer_start_callback:
            b_timer_start_callback()

        b_loop_count = 0
        while running_flag() and b_loop_count < mastery_loops:
            b_loop_count += 1
            if b_loop_count_callback:
                b_loop_count_callback(b_loop_count)
            if b_progress_callback:
                b_progress_callback(b_loop_count, mastery_loops)
            if auto_phase_callback:
                auto_phase_callback(f"刷熟练度 {b_loop_count}/{mastery_loops}")
            log(f"── [自动] 熟练度第 {b_loop_count}/{mastery_loops} 轮 ──")
            if not run_mastery_body(running_flag, mastery_phase_callback, mastery_countdown_callback):
                log("  !!! 熟练度中断")
                break
            if efficiency_update_callback:
                efficiency_update_callback(b_loop_count, cfg.POINTS_PER_LOOP)

        if b_timer_stop_callback:
            b_timer_stop_callback()

        _cleanup()
        if mastery_phase_callback:
            mastery_phase_callback("—")
        if mastery_countdown_callback:
            mastery_countdown_callback("—")
        if b_status_callback:
            b_status_callback("■ 待机", "#888888")

        if not running_flag():
            break
        if b_loop_count < mastery_loops:
            log("!!! 熟练度未完成，自动大循环中止")
            break
        log(f"✓ 熟练度完成 {mastery_loops} 轮")

        # Phase 2: 蓝图 → 车库
        log(">>> Phase 2: 导航 蓝图→车库")
        if auto_phase_callback:
            auto_phase_callback("导航: 蓝图→车库")
        ok = nav_blueprint_to_garage(running_flag)
        if not ok or not running_flag():
            break
        log("✓ 导航完成 蓝图→车库")

        # Phase 3: 买车 + 加点
        log(f">>> Phase 3: 买车加点 {buycar_times} 次")
        if bc_status_callback:
            bc_status_callback("▶ 后台运行", "#00FF88")
        if bc_timer_start_callback:
            bc_timer_start_callback()

        bc_loop_count = 0
        for i in range(buycar_times):
            if not running_flag():
                break
            bc_loop_count = i + 1
            if bc_progress_callback:
                bc_progress_callback(bc_loop_count, buycar_times)
            if auto_phase_callback:
                auto_phase_callback(f"买车加点 {bc_loop_count}/{buycar_times}")
            log(f"=== [自动] 买车第 {bc_loop_count}/{buycar_times} 次 ===")
            if not run_buy_car_body(running_flag):
                log("!!! 买车中断")
                break
            log(f"=== [自动] 买车第 {bc_loop_count} 次完成 ===")

        if bc_timer_stop_callback:
            bc_timer_stop_callback()
        done = bc_loop_count >= buycar_times
        if bc_status_callback:
            bc_status_callback("■ 待机", "#888888")
        if bc_progress_callback:
            bc_progress_callback(bc_loop_count, buycar_times)

        if not running_flag():
            break
        if not done:
            log("!!! 买车未完成，自动大循环中止")
            break
        log(f"✓ 买车加点完成 {buycar_times} 次")

        # 前往我的车辆
        log(">>> 前往我的车辆")
        if not safe_sleep(1000, running_flag):
            break
        if not press("Right", 80, cfg.DC_INIT_WAIT, running_flag):
            break

        log("--- 导航至制造商 ---")
        if not safe_sleep(cfg.DC_INIT_WAIT, running_flag):
            break
        if not press("Up", 80, 80, running_flag):
            break
        if not press("Up", 80, 80, running_flag):
            break
        if not press("Up", 80, 80, running_flag):
            break
        if not press("Enter", 100, cfg.DC_MENU_ENTER, running_flag):
            break
        if not poll_image(cfg.IMG_MY_CAR, 5.0, 300, running_flag):
            log("  !! 超时未检测到我的车辆")
            break

        if not press("BackSpace", 100, 800, running_flag):
            break

        if not navigate_to_brand(running_flag):
            break
        if not press("Enter", 80, 1000, running_flag):
            break

        # Phase 4: 移除车辆
        log(f">>> Phase 4: 移除车辆 {delcar_times} 次")
        if dc_status_callback:
            dc_status_callback("▶ 后台运行", "#00FF88")
        if dc_timer_start_callback:
            dc_timer_start_callback()

        dc_loop_count = 0
        for i in range(delcar_times):
            if not running_flag():
                break
            dc_loop_count = i + 1
            if dc_progress_callback:
                dc_progress_callback(dc_loop_count, delcar_times)
            if auto_phase_callback:
                auto_phase_callback(f"移除车辆 {dc_loop_count}/{delcar_times}")
            log(f"=== [自动] 移除车辆第 {dc_loop_count}/{delcar_times} 次 ===")
            if not run_delete_car_body(running_flag):
                log("!!! 移除车辆中断")
                break
            log(f"=== [自动] 移除车辆第 {dc_loop_count} 次完成 ===")

        if not press("Esc", 80, cfg.DC_ESC_FINAL, running_flag):
            return

        if dc_timer_stop_callback:
            dc_timer_stop_callback()
        if dc_status_callback:
            dc_status_callback("■ 待机", "#888888")
        if dc_progress_callback:
            dc_progress_callback(dc_loop_count, delcar_times)

        if not running_flag():
            break
        if dc_loop_count < delcar_times:
            log("!!! 未检测到待移除的车辆，跳过此阶段")
        else:
            log(f"✓ 移除车辆完成 {delcar_times} 次")


        # Phase 5: 车库 → 我的地平线
        log(">>> Phase 5: 导航 车库→我的地平线")
        if auto_phase_callback:
            auto_phase_callback("导航: 车库→我的地平线")
        ok = nav_garage_to_myhorizon(running_flag)
        if not ok or not running_flag():
            break
        log("✓ 导航完成 车库→我的地平线")

        # Phase 6: 抽奖
        log(f">>> Phase 6: 抽奖 {award_times} 次")
        if aw_status_callback:
            aw_status_callback("▶ 后台运行", "#00FF88")
        if aw_timer_start_callback:
            aw_timer_start_callback()

        # 点击抽奖入口（首次需要）
        if find_and_click_image(cfg.IMG_AWARD_ENTER):
            log("  ✓ 点击抽奖入口")
            if not safe_sleep(300, running_flag):
                return
            aw_loop_count = 0
            for i in range(award_times):
                if not running_flag():
                    break
                aw_loop_count = i + 1
                if aw_progress_callback:
                    aw_progress_callback(aw_loop_count, award_times)
                if auto_phase_callback:
                    auto_phase_callback(f"抽奖 {aw_loop_count}/{award_times}")
                log(f"=== [自动] 抽奖第 {aw_loop_count}/{award_times} 次 ===")
                if not run_award_body(running_flag, is_last=(aw_loop_count == award_times)):
                    log("!!! 抽奖中断")
                    break
                log(f"=== [自动] 抽奖第 {aw_loop_count} 次完成 ===")
        else:
            log("!!! 未检测到抽奖入口，跳过此阶段")

        if aw_timer_stop_callback:
            aw_timer_stop_callback()
        if aw_status_callback:
            aw_status_callback("■ 待机", "#888888")
        if aw_progress_callback:
            aw_progress_callback(aw_loop_count, award_times)

        if not running_flag():
            break
        if aw_loop_count < award_times:
            log("!!! 抽奖未完成，请检查抽奖次数")
        else:
            log(f"✓ 抽奖完成 {award_times} 次")

        # 回到蓝图，准备下一轮
        if not safe_sleep(1000, running_flag):
            break
        log(">>> 导航 我的地平线→蓝图")
        if auto_phase_callback:
            auto_phase_callback("导航: 我的地平线→蓝图")
        ok = nav_myhorizon_to_blueprint(running_flag)
        if not ok or not running_flag():
            break
        log("✓ 导航完成 我的地平线→蓝图")


        log(f"╚══ 第 {cycle} 轮完成 ══╝")

    _cleanup()
    log(f"<<< 自动大循环 结束，共完成 {cycle} 轮")


def run_auto_big_loop(
    running_flag,
    max_cycles=0,
    mastery_loops=None,
    buycar_times=None,
    mastery_phase_callback=None,
    mastery_countdown_callback=None,
    auto_phase_callback=None,
    auto_cycle_callback=None,
    b_status_callback=None,
    bc_status_callback=None,
    b_loop_count_callback=None,
    bc_progress_callback=None,
    b_progress_callback=None,
    b_timer_start_callback=None,
    b_timer_stop_callback=None,
    efficiency_update_callback=None,
    bc_timer_start_callback=None,
    bc_timer_stop_callback=None,
):
    """自动大循环主函数（max_cycles=0 表示无限循环）"""
    if mastery_loops is None:
        mastery_loops = cfg.AUTO_MASTERY_LOOPS
    if buycar_times is None:
        buycar_times = cfg.AUTO_BUYCAR_TIMES
    cycle = 0

    # Phase 0: 漫游界面 → 蓝图
    log(">>> Phase 0: 导航 漫游界面→蓝图")
    if auto_phase_callback:
        auto_phase_callback("导航: 漫游界面→蓝图")
    ok = nav_freeroam_to_blueprint(running_flag)
    if not ok:
        _cleanup()
        return False
    log("✓ 导航完成 漫游界面→蓝图")

    while running_flag():
        if max_cycles > 0 and cycle >= max_cycles:
            log(f"已达到手动次数上限 {max_cycles}，停止循环")
            break
        cycle += 1
        if auto_cycle_callback:
            auto_cycle_callback(cycle)
        log(f"╔══ 自动大循环 第 {cycle} 轮开始 ══╗")

        if cycle > 1:
            if auto_phase_callback:
                auto_phase_callback("等待蓝图页面稳定...")
            log("  等待蓝图页面稳定 5s（防止首圈打空）")
            time.sleep(5)
            if not running_flag():
                break

        # Phase 1: 刷熟练度
        log(f">>> Phase 1: 刷熟练度 {mastery_loops} 轮")
        if b_status_callback:
            b_status_callback("▶ 后台运行", "#00FF88")
        if b_timer_start_callback:
            b_timer_start_callback()

        b_loop_count = 0
        while running_flag() and b_loop_count < mastery_loops:
            b_loop_count += 1
            if b_loop_count_callback:
                b_loop_count_callback(b_loop_count)
            if b_progress_callback:
                b_progress_callback(b_loop_count, mastery_loops)
            if auto_phase_callback:
                auto_phase_callback(f"刷熟练度 {b_loop_count}/{mastery_loops}")
            log(f"── [自动] 熟练度第 {b_loop_count}/{mastery_loops} 轮 ──")
            if not run_mastery_body(running_flag, mastery_phase_callback, mastery_countdown_callback):
                log("  !!! 熟练度中断")
                break
            if efficiency_update_callback:
                efficiency_update_callback(b_loop_count, cfg.POINTS_PER_LOOP)

        if b_timer_stop_callback:
            b_timer_stop_callback()

        _cleanup()
        if mastery_phase_callback:
            mastery_phase_callback("—")
        if mastery_countdown_callback:
            mastery_countdown_callback("—")
        if b_status_callback:
            b_status_callback("■ 待机", "#888888")

        if not running_flag():
            break
        if b_loop_count < mastery_loops:
            log("!!! 熟练度未完成，自动大循环中止")
            break
        log(f"✓ 熟练度完成 {mastery_loops} 轮")

        # Phase 2: 蓝图 → 车库
        log(">>> Phase 2: 导航 蓝图→车库")
        if auto_phase_callback:
            auto_phase_callback("导航: 蓝图→车库")
        ok = nav_blueprint_to_garage(running_flag)
        if not ok or not running_flag():
            break
        log("✓ 导航完成 蓝图→车库")

        # Phase 3: 买车 + 加点
        log(f">>> Phase 3: 买车加点 {buycar_times} 次")
        if bc_status_callback:
            bc_status_callback("▶ 后台运行", "#00FF88")
        if bc_timer_start_callback:
            bc_timer_start_callback()

        bc_loop_count = 0
        for i in range(buycar_times):
            if not running_flag():
                break
            bc_loop_count = i + 1
            if bc_progress_callback:
                bc_progress_callback(bc_loop_count, buycar_times)
            if auto_phase_callback:
                auto_phase_callback(f"买车加点 {bc_loop_count}/{buycar_times}")
            log(f"=== [自动] 买车第 {bc_loop_count}/{buycar_times} 次 ===")
            if not run_buy_car_body(running_flag):
                log("!!! 买车中断")
                break
            log(f"=== [自动] 买车第 {bc_loop_count} 次完成 ===")

        if bc_timer_stop_callback:
            bc_timer_stop_callback()
        done = bc_loop_count >= buycar_times
        if bc_status_callback:
            bc_status_callback("■ 待机", "#888888")
        if bc_progress_callback:
            bc_progress_callback(bc_loop_count, buycar_times)

        if not running_flag():
            break
        if not done:
            log("!!! 买车未完成，自动大循环中止")
            break
        log(f"✓ 买车加点完成 {buycar_times} 次")

        # Phase 4: 车库 → 蓝图
        log(">>> Phase 4: 导航 车库→蓝图")
        if auto_phase_callback:
            auto_phase_callback("导航: 车库→蓝图")
        ok = nav_garage_to_blueprint(running_flag)
        if not ok or not running_flag():
            break
        log("✓ 导航完成 车库→蓝图")

        log(f"╚══ 第 {cycle} 轮完成 ══╝")

    _cleanup()
    log(f"<<< 自动大循环 结束，共完成 {cycle} 轮")


def _cleanup():
    """全局清理：释放所有按键"""
    gsend("{w up}")
    gsend("{Enter up}")
    gsend("{x up}")