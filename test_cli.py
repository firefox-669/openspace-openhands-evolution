#!/usr/bin/env python3
"""
测试命令行工具是否正常工作
"""

import subprocess
import sys


def test_help():
    """测试 help 命令"""
    print("测试 1: openspace-evolution --help")
    result = subprocess.run(
        [sys.executable, "-m", "openspace_openhands_evolution", "--help"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and "OpenSpace-OpenHands-Evolution" in result.stdout:
        print("✅ PASS\n")
        return True
    else:
        print("❌ FAIL")
        print(result.stderr)
        return False


def test_version():
    """测试版本信息"""
    print("测试 2: 检查包版本")
    try:
        from openspace_openhands_evolution import __version__
        print(f"   版本: {__version__}")
        print("✅ PASS\n")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}\n")
        return False


def test_import():
    """测试导入"""
    print("测试 3: 导入核心模块")
    try:
        from openspace_openhands_evolution import (
            EvolutionOrchestrator,
            TaskRequest,
            TransferRequest,
            load_config
        )
        print("   ✅ EvolutionOrchestrator")
        print("   ✅ TaskRequest")
        print("   ✅ TransferRequest")
        print("   ✅ load_config")
        print("✅ PASS\n")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}\n")
        return False


def test_config():
    """测试配置加载"""
    print("测试 4: 配置加载")
    try:
        from openspace_openhands_evolution import load_config
        config = load_config()
        
        if 'openspace' in config and 'openhands' in config:
            print("   ✅ 配置结构正确")
            print(f"   - OpenSpace registry: {config['openspace']['registry_path']}")
            print(f"   - OpenHands model: {config['openhands']['model']}")
            print("✅ PASS\n")
            return True
        else:
            print("❌ FAIL: 配置结构错误\n")
            return False
    except Exception as e:
        print(f"❌ FAIL: {e}\n")
        return False


def main():
    """运行所有测试"""
    print("="*60)
    print("  🔧 OpenSpace-OpenHands-Evolution 测试")
    print("="*60)
    print()
    
    tests = [
        test_import,
        test_version,
        test_config,
        test_help,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ 测试异常: {e}\n")
            results.append(False)
    
    # 总结
    print("="*60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"  🎉 所有测试通过! ({passed}/{total})")
        print("="*60)
        print("\n✨ 项目已准备就绪！")
        print("\n现在可以使用:")
        print("  openspace-evolution                    # 交互模式")
        print("  openspace-evolution run \"创建 API\"     # 执行任务")
        print("  openspace-evolution status             # 查看状态")
        return 0
    else:
        print(f"  ⚠️  {passed}/{total} 个测试通过")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
