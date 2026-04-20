"""
OpenSpace-OpenHands-Evolution 使用示例

展示如何使用系统进行任务执行、跨项目迁移和失败预测。
"""

import asyncio
from openspace_openhands_evolution import EvolutionOrchestrator, TaskRequest, TransferRequest


# 系统配置
CONFIG = {
    'openspace': {
        'registry_path': './data/skills',
        'vector_db_url': 'chromadb://localhost:8000'
    },
    'openhands': {
        'model': 'gpt-4',
        'sandbox_enabled': True
    },
    'monitor': {
        'quality_threshold': 0.8
    },
    'governance': {
        'enable_gatekeeping': True,
        'enable_fingerprint': True
    },
    'mtl': {
        'similarity_threshold': 0.7
    },
    'aaip': {
        'skill_sharing_enabled': True
    }
}


async def example_basic_task():
    """示例 1: 基础任务执行"""
    print("="*60)
    print("示例 1: 基础任务执行")
    print("="*60)
    
    # 初始化编排器
    orchestrator = EvolutionOrchestrator(CONFIG)
    
    # 创建任务
    task = TaskRequest(
        id="task-001",
        description="创建一个 Python Flask API，包含用户 CRUD 操作",
        project_id="my-web-app",
        language="python",
        framework="flask",
        model="gpt-4",
        max_iterations=10
    )
    
    # 执行任务
    result = await orchestrator.execute_task(task)
    
    # 查看结果
    if result.success:
        print(f"✅ 任务成功完成!")
        print(f"   输出: {result.output[:200]}...")
        print(f"   质量评分: {result.metrics.get('overall_score', 0):.2f}")
        print(f"   进化的技能: {result.evolved_skills}")
    else:
        print(f"❌ 任务失败: {result.error}")
    
    print()


async def example_cross_project_transfer():
    """示例 2: 跨项目技能迁移"""
    print("="*60)
    print("示例 2: 跨项目技能迁移")
    print("="*60)
    
    orchestrator = EvolutionOrchestrator(CONFIG)
    
    # 创建迁移请求
    transfer_request = TransferRequest(
        source_project="project-a",
        target_project="project-b",
        min_similarity=0.7
    )
    
    try:
        # 执行迁移
        result = await orchestrator.cross_project_transfer(transfer_request)
        
        print(f"✅ 成功迁移 {result.transferred_count} 个技能")
        print(f"   风险等级: {result.risk_assessment.get('risk_level', 'unknown')}")
        print(f"   风险评分: {result.risk_assessment.get('risk_score', 0):.2f}")
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
    
    print()


async def example_failure_prediction():
    """示例 3: 失败预测"""
    print("="*60)
    print("示例 3: 失败预测")
    print("="*60)
    
    orchestrator = EvolutionOrchestrator(CONFIG)
    
    # 创建高风险任务
    task = TaskRequest(
        id="task-risky",
        description="复杂的数据库迁移脚本，涉及多个表的结构变更",
        project_id="legacy-system",
        language="python",
        context={
            "complexity": "high",
            "has_tests": False,
            "database_type": "postgresql"
        }
    )
    
    # 预测失败风险
    prediction = await orchestrator.predict_failure(task)
    
    print(f"风险等级: {prediction.get('risk_level', 'unknown')}")
    print(f"失败概率: {prediction.get('failure_probability', 0):.2%}")
    print(f"原因:")
    for reason in prediction.get('reasons', []):
        print(f"   - {reason}")
    
    print(f"建议:")
    for rec in prediction.get('recommendations', []):
        print(f"   ✓ {rec}")
    
    print()


async def example_system_status():
    """示例 4: 系统状态查询"""
    print("="*60)
    print("示例 4: 系统状态查询")
    print("="*60)
    
    orchestrator = EvolutionOrchestrator(CONFIG)
    
    # 获取系统状态
    status = await orchestrator.get_system_status()
    
    print("系统状态:")
    print(f"  OpenSpace: {status['openspace']['status']}")
    print(f"  OpenHands: {status['openhands']['status']}")
    print(f"  Monitor: {status['monitor']['status']}")
    print(f"  Governance: {status['governance']['status']}")
    print(f"  时间戳: {status['timestamp']}")
    
    print()


async def example_interpretable_reasoning():
    """示例 5: 可解释推理轨迹（RadAgent 风格）"""
    print("="*60)
    print("示例 5: 可解释推理轨迹")
    print("="*60)
    
    orchestrator = EvolutionOrchestrator(CONFIG)
    
    task = TaskRequest(
        id="task-interpretable",
        description="创建 REST API",
        project_id="demo-project",
        language="python"
    )
    
    result = await orchestrator.execute_task(task)
    
    # 显示推理轨迹
    if result.reasoning_trace:
        print(f"\n📊 推理轨迹 ({len(result.reasoning_trace)} 步):")
        for i, step in enumerate(result.reasoning_trace, 1):
            print(f"\n  步骤 {i}: [{step['layer'].upper()}] {step['step']}")
            print(f"    时间: {step['timestamp']}")
            if 'skills_found' in step:
                print(f"    找到技能: {step['skills_found']}")
            if 'skills_adapted' in step:
                print(f"    适配技能: {step['skills_adapted']}")
            if 'success' in step:
                print(f"    执行结果: {'✅ 成功' if step['success'] else '❌ 失败'}")
    
    # 显示执行步骤
    if result.execution_steps:
        print(f"\n⚙️  执行步骤 ({len(result.execution_steps)} 步):")
        for i, step in enumerate(result.execution_steps, 1):
            print(f"\n  步骤 {i}: {step['step']}")
            for key, value in step.items():
                if key != 'step':
                    print(f"    {key}: {value}")
    
    print()


async def main():
    """运行所有示例"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║  OpenSpace-OpenHands-Evolution 使用示例              ║")
    print("╚" + "="*58 + "╝")
    print()
    
    # 运行示例
    await example_basic_task()
    await example_cross_project_transfer()
    await example_failure_prediction()
    await example_system_status()
    await example_interpretable_reasoning()  # 新增
    
    print("所有示例运行完成! 🎉")


if __name__ == "__main__":
    asyncio.run(main())
