# -*- coding: utf-8 -*-
"""
FH6 AutoScript - 游戏工具模块
窗口查找、后台发键、像素检测、图像搜索（cv2 后台识图，不影响前台）
"""

import ctypes
import ctypes.wintypes
import time
import cv2
import numpy as np
import win32gui
import win32con
import win32api
import win32ui
import win32process
import subprocess


# ── 全局状态 ──
game_hwnd = 0
_log_callback = None


def set_log_callback(cb):
    """设置日志回调函数"""
    global _log_callback
    _log_callback = cb


def log(msg: str):
    """通过回调输出日志"""
    if _log_callback:
        _log_callback(msg)
    else:
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")


# ══════════════════════════════════════════════════════════════
#  窗口查找
# ══════════════════════════════════════════════════════════════

def find_game() -> int:
    """查找游戏窗口句柄"""
    global game_hwnd
    game_hwnd = 0

    def _get_process_name(hwnd):
        """通过窗口句柄获取所属进程名"""
        handle = None
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid:
                handle = win32api.OpenProcess(
                    win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                    False,
                    pid,
                )
                if handle:
                    return win32process.GetModuleFileNameEx(handle, 0)
        except Exception:
            pass
        finally:
            if handle:
                win32api.CloseHandle(handle)
        return ""

    def enum_callback(hwnd, _):
        global game_hwnd
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "Forza Horizon 6" in title:
                proc_name = _get_process_name(hwnd)
                if 'forzahorizon6' in proc_name.lower():
                    game_hwnd = hwnd
                    return False
        return True

    win32gui.EnumWindows(enum_callback, None)

    if not game_hwnd:
        try:
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq forzahorizon6.exe', '/FO', 'CSV', '/NH'],
                capture_output=True,
                text=True,
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            )
            if any(line.strip().startswith('"forzahorizon6.exe"') for line in result.stdout.lower().splitlines()):
                def enum2(hwnd, _):
                    global game_hwnd
                    if not win32gui.IsWindowVisible(hwnd):
                        return True
                    proc_name = _get_process_name(hwnd)
                    if 'forzahorizon6' in proc_name.lower():
                        game_hwnd = hwnd
                        return False
                    return True
                win32gui.EnumWindows(enum2, None)
        except Exception:
            pass

    return game_hwnd


# ══════════════════════════════════════════════════════════════
#  后台发键（PostMessage）
# ══════════════════════════════════════════════════════════════

# 虚拟键码映射
_VK_MAP = {
    "Enter": 0x0D, "Esc": 0x1B, "BackSpace": 0x08,
    "Up": 0x26, "Down": 0x28, "Left": 0x25, "Right": 0x27,
    "PgDn": 0x22, "PgUp": 0x21, "Tab": 0x09, "Space": 0x20,
    "W": 0x57, "X": 0x58, "Y": 0x59, "A": 0x41, "S": 0x53, "D": 0x44,
    "w": 0x57, "x": 0x58, "y": 0x59, "a": 0x41, "s": 0x53, "d": 0x44,
}


def _parse_key(keys: str) -> tuple:
    """解析按键字符串，返回 (vk, is_down, is_up)"""
    key = keys.strip("{}").strip()
    is_down = key.endswith(" down")
    is_up = key.endswith(" up")
    if is_down:
        key = key[:-5]
    elif is_up:
        key = key[:-3]
    vk = _VK_MAP.get(key, 0)
    if vk == 0 and len(key) == 1:
        vk = ord(key[0])
    return vk, is_down, is_up


def gsend(keys: str) -> bool:
    """后台发送按键到游戏窗口（PostMessage）"""
    global game_hwnd
    if not game_hwnd:
        find_game()
    if not game_hwnd:
        log("  !! 未找到游戏窗口，跳过发键")
        return False

    vk, is_down, is_up = _parse_key(keys)
    if vk == 0:
        log(f"  !! 未知按键: {keys}")
        return False

    if is_down:
        win32api.PostMessage(game_hwnd, win32con.WM_KEYDOWN, vk, 0)
    elif is_up:
        win32api.PostMessage(game_hwnd, win32con.WM_KEYUP, vk, 0)
    else:
        win32api.PostMessage(game_hwnd, win32con.WM_KEYDOWN, vk, 0)
        time.sleep(0.03)
        win32api.PostMessage(game_hwnd, win32con.WM_KEYUP, vk, 0)
    return True


# ══════════════════════════════════════════════════════════════
#  后台截图（PrintWindow - 不受遮挡/最小化影响）
# ══════════════════════════════════════════════════════════════

def _capture_window_bgr(hwnd: int) -> np.ndarray | None:
    """
    通过 PrintWindow 截取窗口客户区内容，返回 BGR 格式的 numpy 数组。
    完全后台操作，不影响前台。
    """
    hwnd_dc = None
    mfc_dc = None
    save_dc = None
    bitmap = None
    try:
        rect = win32gui.GetClientRect(hwnd)
        w = rect[2] - rect[0]
        h = rect[3] - rect[1]
        if w <= 0 or h <= 0:
            return None

        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()

        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mfc_dc, w, h)
        save_dc.SelectObject(bitmap)

        # PW_RENDERFULLCONTENT = 2，捕获完整窗口内容（不受遮挡）
        result = ctypes.windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 2)
        if result == 0:
            # 回退到 PW_CLIENTONLY = 1
            ctypes.windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 1)

        bmp_info = bitmap.GetInfo()
        bmp_bits = bitmap.GetBitmapBits(True)

        img = np.frombuffer(bmp_bits, dtype=np.uint8).reshape((h, w, 4))
        # BGRA → BGR
        img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        return img_bgr
    except Exception as e:
        log(f"  !! 截图失败: {e}")
        return None
    finally:
        if bitmap is not None:
            try:
                win32gui.DeleteObject(bitmap.GetHandle())
            except Exception:
                pass
        if save_dc is not None:
            try:
                save_dc.DeleteDC()
            except Exception:
                pass
        if mfc_dc is not None:
            try:
                mfc_dc.DeleteDC()
            except Exception:
                pass
        if hwnd_dc is not None:
            try:
                win32gui.ReleaseDC(hwnd, hwnd_dc)
            except Exception:
                pass


def _capture_window_client(hwnd: int) -> np.ndarray | None:
    """
    通过 PrintWindow 截取窗口客户区（与 _capture_window_bgr 相同，别名）。
    """
    return _capture_window_bgr(hwnd)


# ══════════════════════════════════════════════════════════════
#  像素颜色检测（PrintWindow 取像素，不受遮挡）
# ══════════════════════════════════════════════════════════════

def get_window_pixel_color(hwnd: int, x: int, y: int) -> int:
    """
    通过 PrintWindow 获取窗口客户区 (x, y) 像素的 RGB 颜色值。
    返回 0xRRGGBB 格式整数。
    """
    hdc = None
    hmdc = None
    hbmp = None
    old_bmp = None
    try:
        hdc = ctypes.windll.user32.GetDC(hwnd)
        hmdc = ctypes.windll.gdi32.CreateCompatibleDC(hdc)
        rc = ctypes.wintypes.RECT()
        ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(rc))
        w = rc.right - rc.left
        h = rc.bottom - rc.top
        if w <= 0 or h <= 0:
            return 0

        hbmp = ctypes.windll.gdi32.CreateCompatibleBitmap(hdc, w, h)
        old_bmp = ctypes.windll.gdi32.SelectObject(hmdc, hbmp)
        ctypes.windll.user32.PrintWindow(hwnd, hmdc, 2)
        col = ctypes.windll.gdi32.GetPixel(hmdc, x, y)
        return col
    except Exception:
        return 0
    finally:
        if hmdc and old_bmp:
            ctypes.windll.gdi32.SelectObject(hmdc, old_bmp)
        if hbmp:
            ctypes.windll.gdi32.DeleteObject(hbmp)
        if hmdc:
            ctypes.windll.gdi32.DeleteDC(hmdc)
        if hdc:
            ctypes.windll.user32.ReleaseDC(hwnd, hdc)


# ══════════════════════════════════════════════════════════════
#  FindImage() - 后台识图（cv2 模板匹配）
# ══════════════════════════════════════════════════════════════

def find_image(img_path: str, hwnd: int = None, threshold: float = 0.9) -> tuple | None:
    """
    通过 PrintWindow 后台截图 + cv2 模板匹配，在游戏窗口中查找图片位置。
    全程后台操作，不影响前台鼠标键盘。

    参数:
        img_path:   模板图片路径
        hwnd:       窗口句柄（默认使用全局 game_hwnd）
        threshold:  匹配阈值 (0.0~1.0)，默认 0.9

    返回:
        (x, y, w, h) 在客户区中的位置和大小，未找到返回 None
    """
    if hwnd is None:
        hwnd = game_hwnd
    if not hwnd:
        return None

    template = cv2.imread(img_path, cv2.IMREAD_COLOR)
    if template is None:
        log(f"  !! 无法加载图片: {img_path}")
        return None

    screen_bgr = _capture_window_bgr(hwnd)
    if screen_bgr is None:
        return None

    th, tw = template.shape[:2]
    sh, sw = screen_bgr.shape[:2]
    if th > sh or tw > sw:
        log(f"  !! 模板({tw}x{th})大于窗口({sw}x{sh})")
        return None

    result = cv2.matchTemplate(screen_bgr, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        return (max_loc[0], max_loc[1], tw, th)
    return None


# ══════════════════════════════════════════════════════════════
#  FindAndClickImage() - 后台识图+点击
# ══════════════════════════════════════════════════════════════

def find_and_click_image(img_path: str, hwnd: int = None, threshold: float = 0.9) -> bool:
    """
    通过 PrintWindow 后台截图 + cv2 模板匹配，找到图片后通过 SendMessage
    模拟鼠标点击（WM_MOUSEMOVE + WM_LBUTTONDOWN + WM_LBUTTONUP）。
    全程后台操作，不影响前台鼠标。

    参数:
        img_path:   模板图片路径
        hwnd:       窗口句柄（默认使用全局 game_hwnd）
        threshold:  匹配阈值 (0.0~1.0)，默认 0.9

    返回:
        True 如果找到并点击成功，否则 False
    """
    loc = find_image(img_path, hwnd, threshold)
    if loc is None:
        return False

    if hwnd is None:
        hwnd = game_hwnd
    x, y, w, h = loc
    # 点击中心点
    cx = x + w // 2
    cy = y + h // 2

    lparam = (cy << 16) | cx

    # 使用 SendMessage 替代 PostMessage：游戏通常不响应 PostMessage 的鼠标消息
    ctypes.windll.user32.SendMessageW(hwnd, win32con.WM_MOUSEMOVE, 0, lparam)
    time.sleep(0.02)
    ctypes.windll.user32.SendMessageW(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
    time.sleep(0.05)
    ctypes.windll.user32.SendMessageW(hwnd, win32con.WM_LBUTTONUP, 0, lparam)

    log(f"  ✓ 找到并点击图片 ({img_path}) 位置=({cx},{cy})")
    return True


# ══════════════════════════════════════════════════════════════
#  辅助函数
# ══════════════════════════════════════════════════════════════

def safe_sleep(ms: int, running_flag) -> bool:
    """可中断的 sleep，返回 True=正常完成，False=被中断"""
    elapsed = 0
    while elapsed < ms:
        if not running_flag():
            return False
        chunk = min(30, ms - elapsed)
        time.sleep(chunk / 1000.0)
        elapsed += chunk
    return True


def press(key: str, hold_ms: int, after_ms: int, running_flag) -> bool:
    """按下按键 hold_ms 毫秒，等待 after_ms 毫秒"""
    if not running_flag():
        return False
    log(f"  {key}  按住 {hold_ms}ms  后等 {after_ms}ms")

    gsend("{" + key + " down}")
    if not safe_sleep(hold_ms, running_flag):
        return False
    gsend("{" + key + " up}")
    if after_ms > 0:
        return safe_sleep(after_ms, running_flag)
    return True


def poll_image(img_path: str, timeout_s: float, interval_ms: int, running_flag) -> bool:
    """轮询检测图片是否存在，超时返回 False"""
    elapsed = 0
    while elapsed < timeout_s * 1000:
        if not running_flag():
            return False
        if find_image(img_path):
            return True
        if not safe_sleep(interval_ms, running_flag):
            return False
        elapsed += interval_ms
    return False


def interrupt_sleep(ms: int, running_flag, countdown_callback=None) -> bool:
    """可中断的 sleep，定期更新倒计时"""
    deadline = int(time.time() * 1000) + ms
    while True:
        if not running_flag():
            return False
        if int(time.time() * 1000) >= deadline:
            break
        remaining = max(0, (deadline - int(time.time() * 1000)) // 1000)
        if countdown_callback:
            countdown_callback(f"{remaining}s")
        time.sleep(0.1)
    return running_flag()


def wait_bottom_left_not_black(running_flag) -> bool:
    """等待购买完成（底部中央像素不再是黑色）"""
    global game_hwnd
    while True:
        if not running_flag():
            return False
        try:
            rect = win32gui.GetClientRect(game_hwnd)
            cw = rect[2] - rect[0]
            ch = rect[3] - rect[1]
        except:
            return True

        all_black = True
        for i in range(5):
            sx = (cw // 2) - 40 + i * 20
            sy = ch - 1
            col = get_window_pixel_color(game_hwnd, sx, sy)
            if (col & 0xFFFFFF) > 0x0A0A0A:
                all_black = False
                break

        if not all_black:
            log("  ✓ 购车完成，继续流程")
            time.sleep(0.2)
            return True
        log("  × 尚未购车完成，等待 500ms")
        time.sleep(0.5)


def navigate_to_brand(running_flag) -> bool:
    """品牌导航（公用）"""
    brand_order = "pinyin"
    log(f"--- 品牌导航 [{'拼音排序' if brand_order == 'pinyin' else '非拼音排序'}] ---")

    if brand_order == "pinyin":
        for _ in range(3):
            if not press("Right", 80, 150, running_flag):
                return False
        for _ in range(2):
            if not press("Up", 80, 150, running_flag):
                return False
    else:
        if not press("Right", 80, 150, running_flag):
            return False
        for _ in range(7):
            if not press("Up", 80, 150, running_flag):
                return False
    return True
