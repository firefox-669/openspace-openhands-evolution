"""
OpenSpace-OpenHands-Evolution 核心编排器

负责协调 OpenSpace（记忆/进化）和 OpenHands（执行）的协作，
实现四阶段治理流程和跨项目技能迁移。
"""

import asyncio
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from .openspace_engine import OpenSpaceEngine
from .openhands_engine import OpenHandsEngine
from .monitor import MonitorSystem
from .governance import GovernanceLayer
from .mtl_adapter import MTLAdapter
from .aaip_protocol import AAIPProtocol


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
        self.openhands_engine = OpenHandsEngine(config.get('openhands', {}))
        self.monitor = MonitorSystem(config.get('monitor', {}))
        self.governance = GovernanceLayer(config.get('governance', {}))
        
        # 初始化工具适配器
        self.mtl_adapter = MTLAdapter(config.get('mtl', {}))
        self.aaip_protocol = AAIPProtocol(config.get('aaip', {}))
        
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
            await self._phase1_gatekeeping(task)
            
            # === 阶段 2: 任务规划与执行 ===
            print("⚙️  Phase 2: Task Execution...")
            execution_result = await self._phase2_execute(task)
            
            # === 阶段 3: 运行监控 ===
            print("📊 Phase 3: Runtime Monitoring...")
            quality_metrics = await self._phase3_monitor(execution_result)
            
            # === 阶段 4: 进化优化 ===
            print("🧬 Phase 4: Evolution...")
            evolved_skills = await self._phase4_evolve(
                task=task,
                execution_result=execution_result,
                quality_metrics=quality_metrics
            )
            
            # 启动后台维护任务
            asyncio.create_task(self._background_maintenance())
            
            return TaskResult(
                success=execution_result.get('success', False),
                output=execution_result.get('output', ''),
                metrics=quality_metrics,
                evolved_skills=evolved_skills
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
        
        - 从 OpenSpace 检索相关技能
        - 通过 MTL 适配技能到当前项目
        - 注入技能到 OpenHands
        - 执行任务
        """
        # 1. 检索相关技能
        relevant_skills = await self.openspace_engine.search_skills(
            query=task.description,
            context={
                "project": task.project_id,
                "language": task.language,
                "framework": task.framework
            }
        )
        
        print(f"   Found {len(relevant_skills)} relevant skills")
        
        # 2. 通过 MTL 适配技能
        if relevant_skills and task.project_id:
            adapted_skills = await self.mtl_adapter.transfer_skills(
                source_skills=relevant_skills,
                target_project=task.project_id,
                similarity_threshold=0.7
            )
            print(f"   Adapted {len(adapted_skills)} skills for target project")
        else:
            adapted_skills = relevant_skills
        
        # 3. 注入技能到 OpenHands
        if adapted_skills:
            await self.openhands_engine.inject_skills(adapted_skills)
        
        # 4. 执行任务
        execution_result = await self.openhands_engine.execute(
            task=task,
            skills=adapted_skills
        )
        
        print(f"   Execution {'succeeded' if execution_result['success'] else 'failed'}")
        
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
        
        # 2. MTL: 计算任务结构相似度
        similarity_matrix = await self.mtl_adapter.compute_similarity(
            source_project=transfer_request.source_project,
            target_project=transfer_request.target_project
        )
        
        # 3. 过滤高相似度技能
        transferable_skills = await self.mtl_adapter.filter_by_similarity(
            skills=source_skills,
            similarity_matrix=similarity_matrix,
            threshold=transfer_request.min_similarity
        )
        
        print(f"   Filtered to {len(transferable_skills)} transferable skills")
        
        # 4. AAIP: 标准化技能格式
        standardized_skills = await self.aaip_protocol.standardize(transferable_skills)
        
        # 5. 负迁移检测 (V-02)
        risk_assessment = await self.governance.gatekeeper.assess_negative_transfer(
            skills=standardized_skills,
            target_project=transfer_request.target_project
        )
        
        if risk_assessment.get('risk_level') in ['high', 'critical']:
            raise NegativeTransferRiskError(risk_assessment)
        
        print(f"   Risk assessment: {risk_assessment.get('risk_level')}")
        
        # 6. 导入到目标项目
        await self.openspace_engine.import_skills(
            project_id=transfer_request.target_project,
            skills=standardized_skills
        )
        
        print(f"   ✅ Transferred {len(standardized_skills)} skills successfully")
        
        return TransferResult(
            transferred_count=len(standardized_skills),
            risk_assessment=risk_assessment
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
    
    async def predict_failure(self, task: TaskRequest) -> Dict:
        """
        预测任务失败风险
        
        Args:
            task: 任务请求
            
        Returns:
            失败预测结果
        """
        return await self.monitor.predict_failure(
            task=task,
            context=task.context
        )
    
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
            "timestamp": datetime.utcnow().isoformat()
        }
