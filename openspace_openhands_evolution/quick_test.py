"""
快速验证脚本 - 测试所有核心模块是否正常

使用方法:
    python quick_test.py
"""

import asyncio
import sys
import unittest


class TestCoreModules(unittest.TestCase):
    """核心模块测试类"""
    
    def test_all_modules(self):
        """测试所有核心模块"""
        # 运行异步测试
        result = asyncio.run(self._run_async_tests())
        self.assertTrue(result, "Tests failed")
    
    async def _run_async_tests(self):
        """异步测试逻辑"""
        print("="*60)
        print("Testing OpenSpace-OpenHands-Evolution Core Modules")
        print("="*60)
        print()
        
        try:
            # 测试 1: 导入模块
            print("1️⃣  Testing imports...")
            from openspace_openhands_evolution import (
                EvolutionOrchestrator,
                TaskRequest,
                TransferRequest,
                load_config
            )
            print("   ✅ All imports successful")
            print()
            
            # 测试 2: 初始化编排器
            print("2️⃣  Testing orchestrator initialization...")
            config = {
                'openspace': {'registry_path': './data/skills'},
                'openhands': {'model': 'gpt-4'},
                'monitor': {'quality_threshold': 0.8},
                'governance': {'enable_gatekeeping': True}
            }
            orchestrator = EvolutionOrchestrator(config)
            print("   ✅ Orchestrator initialized")
            print()
            
            # 测试 3: 执行任务
            print("3️⃣  Testing task execution...")
            task = TaskRequest(
                id="test-task-001",
                description="Create a simple API",
                project_id="demo-project",
                language="python"
            )
            
            result = await orchestrator.execute_task(task)
            print(f"   ✅ Task executed: success={result.success}")
            print(f"   📊 Quality score: {result.metrics.get('overall_score', 0):.2f}")
            print(f"   🔍 Reasoning trace steps: {len(result.reasoning_trace)}")
            print(f"   ⚙️  Execution steps: {len(result.execution_steps)}")
            print()
            
            # 测试 4: 系统状态
            print("4️⃣  Testing system status...")
            status = await orchestrator.get_system_status()
            print(f"   ✅ System status retrieved")
            print(f"   - OpenSpace: {status['openspace']['status']}")
            print(f"   - OpenHands: {status['openhands']['status']}")
            print(f"   - Monitor: {status['monitor']['status']}")
            print(f"   - Governance: {status['governance']['status']}")
            print()
            
            # 测试 5: 跨项目迁移
            print("5️⃣  Testing cross-project transfer...")
            from openspace_openhands_evolution import TransferRequest
            
            transfer_request = TransferRequest(
                source_project="project-a",
                target_project="project-b",
                min_similarity=0.7
            )
            
            transfer_result = await orchestrator.cross_project_transfer(transfer_request)
            print(f"   ✅ Transfer completed")
            print(f"   - Transferred skills: {transfer_result.transferred_count}")
            print(f"   - Risk level: {transfer_result.risk_assessment.get('risk_level', 'N/A')}")
            print()
            
            # 测试 6: 失败预测
            print("6️⃣  Testing failure prediction...")
            prediction = await orchestrator.predict_failure(task)
            print(f"   ✅ Failure prediction completed")
            print(f"   - Risk level: {prediction.get('risk_level', 'N/A')}")
            print(f"   - Failure probability: {prediction.get('failure_probability', 0):.2%}")
            print()
            
            print("="*60)
            print("✅ ALL TESTS PASSED!")
            print("="*60)
            print()
            print("🎉 Project is ready for use!")
            print()
            print("Next steps:")
            print("  1. Run: openspace-evolution")
            print("  2. Or: python examples.py")
            print("  3. Check: pytest tests/")
            
            return True
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    # 直接运行时使用 asyncio
    success = asyncio.run(TestCoreModules()._run_async_tests())
    sys.exit(0 if success else 1)
