"""
智能执行策略引擎 (Intelligent Execution Strategy Engine)

提供基于历史数据的策略选择、回溯和预测功能。
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
import os


class StrategyType(Enum):
    """策略类型"""
    CONSERVATIVE = "conservative"  # 保守策略：稳定但慢
    AGGRESSIVE = "aggressive"      # 激进策略：快速但有风险
    BALANCED = "balanced"          # 平衡策略
    EXPERIMENTAL = "experimental"  # 实验性策略


@dataclass
class StrategyRecord:
    """策略执行记录"""
    task_id: str
    task_type: str
    strategy_type: str
    success: bool
    execution_time: float
    quality_score: float
    error_type: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    context: Dict = field(default_factory=dict)


class StrategyHistory:
    """
    策略历史记录器
    
    记录每次任务执行的策略选择和效果，用于后续分析和预测。
    """
    
    def __init__(self, storage_path: str = "./data/strategy_history"):
        self.storage_path = storage_path
        self.records: List[StrategyRecord] = []
        self._ensure_storage()
        self._load_history()
    
    def _ensure_storage(self):
        """确保存储目录存在"""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def _load_history(self):
        """加载历史记录"""
        history_file = os.path.join(self.storage_path, "history.json")
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.records = [StrategyRecord(**r) for r in data]
                print(f"📚 Loaded {len(self.records)} strategy records")
            except Exception as e:
                print(f"⚠️  Failed to load history: {e}")
                self.records = []
    
    def save_history(self):
        """保存历史记录"""
        history_file = os.path.join(self.storage_path, "history.json")
        try:
            data = [r.__dict__ for r in self.records]
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved {len(self.records)} strategy records")
        except Exception as e:
            print(f"❌ Failed to save history: {e}")
    
    def record_execution(self, record: StrategyRecord):
        """
        记录一次策略执行
        
        Args:
            record: 策略执行记录
        """
        self.records.append(record)
        
        # 定期保存（每10条记录）
        if len(self.records) % 10 == 0:
            self.save_history()
    
    def get_success_rate(self, strategy_type: str, task_type: Optional[str] = None) -> float:
        """
        计算某策略的成功率
        
        Args:
            strategy_type: 策略类型
            task_type: 任务类型（可选）
            
        Returns:
            成功率 (0.0-1.0)
        """
        filtered = [r for r in self.records if r.strategy_type == strategy_type]
        
        if task_type:
            filtered = [r for r in filtered if r.task_type == task_type]
        
        if not filtered:
            return 0.5  # 默认值
        
        success_count = sum(1 for r in filtered if r.success)
        return success_count / len(filtered)
    
    def get_avg_execution_time(self, strategy_type: str, task_type: Optional[str] = None) -> float:
        """
        计算某策略的平均执行时间
        
        Args:
            strategy_type: 策略类型
            task_type: 任务类型（可选）
            
        Returns:
            平均执行时间（秒）
        """
        filtered = [r for r in self.records if r.strategy_type == strategy_type]
        
        if task_type:
            filtered = [r for r in filtered if r.task_type == task_type]
        
        if not filtered:
            return 30.0  # 默认值
        
        total_time = sum(r.execution_time for r in filtered)
        return total_time / len(filtered)
    
    def get_avg_quality_score(self, strategy_type: str, task_type: Optional[str] = None) -> float:
        """
        计算某策略的平均质量分数
        
        Args:
            strategy_type: 策略类型
            task_type: 任务类型（可选）
            
        Returns:
            平均质量分数 (0.0-1.0)
        """
        filtered = [r for r in self.records if r.strategy_type == strategy_type]
        
        if task_type:
            filtered = [r for r in filtered if r.task_type == task_type]
        
        if not filtered:
            return 0.7  # 默认值
        
        total_quality = sum(r.quality_score for r in filtered)
        return total_quality / len(filtered)
    
    def get_error_patterns(self, strategy_type: str) -> Dict[str, int]:
        """
        获取某策略的错误模式统计
        
        Args:
            strategy_type: 策略类型
            
        Returns:
            错误类型 -> 出现次数的字典
        """
        filtered = [r for r in self.records if r.strategy_type == strategy_type and not r.success]
        
        error_counts = {}
        for r in filtered:
            if r.error_type:
                error_counts[r.error_type] = error_counts.get(r.error_type, 0) + 1
        
        return error_counts
    
    def get_recent_records(self, count: int = 50) -> List[StrategyRecord]:
        """获取最近的记录"""
        return self.records[-count:]


class PredictiveStrategySelector:
    """
    预测性策略选择器
    
    基于历史数据预测最优策略，支持自适应调整。
    """
    
    def __init__(self, strategy_history: StrategyHistory):
        self.history = strategy_history
        self.weights = {
            'success_rate': 0.4,
            'execution_time': 0.3,
            'quality_score': 0.3
        }
    
    def predict_best_strategy(self, task_type: str, priority: str = "balanced") -> Tuple[str, Dict]:
        """
        预测最优策略
        
        Args:
            task_type: 任务类型
            priority: 优先级 ("speed", "quality", "balanced")
            
        Returns:
            (最佳策略类型, 详细评估信息)
        """
        strategies = [s.value for s in StrategyType]
        
        # 根据优先级调整权重
        if priority == "speed":
            weights = {'success_rate': 0.3, 'execution_time': 0.5, 'quality_score': 0.2}
        elif priority == "quality":
            weights = {'success_rate': 0.3, 'execution_time': 0.2, 'quality_score': 0.5}
        else:  # balanced
            weights = self.weights
        
        best_strategy = None
        best_score = -1
        evaluations = {}
        
        for strategy in strategies:
            # 计算综合评分
            success_rate = self.history.get_success_rate(strategy, task_type)
            avg_time = self.history.get_avg_execution_time(strategy, task_type)
            avg_quality = self.history.get_avg_quality_score(strategy, task_type)
            
            # 归一化执行时间（越短越好）
            normalized_time = max(0, 1 - (avg_time / 60.0))  # 假设60秒为基准
            
            # 加权评分
            score = (
                weights['success_rate'] * success_rate +
                weights['execution_time'] * normalized_time +
                weights['quality_score'] * avg_quality
            )
            
            evaluations[strategy] = {
                'score': score,
                'success_rate': success_rate,
                'avg_execution_time': avg_time,
                'avg_quality_score': avg_quality
            }
            
            if score > best_score:
                best_score = score
                best_strategy = strategy
        
        return best_strategy, evaluations
    
    def suggest_strategy_adjustment(self, current_strategy: str, task_type: str) -> Dict:
        """
        建议策略调整
        
        Args:
            current_strategy: 当前使用的策略
            task_type: 任务类型
            
        Returns:
            调整建议
        """
        best_strategy, evaluations = self.predict_best_strategy(task_type)
        
        current_eval = evaluations.get(current_strategy, {})
        best_eval = evaluations.get(best_strategy, {})
        
        improvement_potential = best_eval.get('score', 0) - current_eval.get('score', 0)
        
        return {
            'current_strategy': current_strategy,
            'recommended_strategy': best_strategy,
            'improvement_potential': improvement_potential,
            'should_switch': improvement_potential > 0.1,  # 提升超过10%才建议切换
            'reason': self._generate_recommendation_reason(
                current_eval, best_eval, improvement_potential
            )
        }
    
    def _generate_recommendation_reason(self, current_eval: Dict, best_eval: Dict, improvement: float) -> str:
        """生成推荐理由"""
        if improvement <= 0:
            return "当前策略已经是最优选择"
        
        reasons = []
        
        if best_eval.get('success_rate', 0) > current_eval.get('success_rate', 0) + 0.1:
            reasons.append(f"成功率可提升 {(best_eval['success_rate'] - current_eval['success_rate']) * 100:.1f}%")
        
        if best_eval.get('avg_execution_time', 60) < current_eval.get('avg_execution_time', 60) * 0.8:
            time_saved = current_eval['avg_execution_time'] - best_eval['avg_execution_time']
            reasons.append(f"执行时间可减少 {time_saved:.1f}秒")
        
        if best_eval.get('avg_quality_score', 0) > current_eval.get('avg_quality_score', 0) + 0.1:
            reasons.append(f"质量分数可提升 {(best_eval['avg_quality_score'] - current_eval['avg_quality_score']) * 100:.1f}%")
        
        return "; ".join(reasons) if reasons else "综合评分更高"
    
    def get_strategy_performance_report(self, task_type: Optional[str] = None) -> Dict:
        """
        生成策略性能报告
        
        Args:
            task_type: 任务类型（可选）
            
        Returns:
            性能报告
        """
        strategies = [s.value for s in StrategyType]
        report = {}
        
        for strategy in strategies:
            report[strategy] = {
                'success_rate': self.history.get_success_rate(strategy, task_type),
                'avg_execution_time': self.history.get_avg_execution_time(strategy, task_type),
                'avg_quality_score': self.history.get_avg_quality_score(strategy, task_type),
                'error_patterns': self.history.get_error_patterns(strategy),
                'total_executions': len([
                    r for r in self.history.records 
                    if r.strategy_type == strategy and (not task_type or r.task_type == task_type)
                ])
            }
        
        return report


class IntelligentExecutionStrategyEngine:
    """
    智能执行策略引擎
    
    整合策略历史记录和预测选择，提供完整的策略管理能力。
    """
    
    def __init__(self, config: Dict):
        storage_path = config.get('storage_path', './data/strategy_history')
        self.history = StrategyHistory(storage_path)
        self.selector = PredictiveStrategySelector(self.history)
        self.current_strategy = config.get('default_strategy', 'balanced')
    
    async def select_strategy(self, task_type: str, priority: str = "balanced") -> str:
        """
        为任务选择最优策略
        
        Args:
            task_type: 任务类型
            priority: 优先级
            
        Returns:
            选择的策略类型
        """
        best_strategy, evaluations = self.selector.predict_best_strategy(task_type, priority)
        
        print(f"🎯 Selected strategy: {best_strategy} for task type: {task_type}")
        print(f"   Evaluations: {evaluations}")
        
        return best_strategy
    
    async def record_execution_result(self, task_id: str, task_type: str, 
                                     strategy_type: str, success: bool,
                                     execution_time: float, quality_score: float,
                                     error_type: Optional[str] = None,
                                     context: Optional[Dict] = None):
        """
        记录执行结果
        
        Args:
            task_id: 任务ID
            task_type: 任务类型
            strategy_type: 使用的策略
            success: 是否成功
            execution_time: 执行时间
            quality_score: 质量分数
            error_type: 错误类型（如果失败）
            context: 上下文信息
        """
        record = StrategyRecord(
            task_id=task_id,
            task_type=task_type,
            strategy_type=strategy_type,
            success=success,
            execution_time=execution_time,
            quality_score=quality_score,
            error_type=error_type,
            context=context or {}
        )
        
        self.history.record_execution(record)
        print(f"📝 Recorded execution: {task_id} - {strategy_type} - {'✅' if success else '❌'}")
    
    async def get_adjustment_suggestion(self, task_type: str) -> Dict:
        """
        获取策略调整建议
        
        Args:
            task_type: 任务类型
            
        Returns:
            调整建议
        """
        suggestion = self.selector.suggest_strategy_adjustment(
            self.current_strategy, task_type
        )
        
        if suggestion['should_switch']:
            print(f"💡 Strategy adjustment suggested:")
            print(f"   Current: {suggestion['current_strategy']}")
            print(f"   Recommended: {suggestion['recommended_strategy']}")
            print(f"   Reason: {suggestion['reason']}")
            self.current_strategy = suggestion['recommended_strategy']
        
        return suggestion
    
    async def get_performance_report(self, task_type: Optional[str] = None) -> Dict:
        """
        获取性能报告
        
        Args:
            task_type: 任务类型（可选）
            
        Returns:
            性能报告
        """
        report = self.selector.get_strategy_performance_report(task_type)
        
        print(f"📊 Strategy Performance Report:")
        for strategy, metrics in report.items():
            print(f"   {strategy}:")
            print(f"      Success Rate: {metrics['success_rate']:.2%}")
            print(f"      Avg Time: {metrics['avg_execution_time']:.1f}s")
            print(f"      Avg Quality: {metrics['avg_quality_score']:.2f}")
            print(f"      Executions: {metrics['total_executions']}")
        
        return report
    
    def save_state(self):
        """保存状态"""
        self.history.save_history()
    
    def load_state(self):
        """加载状态"""
        self.history._load_history()
