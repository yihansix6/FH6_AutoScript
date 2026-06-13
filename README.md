# FH6 AutoScript

FH6 AutoScript 是一个 Windows 桌面自动化工具，基于 PyQt6 提供图形界面，通过后台窗口截图、OpenCV 模板匹配和 Windows 消息模拟按键/点击，自动完成游戏内重复流程。

> 项目面向《Forza Horizon 6》窗口标题和 `forzahorizon6.exe` 进程名设计。使用前请确认游戏窗口、分辨率和图片模板与当前环境匹配。

## 功能

| 功能 | 热键 | 说明 |
| --- | --- | --- |
| 买车加点 | `Ctrl+F1` | 自动购买车辆并分配车辆熟练度点数 |
| 移除车辆 | `Ctrl+F2` | 自动移除指定车辆 |
| 抽奖 | `Ctrl+F3` | 自动执行超级/普通抽奖流程 |
| 熟练度循环 | `Ctrl+F4` | 自动刷车辆熟练度 |
| 自动大循环 | `Ctrl+F5` | 组合熟练度、买车、删车、抽奖等流程，支持两种模式：仅刷点买车加点 / 包括删车和抽奖 |

## 环境要求

- Windows 10/11
- Python 3.9 或更高版本
- 游戏分辨率建议为 `1280x720`
- 建议以管理员权限运行，便于全局热键和后台按键稳定工作

## 安装

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

如果当前机器已经有可用 Python 环境，也可以直接执行：

```powershell
python -m pip install -r requirements.txt
```

## 运行

```powershell
python main.py
```

启动后点击“刷新窗口”，确认工具已经找到游戏窗口，再使用界面按钮或热键启动对应功能。

## 构建

项目提供了 `FH6_AutoScript.spec`，会自动把 `images/` 和 `assets/` 打包进可执行文件。

一键构建：

```powershell
.\build.bat
```

手动构建：

```powershell
python -m PyInstaller FH6_AutoScript.spec --clean --noconfirm
```

构建产物位于：

```text
dist/FH6_AutoScript.exe
```

> `build.bat` 会在构建完成后自动将 `images/` 文件夹复制到 `dist/images/`，确保 EXE 运行时能加载模板图片。

## 项目结构

```text
FH6_AutoScript/
├── main.py                  # 程序入口、QApplication 初始化、全局热键注册
├── build.bat                # 一键构建脚本（调用 PyInstaller 并复制 images/）
├── requirements.txt         # 运行和构建依赖
├── FH6_AutoScript.spec      # PyInstaller 构建配置
├── .gitignore               # Git 忽略规则
├── assets/                  # 图标等静态资源
│   └── FH6.ico
├── images/                  # OpenCV 模板匹配图片
├── core/
│   ├── config.py            # 热键、流程延时、图片路径和导航序列
│   ├── game_utils.py        # 窗口查找、后台截图、按键、识图工具
│   └── signals.py           # PyQt 线程安全信号
├── modules/
│   ├── award.py             # 抽奖流程
│   ├── auto_cycle.py        # 自动大循环
│   ├── buy_car.py           # 买车加点流程
│   ├── delete_car.py        # 移除车辆流程
│   ├── mastery.py           # 熟练度循环
│   └── navigation.py        # 游戏菜单导航序列
└── ui/
    ├── main_window.py       # 主窗口和交互逻辑
    ├── styles.py            # QSS 样式（深色主题）
    └── widgets.py           # 自定义控件
```

## 配置

主要配置集中在 `core/config.py`：

- 热键：`HOT_BUYCAR`、`HOT_DELCAR`、`HOT_GETAWARD`、`HOT_MASTERY`、`HOT_AUTO`
- 延时参数：如 `BC_INIT_WAIT`、`DC_MENU_ENTER`、`MA_DRIVE_MS`
- 自动循环次数：如 `AUTO_MASTERY_LOOPS`、`AUTO_BUYCAR_TIMES`
- 图片模板路径：如 `IMG_BUY_CAR`、`IMG_AWARD_ENTER`
- 菜单导航序列：如 `SEQ_MTG`、`SEQ_GTM`

图片识别对分辨率、UI 缩放和游戏语言较敏感。如果识别失败，请重新截取对应 UI 元素并替换 `images/` 下的模板图片。

## 注意事项

- 工具会向游戏窗口发送后台按键/鼠标消息，运行前请确认当前游戏页面与功能要求一致。
- 各功能需在特定游戏页面启动：

| 功能 | 启动页面 |
| --- | --- |
| 买车加点 (`Ctrl+F1`) | 购买与出售 |
| 移除车辆 (`Ctrl+F2`) | 车辆 |
| 抽奖 (`Ctrl+F3`) | 我的地平线 |
| 熟练度循环 (`Ctrl+F4`) | 开始竞赛赛事 |
| 自动大循环 (`Ctrl+F5`) | 漫游模式 |

- 自动大循环支持两种模式：**仅刷点买车加点** 和 **包括删车和抽奖**，可在界面中切换。
- 自动流程运行中可以再次点击按钮或使用对应热键停止。
- 如果长时间无法识别图片，请检查游戏窗口是否已启动、分辨率是否一致、模板图片是否过期。
- 打包后的可执行文件仍依赖 Windows 图形环境和游戏窗口，不建议在无桌面会话中运行。

## 开发检查

```powershell
python -m compileall -q .
python -m PyInstaller FH6_AutoScript.spec --clean --noconfirm
```
