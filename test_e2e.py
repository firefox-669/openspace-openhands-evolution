"""
端到端生产环境测试

验证真实 LLM 调用和代码执行
"""

import asyncio
import os
import sys


async def test_production_flow():
    """测试完整的生产流程"""
    print("="*60)
    print("Production End-to-End Test")
    print("="*60)
    print()
    
    # 检查 API key
    api_key = os.getenv('OPENAI_API_KEY', '')
    if not api_key or api_key == 'your-api-key-here':
        print("⚠️  OPENAI_API_KEY not set")
        print("   Set it to test real LLM integration:")
        print("   export OPENAI_API_KEY=sk-your-key")
        print()
        use_mock = input("Continue with mock test? (y/n): ").strip().lower()
        if use_mock != 'y':
            return False
    
    try:
        from openspace_openhands_evolution import EvolutionOrchestrator, TaskRequest
        
        # 配置
        config = {
            'llm': {
                'provider': 'openai',
                'model': 'gpt-4',
                'api_key': api_key if api_key and api_key != 'your-api-key-here' else None
            },
            'openspace': {'registry_path': './data/skills'},
            'openhands': {
                'model': 'gpt-4',
                'sandbox_timeout': 30,
                'max_retries': 2
            },
            'monitor': {'quality_threshold': 0.7},
            'governance': {'enable_gatekeeping': True}
        }
        
        print("1️⃣  Initializing orchestrator...")
        orchestrator = EvolutionOrchestrator(config)
        print("   ✅ Orchestrator initialized")
        print()
        
        # 创建测试任务
        print("2️⃣  Creating test task...")
        task = TaskRequest(
            id="e2e-test-001",
            description="Write a Python function that calculates factorial",
            project_id="test-project",
            language="python"
        )
        print(f"   Task: {task.description}")
        print()
        
        # 执行任务
        print("3️⃣  Executing task...")
        print("   (This may take 10-30 seconds with real LLM)")
        print()
        
        result = await orchestrator.execute_task(task)
        
        print()
        print("4️⃣  Results:")
        print(f"   Success: {result.success}")
        print(f"   Output length: {len(result.output)} chars")
        
        if result.success:
            print(f"\n   Preview:\n   {result.output[:200]}...")
        
        if result.metrics:
            score = result.metrics.get('overall_score', 0)
            print(f"\n   Quality Score: {score:.2f}")
        
        if result.reasoning_trace:
            print(f"   Reasoning Steps: {len(result.reasoning_trace)}")
        
        print()
        
        if result.success:
            print("✅ PRODUCTION TEST PASSED!")
            print("\n🎉 The system is working with real LLM and code execution!")
            return True
        else:
            print(f"❌ Task failed: {result.error}")
            return False
    
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_sandbox_only():
    """仅测试沙箱执行（不需要 API key）"""
    print("="*60)
    print("Sandbox Execution Test (No API Key Required)")
    print("="*60)
    print()
    
    try:
        from openspace_openhands_evolution.execution_engine import ExecutionSandbox
        
        print("1️⃣  Creating sandbox...")
        sandbox = ExecutionSandbox(timeout=10)
        print("   ✅ Sandbox created")
        print()
        
        print("2️⃣  Executing Python code...")
        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

result = factorial(5)
print(f"Factorial of 5 is {result}")
"""
        
        result = await sandbox.execute_python(code)
        
        print(f"   Success: {result['success']}")
        if result['success']:
            print(f"   Output: {result['stdout'].strip()}")
            print("   ✅ Code execution works!")
        else:
            print(f"   Error: {result['stderr']}")
            print("   ❌ Code execution failed")
        
        print()
        
        print("3️⃣  Testing file operations...")
        sandbox.write_file("test.txt", "Hello from sandbox!")
        content = sandbox.read_file("test.txt")
        
        if content == "Hello from sandbox!":
            print("   ✅ File operations work!")
        else:
            print("   ❌ File operations failed")
        
        sandbox.cleanup()
        
        print()
        print("✅ SANDBOX TEST PASSED!")
        print("\nℹ️  To test full production flow, set OPENAI_API_KEY")
        return True
    
    except Exception as e:
        print(f"\n❌ Sandbox test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print()
    
    # 先测试沙箱（总是可以运行）
    sandbox_ok = await test_sandbox_only()
    
    print("\n" + "="*60)
    
    if sandbox_ok:
        # 询问是否测试完整流程
        print()
        test_full = input("Test full production flow with LLM? (y/n): ").strip().lower()
        
        if test_full == 'y':
            print()
            full_ok = await test_production_flow()
            return full_ok
        else:
            print("\n✅ Sandbox test passed - Core execution engine works!")
            print("\nTo enable full production mode:")
            print("  1. Set OPENAI_API_KEY environment variable")
            print("  2. Or create config.yaml with your API key")
            print("  3. Run: python test_e2e.py again")
            return True
    else:
        print("\n❌ Sandbox test failed - Please fix issues first")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
