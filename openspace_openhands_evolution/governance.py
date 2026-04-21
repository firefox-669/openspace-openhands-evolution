"""
治理层 - 四阶段治理流程实现

负责：
- Gatekeeping: 准入控制
- Runtime Monitoring: 运行监控（与 Monitor 协作）
- Maintenance: 定期维护
- Evolution: 进化优化
"""

from typing import Dict, List, Optional
from datetime import datetime
import asyncio


class Gatekeeper:
    """准入控制器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get('enable_gatekeeping', True)
        self.blocked_tasks = []
    
    async def validate_task(self, task) -> tuple[bool, Optional[str]]:
        """
        验证任务是否符合准入条件
        
        Returns:
            (是否通过, 拒绝原因)
        """
        if not self.enabled:
            return True, None
        
        # 检查 1: 任务描述不能为空
        if not hasattr(task, 'description') or not task.description:
            return False, "Task description is required"
        
        # 检查 2: 项目 ID 不能为空
        if not hasattr(task, 'project_id') or not task.project_id:
            return False, "Project ID is required"
        
        # 检查 3: 语言必须是支持的
        supported_languages = ['python', 'javascript', 'typescript', 'java', 'go']
        language = getattr(task, 'language', 'python')
        if language not in supported_languages:
            return False, f"Unsupported language: {language}"
        
        # 检查 4: 迭代次数不能超过限制
        max_iterations = getattr(task, 'max_iterations', 10)
        if max_iterations > 50:
            return False, f"Max iterations ({max_iterations}) exceeds limit (50)"
        
        return True, None
    
    async def check_environment_compatibility(self, task, env_fingerprint: Dict) -> tuple[bool, Optional[str]]:
        """
        检查环境兼容性（V-06）
        
        Returns:
            (是否兼容, 不兼容原因)
        """
        # 简化实现：总是通过
        # 在实际实现中，应该比较当前环境与技能所需环境
        return True, None


class Maintainer:
    """维护器 - 定期维护任务"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.maintenance_log = []
    
    async def cleanup_old_memories(self, project_id: str, days_to_keep: int = 30):
        """清理旧的记忆"""
        # TODO: 实现记忆清理逻辑
        print(f"🧹 Cleaning up memories older than {days_to_keep} days for {project_id}")
    
    async def scheduled_maintenance(self):
        """执行定期维护任务"""
        print("Running scheduled maintenance...")
        await self.optimize_skill_registry()
        # TODO: 添加更多维护任务
        print("Scheduled maintenance completed")
    
    async def optimize_skill_registry(self):
        """优化技能注册表"""
        print("🔧 Optimizing skill registry...")
    
    async def rollback(self, task_id: str):
        """
        回滚任务
        
        Args:
            task_id: 任务 ID
        """
        rollback_entry = {
            "task_id": task_id,
            "timestamp": datetime.utcnow().isoformat(),
            "action": "rollback",
            "reason": "Task failure"
        }
        self.maintenance_log.append(rollback_entry)
        print(f"↩️  Rolled back task {task_id}")


class Evolver:
    """进化器 - 技能进化优化"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.evolution_history = []
    
    async def evolve_from_failure(self, task, error_context: Dict):
        """
        从失败中学习并进化
        
        Args:
            task: 失败的任务
            error_context: 错误上下文
            
        Returns:
            进化后的技能列表
        """
        evolution_entry = {
            "task_id": getattr(task, 'id', 'unknown'),
            "timestamp": datetime.utcnow().isoformat(),
            "type": "failure_learning",
            "error": error_context.get('error', 'Unknown'),
            "improvements": []
        }
        
        # TODO: 分析失败原因，生成改进建议
        improvement = {
            "suggestion": "Add better error handling",
            "priority": "high"
        }
        evolution_entry["improvements"].append(improvement)
        
        self.evolution_history.append(evolution_entry)
        
        print(f"🧬 Learning from failure: {improvement['suggestion']}")
        
        return [improvement]
    
    async def optimize_successful_skill(self, skill_id: str, quality_score: float):
        """
        优化成功的技能
        
        Args:
            skill_id: 技能 ID
            quality_score: 质量评分
        """
        if quality_score > 0.9:
            # 高质量技能，标记为优秀
            print(f"⭐ Skill {skill_id} marked as excellent (score: {quality_score:.2f})")
        elif quality_score > 0.7:
            # 中等质量，可以进一步优化
            print(f"📈 Skill {skill_id} has room for improvement (score: {quality_score:.2f})")
        
        evolution_entry = {
            "skill_id": skill_id,
            "timestamp": datetime.utcnow().isoformat(),
            "type": "optimization",
            "quality_score": quality_score
        }
        self.evolution_history.append(evolution_entry)


class GovernanceLayer:
    """治理层 - 协调所有治理组件"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.gatekeeper = Gatekeeper(config)
        self.maintainer = Maintainer(config)
        self.evolver = Evolver(config)
        
        # 治理统计
        self.total_validations = 0
        self.total_rejections = 0
        self.total_evolutions = 0
    
    async def validate_and_approve(self, task) -> tuple[bool, Optional[str]]:
        """
        验证并批准任务（阶段 1: Gatekeeping）
        
        Returns:
            (是否批准, 拒绝原因)
        """
        self.total_validations += 1
        
        # 基本验证
        approved, reason = await self.gatekeeper.validate_task(task)
        
        if not approved:
            self.total_rejections += 1
            print(f"❌ Task rejected: {reason}")
            return False, reason
        
        print("✅ Task approved by gatekeeper")
        return True, None
    
    async def maintain_background(self):
        """后台维护任务（阶段 3: Maintenance）"""
        print("🔧 Running background maintenance...")
        
        # 执行维护任务
        await self.maintainer.optimize_skill_registry()
        
        # TODO: 定期清理、优化等
    
    async def evolve_after_execution(self, task, execution_result: Dict, quality_metrics: Dict):
        """
        执行后进化（阶段 4: Evolution）
        
        Args:
            task: 执行的任务
            execution_result: 执行结果
            quality_metrics: 质量指标
            
        Returns:
            进化产生的改进列表
        """
        improvements = []
        
        # 如果执行失败，从失败中学习
        if not execution_result.get('success', False):
            error_context = {
                "error": execution_result.get('error', 'Unknown error'),
                "output": execution_result.get('output', '')
            }
            evolved = await self.evolver.evolve_from_failure(task, error_context)
            improvements.extend(evolved)
        
        # 如果执行成功但质量不高，优化技能
        quality_score = quality_metrics.get('overall_score', 0)
        if execution_result.get('success') and quality_score < 0.8:
            print(f"⚠️  Execution succeeded but quality is low ({quality_score:.2f})")
            # TODO: 触发技能优化
        
        self.total_evolutions += len(improvements)
        
        return improvements
    
    async def get_status(self) -> Dict:
        """获取治理层状态"""
        return {
            "status": "running",
            "gatekeeper_enabled": self.gatekeeper.enabled,
            "total_validations": self.total_validations,
            "total_rejections": self.total_rejections,
            "total_evolutions": self.total_evolutions,
            "approval_rate": round(
                (self.total_validations - self.total_rejections) / self.total_validations * 100
                if self.total_validations > 0 else 0, 2
            )
        }
