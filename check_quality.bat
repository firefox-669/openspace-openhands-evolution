@echo off
REM 代码质量检查

echo ========================================
echo Code Quality Check
echo ========================================
echo.

REM 安装工具
pip install black flake8 mypy -q

REM 1. 代码格式化检查
echo [1/3] Checking code formatting with Black...
black --check openspace_openhands_evolution/ tests/
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Code formatting issues found!
    echo Run 'black openspace_openhands_evolution/ tests/' to fix
    echo.
) else (
    echo ✅ Code formatting OK
    echo.
)

REM 2. 代码风格检查
echo [2/3] Checking code style with Flake8...
flake8 openspace_openhands_evolution/ tests/ --max-line-length=100 --ignore=E501,W503
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Code style issues found!
    echo.
) else (
    echo ✅ Code style OK
    echo.
)

REM 3. 类型检查
echo [3/3] Checking type hints with MyPy...
mypy openspace_openhands_evolution/ --ignore-missing-imports
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Type hint issues found!
    echo.
) else (
    echo ✅ Type hints OK
    echo.
)

echo ========================================
echo Quality Check Complete
echo ========================================
echo.

pause
