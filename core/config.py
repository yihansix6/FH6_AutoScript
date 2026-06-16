# -*- coding: utf-8 -*-
"""
FH6 AutoScript - 配置模块
所有可调参数集中管理
"""

import os
import sys

# ── 工作目录 ──
if getattr(sys, 'frozen', False):
    # 打包后：EXE 所在目录
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(SCRIPT_DIR, "images")

# ── 热键 ──
HOT_BUYCAR   = "Ctrl+F1"
HOT_DELCAR   = "Ctrl+F2"
HOT_GETAWARD = "Ctrl+F3"
HOT_MASTERY  = "Ctrl+F4"
HOT_AUTO     = "Ctrl+F5"

# ── 买车+加点 参数 ──
BC_INIT_WAIT    = 500
BC_MENU_ENTER   = 1000
BC_CONFIRM_WAIT = 3800
BC_PURCHASE_CFM = 1500
BC_AFTER_BUY    = 13000
BC_ESC_WAIT     = 1000
BC_SKILL_ENTER  = 1000
BC_SKILL_SETTLE = 1000
BC_SKILL_APPLY  = 1200
BC_ESC_FINAL    = 800
BC_ESC_FINAL2   = 1500

# ── 删车 参数 ──
DC_INIT_WAIT    = 500
DC_MENU_ENTER   = 1000
DC_ESC_FINAL    = 800

# ── 熟练度循环 参数 ──
MA_INIT_WAIT    = 3000
MA_DRIVE_MS     = 100000
MA_SETTLE_MS    = 4000
POINTS_PER_LOOP = 50

# ── 自动大循环配置 ──
AUTO_MASTERY_LOOPS = 21   # 每轮刷熟练度圈数
AUTO_BUYCAR_TIMES  = 33    # 每轮买车次数
AUTO_DELCAR_TIMES  = 33    # 每轮删车次数
AUTO_AWARD_TIMES   = 33    # 每轮抽奖次数
AUTO_CYCLE_COUNT   = 0     # 手动次数默认值（0 = 无限循环）

# ── 图片资源 ──
IMG_DEL_CAR        = os.path.join(IMAGES_DIR, "IMG_DEL_CAR.png")   # 待删除车辆
IMG_DEL_CONFIRM    = os.path.join(IMAGES_DIR, "IMG_DEL_CONFIRM.png")   # 待删除车辆性能
IMG_DEL_CHOICE     = os.path.join(IMAGES_DIR, "IMG_DEL_CHOICE.png")   # 待删除车辆确认选择
IMG_AWARD_ENTER    = os.path.join(IMAGES_DIR, "IMG_AWARD_ENTER.png")   # 超级抽奖入口
IMG_GENERAL_AWARD_ENTER    = os.path.join(IMAGES_DIR, "IMG_GENERAL_AWARD_ENTER.png")   # 普通抽奖入口
IMG_AWARD_CONTINUE = os.path.join(IMAGES_DIR, "IMG_AWARD_CONTINUE.png")   # 继续抽奖按钮
IMG_AWARD_SKIP     = os.path.join(IMAGES_DIR, "IMG_AWARD_SKIP.png")   # 跳过抽奖动画
IMG_AWARD_CAR     = os.path.join(IMAGES_DIR, "IMG_AWARD_CAR.png")   # 重复车辆
IMG_MY_CAR         = os.path.join(IMAGES_DIR, "IMG_MY_CAR.png")   # 我的车辆
IMG_BUY_CAR         = os.path.join(IMAGES_DIR, "IMG_BUY_CAR.png")   # 买车车辆
IMG_COLOR          = os.path.join(IMAGES_DIR, "IMG_COLOR.png")   # 车辆颜色
IMG_PHOTO          = os.path.join(IMAGES_DIR, "IMG_PHOTO.png")   # 拍照模式
IMG_CAR_TEC        = os.path.join(IMAGES_DIR, "IMG_CAR_TEC.png")   # 车辆熟练度
IMG_NOT_ENOUGH     = os.path.join(IMAGES_DIR, "IMG_NOT_ENOUGH.png")   # 熟练度不足

# ── 导航序列 ──
# 蓝图 → 车库
SEQ_MTG = [
    ["Down",  100,  150],
    ["Down",  100,  150],
    ["Down",  100,  150],
    ["Down",  100,  600],
    ["Enter", 100, 1000],
    ["Enter", 100, 18000],
    ["Esc",   100, 1500],
    ["PgDn",  100,  400],
    ["PgDn",  100, 1000],
    ["Enter", 100,  800],
    ["Enter", 100, 15000],
    ["Right", 100, 2000],
]

# 车库 → 蓝图
SEQ_GTM = [
    ["Esc",   100, 11000],
    ["Esc",   100, 1100],
    ["PgDn",  100,  150],
    ["PgDn",  100,  150],
    ["PgDn",  100,  150],
    ["PgDn",  100,  500],
    ["Enter", 100,  900],
    ["Enter", 100, 1000],
    ["PgDn",  100,  150],
    ["PgDn",  100,  150],
    ["PgDn",  100,  150],
    ["PgDn",  100,  150],
    ["PgDn",  100,  150],
    ["PgDn",  100,  150],
    ["PgDn",  100, 5000],
    ["Enter", 100, 7000],
    ["Enter", 100, 3000],
    ["Y",     100, 1000],
    ["Enter", 100, 1000],
    ["Esc",   100, 1000],
    ["Enter", 100, 15000],
]

# 漫游界面 → 蓝图
SEQ_BTB = [
    ["Esc",   100, 1100],
    ["PgDn",  100,  150],
    ["PgDn",  100,  150],
    ["PgDn",  100,  150],
    ["PgDn",  100,  500],
    ["Enter", 100,  900],
    ["Enter", 100, 1000],
    ["PgDn",  100,  150],
    ["PgDn",  100,  150],
    ["PgDn",  100,  150],
    ["PgDn",  100,  150],
    ["PgDn",  100,  150],
    ["PgDn",  100,  150],
    ["PgDn",  100, 5000],
    ["Enter", 100, 7000],
    ["Enter", 100, 3000],
    ["Y",     100, 1000],
    ["Enter", 100, 1000],
    ["Esc",   100, 1000],
    ["Enter", 100, 15000],
]

# 车库 → 我的地平线
SEQ_GTA = [
    ["Esc",   100, 11000],
    ["Esc",   100, 1100],
    ["PgDn",  100,  150],
    ["PgDn",  100,  150],
]

# 我的地平线 → 蓝图
SEQ_ATB = [
    ["PgDn",  100,  150],
    ["PgDn",  100,  500],
    ["Enter", 100,  900],
    ["Enter", 100, 1000],
    ["PgDn",  100,  150],
    ["PgDn",  100,  150],
    ["PgDn",  100,  150],
    ["PgDn",  100,  150],
    ["PgDn",  100,  150],
    ["PgDn",  100,  150],
    ["PgDn",  100, 5000],
    ["Enter", 100, 7000],
    ["Enter", 100, 3000],
    ["Y",     100, 1000],
    ["Enter", 100, 1000],
    ["Esc",   100, 1000],
    ["Enter", 100, 15000],
]