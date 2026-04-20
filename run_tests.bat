@echo off
REM 运行所有测试并生成覆盖率报告

echo ========================================
echo Running Tests with Coverage
echo ========================================
echo.

REM 安装测试依赖
pip install pytest pytest-asyncio coverage -q

REM 运行测试
echo Running tests...
pytest tests/ -v --cov=openspace_openhands_evolution --cov-report=term-missing --cov-report=html:htmlcov

echo.
echo ========================================
echo Test Summary
echo ========================================
echo.
echo Coverage report generated in htmlcov/ directory
echo Open htmlcov/index.html in browser to view detailed report
echo.

pause
