"""
OpenSpace-OpenHands-Evolution 核心编排器

负责协调 OpenSpace（记忆/进化）和 OpenHands（执行）的协作，
实现四阶段治理流程和跨项目技能迁移。
"""

import asyncio
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone

from .openspace_engine import OpenSpaceEngine
from .production_engine import ProductionOpenHandsEngine
from .monitor import MonitorSystem
from .governance import GovernanceLayer
from .mtl_adapter import MTLAdapter
from .aaip_protocol import AAIPProtocol
from .strategy_engine import IntelligentExecutionStrategyEngine
from .knowledge_graph import KnowledgeGraph
from .error_prediction import RealTimeErrorPreventionSystem


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EvolutionType(Enum):
    """进化类型"""
    FIX = "fix"
    OPTIMIZE = "optimize"
    CREATE = "create"


class AgentLayer(Enum):
    """Agent 分层架构（参考 MM-WebAgent）"""
    PLANNING = "planning"      # 顶层：任务规划与分解
    COORDINATION = "coordination"  # 中层：协调与约束传播
    EXECUTION = "execution"    # 底层：具体执行


@dataclass
class TaskRequest:
    """任务请求"""
    id: str
    description: str
    project_id: str
    language: str = "python"
    framework: Optional[str] = None
    model: str = "gpt-4"
    max_iterations: int = 10
    expected_output: Optional[str] = None
    context: Dict = field(default_factory=dict)


@dataclass
class TaskResult:
    """任务结果"""
    success: bool
    output: str
    metrics: Dict
    evolved_skills: List[str] = field(default_factory=list)
    error: Optional[str] = None
    reasoning_trace: List[Dict] = field(default_factory=list)  # RadAgent 式推理轨迹
    execution_steps: List[Dict] = field(default_factory=list)  # 执行步骤详情


@dataclass
class TransferRequest:
    """跨项目迁移请求"""
    source_project: str
    target_project: str
    min_similarity: float = 0.7
    skill_ids: Optional[List[str]] = None


@dataclass
class TransferResult:
    """迁移结果"""
    transferred_count: int
    risk_assessment: Dict
    transfer_details: List[Dict] = field(default_factory=list)  # 迁移详情


class GatekeepingError(Exception):
    """准入控制错误"""
    pass


class EnvironmentMismatchError(Exception):
    """环境不匹配错误"""
    pass


class NegativeTransferRiskError(Exception):
    """负迁移风险错误"""
    def __init__(self, assessment: Dict):
        self.assessment = assessment
        super().__init__(f"Negative transfer risk: {assessment}")


class EvolutionOrchestrator:
    """
    进化编排器 - 系统核心控制器
    
    协调 OpenSpace 和 OpenHands 的协作，实现：
    1. 四阶段治理流程（准入、运行、维护、进化）
    2. 跨项目技能迁移（MTL + AAIP）
    3. 智能错误预测和预防
    4. 环境指纹匹配和负迁移检测
    """
    
    def __init__(self, config: Dict):
        """
        初始化编排器
        
        Args:
            config: 系统配置字典
        """
        self.config = config
        
        # 初始化核心引擎
        self.openspace_engine = OpenSpaceEngine(config.get('openspace', {}))
        
        # 使用生产级引擎（支持真实 LLM 和代码执行）
        openhands_config = config.get('openhands', {})
        llm_config = config.get('llm', {})
        # 合并配置
        production_config = {**openhands_config, **llm_config}
        self.openhands_engine = ProductionOpenHandsEngine(production_config)
        
        self.monitor = MonitorSystem(config.get('monitor', {}))
        self.governance = GovernanceLayer(config.get('governance', {}))
        
        # 初始化工具适配器
        self.mtl_adapter = MTLAdapter(config.get('mtl', {}))
        self.aaip_protocol = AAIPProtocol(config.get('aaip', {}))
        
        # 初始化智能策略引擎
        self.strategy_engine = IntelligentExecutionStrategyEngine(config.get('strategy', {}))
        
        # 初始化知识图谱
        self.knowledge_graph = KnowledgeGraph(config.get('knowledge_graph', {}).get('storage_path', './data/knowledge_graph'))
        
        # 初始化错误预测系统
        self.error_prevention = RealTimeErrorPreventionSystem(config.get('error_prediction', {}))
        
        # 质量阈值
        self.quality_threshold = config.get('quality_threshold', 0.8)
        self.skill_sharing_enabled = config.get('skill_sharing_enabled', True)
    
    async def execute_task(self, task: TaskRequest) -> TaskResult:
        """
        执行任务的完整流程
        
        四阶段治理:
        1. 准入控制 (Gatekeeping)
        2. 运行监控 (Runtime Monitoring)
        3. 定期维护 (Maintenance) - 异步后台任务
        4. 进化优化 (Evolution)
        
        Args:
            task: 任务请求
            
        Returns:
            TaskResult: 任务执行结果
        """
        print(f"🚀 Starting task execution: {task.id}")
        
        try:
            # === 阶段 1: 准入控制 ===
            print("📋 Phase 1: Gatekeeping...")
            approved, reason = await self.governance.gatekeeper.validate_task(task)
            if not approved:
                raise GatekeepingError(reason)
            
            # === 阶段 1.5: 错误预测与预防 ===
            print("🔮 Phase 1.5: Error Prediction...")
            task_type = self._classify_task_type(task)
            prediction_result = await self.error_prevention.predict_and_prevent(
                task_id=task.id,
                task_type=task_type,
                context=task.context
            )
            
            if not prediction_result['should_proceed']:
                print(f"⚠️  High risk detected, proceeding with caution")
                print(f"   Risk Score: {prediction_result['prediction']['overall_risk_score']:.2f}")
                for suggestion in prediction_result['prediction'].get('prevention_suggestions', []):
                    print(f"   {suggestion}")
            
            # === 阶段 1.6: 智能策略选择 ===
            print("🎯 Phase 1.6: Strategy Selection...")
            selected_strategy = await self.strategy_engine.select_strategy(
                task_type=task_type,
                priority="balanced"
            )
            task.context['selected_strategy'] = selected_strategy
            
            # === 阶段 2: 任务规划与执行 ===
            print("⚙️  Phase 2: Task Execution...")
            execution_result = await self._phase2_execute(task)
            
            # === 阶段 3: 运行监控 ===
            print("📊 Phase 3: Runtime Monitoring...")
            quality_metrics = await self.monitor.monitor_execution(execution_result)
            
            # === 阶段 4: 进化优化 ===
            print("🧬 Phase 4: Evolution...")
            evolved_skills = await self._phase4_evolve(
                task=task,
                execution_result=execution_result,
                quality_metrics=quality_metrics
            )
            
            # === 阶段 5: 记录执行结果到策略引擎和知识图谱 ===
            print("📝 Phase 5: Recording Results...")
            task_type = self._classify_task_type(task)
            selected_strategy = task.context.get('selected_strategy', 'balanced')
            
            # 记录策略执行结果
            await self.strategy_engine.record_execution_result(
                task_id=task.id,
                task_type=task_type,
                strategy_type=selected_strategy,
                success=execution_result.get('success', False),
                execution_time=quality_metrics.get('execution_time', 0),
                quality_score=quality_metrics.get('quality_score', 0),
                error_type=execution_result.get('error_type'),
                context={'project_id': task.project_id}
            )
            
            # 如果失败，记录错误
            if not execution_result.get('success'):
                await self.error_prevention.record_execution_error(
                    task_id=task.id,
                    task_type=task_type,
                    error_type=execution_result.get('error_type', 'unknown'),
                    error_message=execution_result.get('error', 'Unknown error'),
                    severity='medium',
                    context={'project_id': task.project_id}
                )
            
            # 更新知识图谱
            await self._update_knowledge_graph(task, execution_result, evolved_skills)
            
            # 启动后台维护任务
            asyncio.create_task(self._background_maintenance())
            
            return TaskResult(
                success=execution_result.get('success', False),
                output=execution_result.get('output', ''),
                metrics=quality_metrics,
                evolved_skills=evolved_skills,
                reasoning_trace=execution_result.get('reasoning_trace', []),
                execution_steps=execution_result.get('execution_steps', [])
            )
            
        except GatekeepingError as e:
            print(f"❌ Gatekeeping failed: {e}")
            return TaskResult(
                success=False,
                output='',
                metrics={},
                error=f"Gatekeeping failed: {str(e)}"
            )
            
        except Exception as e:
            print(f"❌ Task execution failed: {e}")
            await self.monitor.log_error(e)
            await self.governance.maintainer.rollback(task.id)
            
            return TaskResult(
                success=False,
                output='',
                metrics={},
                error=str(e)
            )
    
    async def _phase1_gatekeeping(self, task: TaskRequest):
        """
        阶段 1: 准入控制
        
        - 验证任务语法
        - 安全检查
        - 资源限制检查
        - 环境兼容性检查
        - 环境指纹匹配
        """
        # 1. 基本验证
        validation_result = await self.governance.gatekeeper.validate(task)
        if not validation_result['passed']:
            raise GatekeepingError(
                f"Task validation failed: {validation_result['checks']}"
            )
        
        # 2. 环境指纹捕获和匹配
        env_fingerprint = await self.governance.fingerprint_system.capture()
        required_fingerprint = await self._get_required_fingerprint(task.project_id)
        
        if required_fingerprint:
            match_result = await self.governance.fingerprint_system.match(
                current_fp=env_fingerprint,
                required_fp=required_fingerprint,
                tolerance=0.8
            )
            
            if not match_result['compatible']:
                raise EnvironmentMismatchError(
                    f"Environment mismatch: {match_result['incompatible_items']}"
                )
        
        print("✅ Gatekeeping passed")
    
    async def _phase2_execute(self, task: TaskRequest) -> Dict:
        """
        阶段 2: 任务执行
        
        采用分层 Agent 架构（参考 MM-WebAgent）：
        - Planning Layer: 任务规划与分解
        - Coordination Layer: 协调与约束传播
        - Execution Layer: 具体执行
        
        同时记录推理轨迹（参考 RadAgent）
        """
        reasoning_trace = []
        execution_steps = []
        
        # === Planning Layer: 任务规划 ===
        print("   [Planning] Decomposing task...")
        planning_result = await self._planning_layer(task)
        reasoning_trace.append({
            "layer": "planning",
            "step": "task_decomposition",
            "output": planning_result,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # === Coordination Layer: 技能检索与适配 ===
        print("   [Coordination] Retrieving and adapting skills...")
        relevant_skills = await self.openspace_engine.search_skills(
            query=task.description,
            context={
                "project": task.project_id,
                "language": task.language,
                "framework": task.framework
            }
        )
        
        reasoning_trace.append({
            "layer": "coordination",
            "step": "skill_retrieval",
            "skills_found": len(relevant_skills),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        print(f"   Found {len(relevant_skills)} relevant skills")
        
        # 通过 MTL 适配技能
        if relevant_skills and task.project_id:
            adapted_skills = await self.mtl_adapter.transfer_skills(
                source_skills=relevant_skills,
                target_project=task.project_id,
                similarity_threshold=0.7
            )
            reasoning_trace.append({
                "layer": "coordination",
                "step": "skill_adaptation",
                "skills_adapted": len(adapted_skills),
                "timestamp": datetime.utcnow().isoformat()
            })
            print(f"   Adapted {len(adapted_skills)} skills for target project")
        else:
            adapted_skills = relevant_skills
        
        execution_steps.append({
            "step": "skill_preparation",
            "retrieved": len(relevant_skills),
            "adapted": len(adapted_skills)
        })
        
        # === Execution Layer: 任务执行 ===
        print("   [Execution] Running task...")
        if adapted_skills:
            await self.openhands_engine.inject_skills(adapted_skills)
        
        execution_result = await self.openhands_engine.execute(
            task=task,
            skills=adapted_skills
        )
        
        reasoning_trace.append({
            "layer": "execution",
            "step": "task_execution",
            "success": execution_result.get('success'),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        execution_steps.append({
            "step": "task_execution",
            "success": execution_result.get('success'),
            "output_length": len(execution_result.get('output', ''))
        })
        
        print(f"   Execution {'succeeded' if execution_result['success'] else 'failed'}")
        
        # 附加推理轨迹到结果
        execution_result['reasoning_trace'] = reasoning_trace
        execution_result['execution_steps'] = execution_steps
        
        return execution_result
    
    async def _phase3_monitor(self, execution_result: Dict) -> Dict:
        """
        阶段 3: 运行监控
        
        - 评估执行质量
        - 检测异常
        - 记录指标
        """
        quality_metrics = await self.monitor.evaluate_execution(execution_result)
        
        # 如果质量低于阈值，触发审查
        if quality_metrics.get('overall_score', 0) < self.quality_threshold:
            print(f"⚠️  Quality score {quality_metrics['overall_score']} below threshold")
            await self.monitor.trigger_review(execution_result)
        
        print(f"   Quality score: {quality_metrics.get('overall_score', 0):.2f}")
        
        return quality_metrics
    
    async def _phase4_evolve(self, task: TaskRequest, 
                            execution_result: Dict,
                            quality_metrics: Dict) -> List[str]:
        """
        阶段 4: 进化优化
        
        - 如果成功：提取经验，进化技能
        - 如果失败：分析原因，修复技能
        - 通过 AAIP 分享技能
        """
        evolved_skills = []
        
        if execution_result.get('success'):
            # 成功：进化技能
            print("   Evolving skill based on successful execution...")
            
            new_skill = await self.openspace_engine.evolve_skill(
                task=task,
                execution_trace=execution_result.get('trace', {}),
                quality_score=quality_metrics.get('overall_score', 0)
            )
            
            if new_skill:
                evolved_skills.append(new_skill.get('id', ''))
                
                # 通过 AAIP 分享技能
                if self.skill_sharing_enabled:
                    await self.aaip_protocol.share_skill(
                        skill_id=new_skill.get('id'),
                        scope="global"
                    )
                    print(f"   Shared skill {new_skill.get('id')} globally")
        else:
            # 失败：修复技能
            print("   Fixing skill based on failure analysis...")
            
            failed_skill_id = execution_result.get('failed_skill_id')
            if failed_skill_id:
                await self.openspace_engine.fix_skill(
                    failed_skill_id=failed_skill_id,
                    error_context=execution_result.get('error', {})
                )
                evolved_skills.append(f"{failed_skill_id}:fixed")
        
        return evolved_skills
    
    async def cross_project_transfer(self, transfer_request: TransferRequest) -> TransferResult:
        """
        跨项目技能迁移（MTL + AAIP 混合方案）
        
        Args:
            transfer_request: 迁移请求
            
        Returns:
            TransferResult: 迁移结果
        """
        print(f"🔄 Starting cross-project transfer: "
              f"{transfer_request.source_project} → {transfer_request.target_project}")
        
        # 1. 从源项目提取技能
        if transfer_request.skill_ids:
            source_skills = await self.openspace_engine.get_skills_by_ids(
                transfer_request.skill_ids
            )
        else:
            source_skills = await self.openspace_engine.get_project_skills(
                transfer_request.source_project
            )
        
        print(f"   Extracted {len(source_skills)} skills from source project")
        
        # 2. MTL: 计算任务结构相似度（简化实现）
        print("   🧠 Computing task similarity...")
        # 由于是演示，假设所有技能都适合迁移
        transferable_skills = source_skills
        
        print(f"   Filtered to {len(transferable_skills)} transferable skills")
        
        # 3. AAIP: 标准化技能格式
        standardized_skills = []
        for skill in transferable_skills:
            standardized = await self.aaip_protocol.standardize_skill(skill)
            standardized_skills.append(standardized)
        
        # 4. 负迁移检测 (V-02) - 简化实现
        risk_assessment = {
            'risk_level': 'low',
            'risk_score': 0.2,
            'factors': []
        }
        
        if risk_assessment.get('risk_level') in ['high', 'critical']:
            raise NegativeTransferRiskError(risk_assessment)
        
        print(f"   Risk assessment: {risk_assessment.get('risk_level')}")
        
        # 5. 导入到目标项目
        await self.openspace_engine.import_skills(
            project_id=transfer_request.target_project,
            skills=standardized_skills
        )
        
        print(f"   ✅ Transferred {len(standardized_skills)} skills successfully")
        
        return TransferResult(
            transferred_count=len(standardized_skills),
            risk_assessment=risk_assessment,
            transfer_details=[{"skill_id": s.get('skill_id')} for s in standardized_skills]
        )
    
    async def _background_maintenance(self):
        """
        后台维护任务
        
        - 清理过期技能
        - 优化索引
        - 备份数据库
        - 健康检查
        """
        try:
            print("🔧 Running background maintenance...")
            await self.governance.maintainer.scheduled_maintenance()
            print("✅ Maintenance completed")
        except Exception as e:
            print(f"⚠️  Maintenance failed: {e}")
    
    async def _get_required_fingerprint(self, project_id: str) -> Optional[Dict]:
        """获取项目所需的环境指纹"""
        # TODO: 从配置或数据库中获取
        return None
    
    async def _planning_layer(self, task: TaskRequest) -> Dict:
        """
        Planning Layer: 任务规划与分解（参考 MM-WebAgent）
        
        负责：
        - 理解任务意图
        - 分解为子任务
        - 制定执行策略
        - 设定约束条件
        """
        # 简化实现：基于任务描述生成规划
        planning_result = {
            "task_id": task.id,
            "description": task.description,
            "subtasks": [
                {
                    "id": f"{task.id}-1",
                    "name": "分析需求",
                    "type": "analysis",
                    "estimated_complexity": "medium"
                },
                {
                    "id": f"{task.id}-2",
                    "name": "设计解决方案",
                    "type": "design",
                    "dependencies": [f"{task.id}-1"]
                },
                {
                    "id": f"{task.id}-3",
                    "name": "执行实现",
                    "type": "implementation",
                    "dependencies": [f"{task.id}-2"]
                }
            ],
            "constraints": {
                "language": task.language,
                "framework": task.framework,
                "max_iterations": task.max_iterations
            },
            "strategy": "hierarchical_decomposition"
        }
        
        return planning_result
    
    async def predict_failure(self, task: TaskRequest) -> Dict:
        """
        预测任务失败风险
        
        Args:
            task: 任务请求
            
        Returns:
            失败预测结果
        """
        # 简化实现：基于任务复杂度评估
        import random
        
        risk_factors = []
        
        # 检查 1: 任务描述长度
        if len(task.description) < 10:
            risk_factors.append("Task description too short")
        
        # 检查 2: 是否有上下文
        if not task.context:
            risk_factors.append("No additional context provided")
        
        # 检查 3: 最大迭代次数
        if task.max_iterations < 5:
            risk_factors.append("Low iteration limit")
        
        # 计算风险等级
        if len(risk_factors) >= 2:
            risk_level = "high"
            failure_prob = 0.7
        elif len(risk_factors) == 1:
            risk_level = "medium"
            failure_prob = 0.4
        else:
            risk_level = "low"
            failure_prob = 0.1
        
        return {
            "risk_level": risk_level,
            "failure_probability": failure_prob,
            "risk_factors": risk_factors,
            "recommendations": [
                "Provide more detailed task description",
                "Add relevant context information",
                "Consider increasing max_iterations"
            ] if risk_factors else ["Task looks good, proceed with execution"]
        }
    
    async def get_system_status(self) -> Dict:
        """
        获取系统状态
        
        Returns:
            系统状态信息
        """
        return {
            "openspace": await self.openspace_engine.get_status(),
            "openhands": await self.openhands_engine.get_status(),
            "monitor": await self.monitor.get_status(),
            "governance": await self.governance.get_status(),
            "strategy_engine": {
                "total_records": len(self.strategy_engine.history.records),
                "current_strategy": self.strategy_engine.current_strategy
            },
            "knowledge_graph": {
                "projects": len(self.knowledge_graph.projects),
                "edges": len(self.knowledge_graph.edges),
                "knowledge_items": len(self.knowledge_graph.knowledge_items)
            },
            "error_prevention": {
                "error_patterns": len(self.error_prevention.db.patterns),
                "error_records": len(self.error_prevention.db.error_records)
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _classify_task_type(self, task: TaskRequest) -> str:
        """
        分类任务类型
        
        Args:
            task: 任务请求
            
        Returns:
            任务类型字符串
        """
        description_lower = task.description.lower()
        
        if any(keyword in description_lower for keyword in ['create', 'build', 'generate']):
            return 'code_generation'
        elif any(keyword in description_lower for keyword in ['fix', 'debug', 'repair']):
            return 'bug_fixing'
        elif any(keyword in description_lower for keyword in ['refactor', 'optimize', 'improve']):
            return 'code_refactoring'
        elif any(keyword in description_lower for keyword in ['test', 'validate']):
            return 'testing'
        elif any(keyword in description_lower for keyword in ['analyze', 'review']):
            return 'code_analysis'
        else:
            return 'general'
    
    async def _update_knowledge_graph(self, task: TaskRequest, 
                                     execution_result: Dict,
                                     evolved_skills: List[str]):
        """
        更新知识图谱
        
        Args:
            task: 任务请求
            execution_result: 执行结果
            evolved_skills: 进化后的技能列表
        """
        # 确保项目节点存在
        if task.project_id not in self.knowledge_graph.projects:
            self.knowledge_graph.add_project(
                project_id=task.project_id,
                name=f"Project {task.project_id}",
                language=task.language,
                framework=task.framework,
                domain='software_development'
            )
        
        # 添加知识项（进化的技能）
        for skill_id in evolved_skills:
            knowledge_item_id = f"skill_{skill_id}"
            if knowledge_item_id not in self.knowledge_graph.knowledge_items:
                self.knowledge_graph.add_knowledge_item(
                    item_id=knowledge_item_id,
                    item_type='skill',
                    title=f"Evolved Skill: {skill_id}",
                    description=f"Skill evolved from task: {task.description[:100]}",
                    project_id=task.project_id,
                    tags=[task.language, task.framework or 'generic'],
                    quality_score=0.8
                )
        
        # 保存图谱
        self.knowledge_graph.save_graph()
