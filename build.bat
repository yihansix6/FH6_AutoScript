@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ========================================
echo   FH6 AutoScript - Build
echo ========================================
echo.

echo [1/4] Cleaning old build...
if exist "build\" rd /s /q "build"
if exist "dist\"  rd /s /q "dist"

echo [2/4] Building...
python -m PyInstaller FH6_AutoScript.spec --clean --noconfirm

echo.
if %errorlevel% neq 0 (
    echo Build FAILED! Error code: %errorlevel%
    goto :end
)

echo [3/4] Copying images folder...
xcopy "images" "dist\images\" /E /I /Y >nul

echo [4/4] Build SUCCESS!
for %%A in ("dist\FH6_AutoScript.exe") do echo   Output: %%~fA (%%~zA bytes)

:end
echo.
pause