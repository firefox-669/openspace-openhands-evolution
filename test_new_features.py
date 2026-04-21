"""
测试新增功能：策略引擎、知识图谱、错误预测
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from openspace_openhands_evolution import (
    IntelligentExecutionStrategyEngine,
    KnowledgeGraph,
    RealTimeErrorPreventionSystem
)


async def test_strategy_engine():
    """测试智能策略引擎"""
    print("\n" + "="*60)
    print("🧪 Testing Strategy Engine")
    print("="*60)
    
    config = {'storage_path': './data/test_strategy'}
    engine = IntelligentExecutionStrategyEngine(config)
    
    # 模拟一些执行记录
    print("\n📝 Recording execution results...")
    await engine.record_execution_result(
        task_id="test-001",
        task_type="code_generation",
        strategy_type="balanced",
        success=True,
        execution_time=15.5,
        quality_score=0.85
    )
    
    await engine.record_execution_result(
        task_id="test-002",
        task_type="code_generation",
        strategy_type="aggressive",
        success=False,
        execution_time=8.2,
        quality_score=0.45,
        error_type="timeout_error"
    )
    
    await engine.record_execution_result(
        task_id="test-003",
        task_type="bug_fixing",
        strategy_type="conservative",
        success=True,
        execution_time=25.3,
        quality_score=0.92
    )
    
    # 预测最佳策略
    print("\n🔮 Predicting best strategy for code_generation...")
    best_strategy, evaluations = engine.selector.predict_best_strategy("code_generation")
    print(f"   Best strategy: {best_strategy}")
    for strategy, eval_data in evaluations.items():
        print(f"   - {strategy}: score={eval_data['score']:.2f}, "
              f"success_rate={eval_data['success_rate']:.2%}")
    
    # 获取性能报告
    print("\n📊 Performance Report:")
    report = await engine.get_performance_report("code_generation")
    
    # 获取调整建议
    print("\n💡 Adjustment Suggestion:")
    suggestion = await engine.get_adjustment_suggestion("code_generation")
    print(f"   Should switch: {suggestion['should_switch']}")
    if suggestion['should_switch']:
        print(f"   Reason: {suggestion['reason']}")
    
    engine.save_state()
    print("\n✅ Strategy Engine test completed!")


async def test_knowledge_graph():
    """测试知识图谱"""
    print("\n" + "="*60)
    print("🧪 Testing Knowledge Graph")
    print("="*60)
    
    kg = KnowledgeGraph(storage_path='./data/test_kg')
    
    # 添加项目节点
    print("\n📦 Adding project nodes...")
    kg.add_project(
        project_id="project-a",
        name="E-commerce Platform",
        language="python",
        framework="django",
        domain="web_development"
    )
    
    kg.add_project(
        project_id="project-b",
        name="Data Pipeline",
        language="python",
        framework="fastapi",
        domain="data_engineering"
    )
    
    kg.add_project(
        project_id="project-c",
        name="Mobile API",
        language="javascript",
        framework="express",
        domain="web_development"
    )
    
    # 添加知识项
    print("\n📝 Adding knowledge items...")
    kg.add_knowledge_item(
        item_id="skill-001",
        item_type="skill",
        title="REST API Design Pattern",
        description="Best practices for RESTful API design",
        project_id="project-a",
        tags=["api", "rest", "design"],
        quality_score=0.9
    )
    
    kg.add_knowledge_item(
        item_id="skill-002",
        item_type="pattern",
        title="Async Task Processing",
        description="Pattern for handling async tasks efficiently",
        project_id="project-b",
        tags=["async", "task", "performance"],
        quality_score=0.85
    )
    
    # 添加知识边
    print("\n🔗 Adding knowledge edges...")
    kg.add_knowledge_edge(
        source_project="project-a",
        target_project="project-c",
        relation_type="same_domain",
        strength=0.8,
        knowledge_items=["skill-001"]
    )
    
    kg.add_knowledge_edge(
        source_project="project-a",
        target_project="project-b",
        relation_type="shared_skill",
        strength=0.6,
        knowledge_items=["skill-001", "skill-002"]
    )
    
    # 查询相关项目
    print("\n🔍 Querying related projects for project-a...")
    related = kg.query_related_projects("project-a", min_strength=0.5)
    print(f"   Found {len(related)} related projects:")
    for rel in related:
        print(f"   - {rel['project']['name']} (strength: {rel['edge']['strength']:.2f})")
    
    # 查找可迁移知识
    print("\n🔄 Finding transferable knowledge from project-a to project-c...")
    transferable = kg.find_transferable_knowledge("project-a", "project-c")
    print(f"   Found {len(transferable)} transferable items:")
    for item in transferable:
        print(f"   - {item.title} (quality: {item.quality_score:.2f})")
    
    # 记录知识迁移
    if transferable:
        print("\n📤 Recording knowledge transfer...")
        kg.record_knowledge_transfer(
            source_project="project-a",
            target_project="project-c",
            knowledge_item_ids=[item.id for item in transferable],
            success=True,
            quality_impact=0.1
        )
    
    # 搜索知识
    print("\n🔎 Searching knowledge with keyword 'api'...")
    results = kg.search_knowledge("api", min_quality=0.8)
    print(f"   Found {len(results)} items:")
    for item in results:
        print(f"   - {item.title} (type: {item.type})")
    
    # 获取项目统计
    print("\n📊 Project Statistics for project-a:")
    stats = kg.get_project_statistics("project-a")
    print(f"   Total knowledge items: {stats['total_knowledge_items']}")
    print(f"   Average quality: {stats['avg_quality_score']:.2f}")
    print(f"   Total connections: {stats['total_connections']}")
    
    # 可视化图谱
    print("\n🕸️  Graph Visualization:")
    visualization = kg.visualize_graph()
    print(visualization)
    
    kg.save_graph()
    print("\n✅ Knowledge Graph test completed!")


async def test_error_prediction():
    """测试错误预测系统"""
    print("\n" + "="*60)
    print("🧪 Testing Error Prediction System")
    print("="*60)
    
    config = {'storage_path': './data/test_errors'}
    prevention_system = RealTimeErrorPreventionSystem(config)
    
    # 模拟一些历史错误
    print("\n📝 Recording historical errors...")
    prevention_system.record_execution_error(
        task_id="hist-001",
        task_type="code_generation",
        error_type="syntax_error",
        error_message="Missing colon in function definition",
        severity="low"
    )
    
    prevention_system.record_execution_error(
        task_id="hist-002",
        task_type="code_generation",
        error_type="timeout_error",
        error_message="Execution exceeded 30s timeout",
        severity="high"
    )
    
    prevention_system.record_execution_error(
        task_id="hist-003",
        task_type="bug_fixing",
        error_type="runtime_error",
        error_message="Null pointer exception",
        severity="medium"
    )
    
    prevention_system.record_execution_error(
        task_id="hist-004",
        task_type="code_generation",
        error_type="dependency_error",
        error_message="Module not found: requests",
        severity="medium"
    )
    
    # 预测新任务的错误
    print("\n🔮 Predicting errors for new code_generation task...")
    prediction_result = await prevention_system.predict_and_prevent(
        task_id="new-task-001",
        task_type="code_generation",
        context={"framework": "flask"}
    )
    
    prediction = prediction_result['prediction']
    print(f"   Overall Risk Score: {prediction['overall_risk_score']:.2f}")
    print(f"   Confidence: {prediction['confidence']:.2%}")
    print(f"   Predicted Errors: {len(prediction['predicted_errors'])}")
    
    for error in prediction['predicted_errors'][:3]:  # 显示前3个
        print(f"\n   ⚠️  {error['error_type']}")
        print(f"      Severity: {error['severity']}")
        print(f"      Risk Score: {error['risk_score']:.2f}")
        if error.get('prevention_strategies'):
            print(f"      Prevention:")
            for strategy in error['prevention_strategies'][:2]:
                print(f"        • {strategy}")
    
    # 获取调整建议
    print("\n💡 Dynamic Adjustment Suggestion:")
    adjustment = prediction_result['adjustment']
    print(f"   Action: {adjustment['action']}")
    print(f"   Message: {adjustment['message']}")
    if 'recommendations' in adjustment:
        print(f"   Recommendations:")
        for rec in adjustment['recommendations']:
            print(f"     - {rec}")
    
    # 获取错误分析
    print("\n📊 Error Analytics:")
    analytics = prevention_system.get_error_analytics("code_generation")
    print(f"   Total error patterns: {analytics['total_error_patterns']}")
    print(f"   Total error records: {analytics['total_error_records']}")
    print(f"   Most common errors:")
    for error_info in analytics['most_common_errors'][:3]:
        print(f"     - {error_info['error_type']}: {error_info['occurrence_count']} occurrences")
    
    prevention_system.save_state()
    print("\n✅ Error Prediction test completed!")


async def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 Testing New Features: Strategy, Knowledge Graph, Error Prediction")
    print("="*60)
    
    try:
        # 测试策略引擎
        await test_strategy_engine()
        
        # 测试知识图谱
        await test_knowledge_graph()
        
        # 测试错误预测
        await test_error_prediction()
        
        print("\n" + "="*60)
        print("✅ All tests completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
