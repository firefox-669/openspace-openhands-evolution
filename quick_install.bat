@echo off
REM 快速安装和验证脚本

echo ========================================
echo OpenSpace-OpenHands-Evolution
echo Quick Install and Validate
echo ========================================
echo.

REM 1. 安装项目
echo [1/3] Installing package...
pip install -e . -q

if %errorlevel% neq 0 (
    echo.
    echo ❌ Installation failed!
    pause
    exit /b 1
)

echo ✅ Package installed
echo.

REM 2. 安装可选依赖
echo [2/3] Installing optional dependencies...
pip install openai anthropic -q
echo ✅ Optional dependencies installed (if available)
echo.

REM 3. 运行验证
echo [3/3] Running validation...
echo.
python validate_production.py

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Copy config.production.yaml to config.yaml
echo   2. Edit config.yaml and add your API keys
echo   3. Run: openspace-evolution
echo.

pause
