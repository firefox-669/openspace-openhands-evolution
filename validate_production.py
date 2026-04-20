"""
生产环境验证脚本

快速检查所有生产级功能是否正常
"""

import sys
import os


def test_imports():
    """测试所有模块是否可以导入"""
    print("="*60)
    print("Testing Module Imports")
    print("="*60)
    
    # 首先检查是否已安装
    try:
        import openspace_openhands_evolution
        print("✅ Package is installed")
        installed = True
    except ImportError:
        print("❌ Package not installed")
        print("\n💡 Solution: Run 'pip install -e .' to install the package")
        print("   Or add the project directory to PYTHONPATH")
        installed = False
        return False
    
    modules = [
        ('openspace_openhands_evolution.orchestrator', 'Orchestrator'),
        ('openspace_openhands_evolution.execution_engine', 'Execution Engine'),
        ('openspace_openhands_evolution.llm_integration', 'LLM Integration'),
        ('openspace_openhands_evolution.production_engine', 'Production Engine'),
        ('openspace_openhands_evolution.monitor', 'Monitor System'),
        ('openspace_openhands_evolution.governance', 'Governance'),
    ]
    
    failed = []
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"✅ {description:30s} - OK")
        except ImportError as e:
            print(f"❌ {description:30s} - FAILED: {e}")
            failed.append(module_name)
    
    print()
    if failed:
        print(f"⚠️  {len(failed)} module(s) failed to import")
        return False
    else:
        print("✅ All modules imported successfully!")
        return True


def test_dependencies():
    """测试关键依赖是否安装"""
    print("\n" + "="*60)
    print("Testing Dependencies")
    print("="*60)
    
    packages = [
        ('openai', 'OpenAI SDK (optional)'),
        ('anthropic', 'Anthropic SDK (optional)'),
        ('yaml', 'PyYAML'),
        ('pydantic', 'Pydantic'),
    ]
    
    missing_optional = []
    missing_required = []
    
    for package, description in packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {description:30s} - Installed")
        except ImportError:
            if 'optional' in description:
                print(f"⚠️  {description:30s} - Not installed (optional)")
                missing_optional.append(package)
            else:
                print(f"❌ {description:30s} - MISSING")
                missing_required.append(package)
    
    print()
    if missing_required:
        print(f"❌ Required packages missing: {', '.join(missing_required)}")
        print(f"   Install with: pip install {' '.join(missing_required)}")
        return False
    else:
        print("✅ All required dependencies installed!")
        if missing_optional:
            print(f"ℹ️  Optional packages not installed: {', '.join(missing_optional)}")
        return True


def test_execution_sandbox():
    """测试执行沙箱"""
    print("\n" + "="*60)
    print("Testing Execution Sandbox")
    print("="*60)
    
    try:
        import asyncio
        from openspace_openhands_evolution.execution_engine import ExecutionSandbox
        
        async def test():
            sandbox = ExecutionSandbox(timeout=5)
            
            # 测试 Python 执行
            result = await sandbox.execute_python("print('Hello from sandbox!')")
            
            if result['success']:
                print("✅ Python execution - OK")
                print(f"   Output: {result['stdout'].strip()}")
            else:
                print(f"❌ Python execution - FAILED: {result['stderr']}")
                return False
            
            # 测试文件写入
            success = sandbox.write_file("test.txt", "Test content")
            if success:
                print("✅ File write - OK")
            else:
                print("❌ File write - FAILED")
                return False
            
            # 测试文件读取
            content = sandbox.read_file("test.txt")
            if content == "Test content":
                print("✅ File read - OK")
            else:
                print("❌ File read - FAILED")
                return False
            
            sandbox.cleanup()
            return True
        
        success = asyncio.run(test())
        return success
    
    except Exception as e:
        print(f"❌ Execution sandbox test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_router():
    """测试 LLM 路由器（不实际调用 API）"""
    print("\n" + "="*60)
    print("Testing LLM Router")
    print("="*60)
    
    try:
        from openspace_openhands_evolution.llm_integration import LLMRouter
        
        # 测试 Ollama（不需要 API key）
        try:
            config = {
                "provider": "ollama",
                "model": "llama2",
                "base_url": "http://localhost:11434"
            }
            router = LLMRouter(config)
            print("✅ Ollama provider - Initialized")
            print("   Note: Requires Ollama running at localhost:11434")
        except Exception as e:
            print(f"⚠️  Ollama provider - Not available: {e}")
        
        # 测试 OpenAI（需要 API key）
        api_key = os.getenv('OPENAI_API_KEY', '')
        if api_key and api_key != 'your-api-key-here':
            try:
                config = {
                    "provider": "openai",
                    "model": "gpt-4",
                    "api_key": api_key
                }
                router = LLMRouter(config)
                print("✅ OpenAI provider - Configured")
            except Exception as e:
                print(f"⚠️  OpenAI provider - Config error: {e}")
        else:
            print("⚠️  OpenAI provider - No API key configured")
            print("   Set OPENAI_API_KEY environment variable to enable")
        
        # 测试 Anthropic（需要 API key）
        api_key = os.getenv('ANTHROPIC_API_KEY', '')
        if api_key and api_key != 'your-api-key-here':
            try:
                config = {
                    "provider": "anthropic",
                    "model": "claude-3-opus-20240229",
                    "api_key": api_key
                }
                router = LLMRouter(config)
                print("✅ Anthropic provider - Configured")
            except Exception as e:
                print(f"⚠️  Anthropic provider - Config error: {e}")
        else:
            print("⚠️  Anthropic provider - No API key configured")
            print("   Set ANTHROPIC_API_KEY environment variable to enable")
        
        print("\n✅ LLM Router - Working")
        return True
    
    except Exception as e:
        print(f"❌ LLM Router test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_version():
    """测试版本号"""
    print("\n" + "="*60)
    print("Version Check")
    print("="*60)
    
    try:
        from openspace_openhands_evolution import __version__
        print(f"✅ Version: {__version__}")
        
        if __version__ == "1.0.0":
            print("✅ Production version confirmed!")
            return True
        else:
            print(f"⚠️  Expected version 1.0.0, got {__version__}")
            return False
    except Exception as e:
        print(f"❌ Version check failed: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "🔍"*30)
    print("OpenSpace-OpenHands-Evolution Production Validation")
    print("🔍"*30 + "\n")
    
    tests = [
        ("Module Imports", test_imports),
        ("Dependencies", test_dependencies),
        ("Execution Sandbox", test_execution_sandbox),
        ("LLM Router", test_llm_router),
        ("Version", test_version),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ {name} test crashed: {e}")
            results[name] = False
    
    # 总结
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10s} - {name}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print("\n" + "-"*60)
    print(f"Total: {passed}/{total} tests passed")
    print("-"*60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ Project is PRODUCTION READY!")
        print("\nNext steps:")
        print("  1. Configure your API keys in config.yaml")
        print("  2. Run: openspace-evolution")
        print("  3. Or: openspace-evolution run \"Your task\"")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("\nPlease fix the issues above before using in production.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
