@echo off
chcp 65001 >nul
echo ============================================================
echo   🔧 OpenSpace-OpenHands-Evolution 安装和测试
echo ============================================================
echo.

echo [1/3] 安装包...
pip install -e .
if errorlevel 1 (
    echo ❌ 安装失败
    pause
    exit /b 1
)
echo ✅ 安装成功
echo.

echo [2/3] 运行测试...
python test_cli.py
if errorlevel 1 (
    echo.
    echo ⚠️  部分测试失败，但项目仍可使用
)
echo.

echo [3/3] 测试命令行工具...
python -m openspace_openhands_evolution --help
if errorlevel 1 (
    echo ❌ 命令行工具测试失败
    pause
    exit /b 1
)
echo.

echo ============================================================
echo   🎉 安装完成！
echo ============================================================
echo.
echo 现在可以使用以下命令:
echo.
echo   openspace-evolution                    # 交互模式
echo   openspace-evolution run "创建 API"     # 执行任务
echo   openspace-evolution status             # 查看状态
echo   openspace-evolution --help             # 显示帮助
echo.
echo 或者使用 Python 模块方式:
echo.
echo   python -m openspace_openhands_evolution
echo.
pause
