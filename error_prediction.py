"""
实时错误预测与预防系统 (Real-time Error Prediction & Prevention System)

基于历史错误模式预测潜在风险，提供主动预防建议。
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from collections import defaultdict


class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """错误类别"""
    SYNTAX_ERROR = "syntax_error"
    RUNTIME_ERROR = "runtime_error"
    LOGIC_ERROR = "logic_error"
    CONFIGURATION_ERROR = "configuration_error"
    DEPENDENCY_ERROR = "dependency_error"
    RESOURCE_ERROR = "resource_error"
    TIMEOUT_ERROR = "timeout_error"
    SECURITY_ERROR = "security_error"


@dataclass
class ErrorPattern:
    """错误模式"""
    pattern_id: str
    category: str
    description: str
    common_causes: List[str] = field(default_factory=list)
    prevention_strategies: List[str] = field(default_factory=list)
    occurrence_count: int = 0
    avg_severity: float = 0.5
    affected_task_types: List[str] = field(default_factory=list)
    last_occurrence: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'pattern_id': self.pattern_id,
            'category': self.category,
            'description': self.description,
            'common_causes': self.common_causes,
            'prevention_strategies': self.prevention_strategies,
            'occurrence_count': self.occurrence_count,
            'avg_severity': self.avg_severity,
            'affected_task_types': self.affected_task_types,
            'last_occurrence': self.last_occurrence
        }


@dataclass
class ErrorPrediction:
    """错误预测结果"""
    task_id: str
    predicted_errors: List[Dict] = field(default_factory=list)
    overall_risk_score: float = 0.0
    confidence: float = 0.0
    prevention_suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'task_id': self.task_id,
            'predicted_errors': self.predicted_errors,
            'overall_risk_score': self.overall_risk_score,
            'confidence': self.confidence,
            'prevention_suggestions': self.prevention_suggestions
        }


@dataclass
class ErrorRecord:
    """错误记录"""
    error_id: str
    task_id: str
    task_type: str
    error_type: str
    error_message: str
    severity: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    context: Dict = field(default_factory=dict)
    resolution: Optional[str] = None
    prevention_applied: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'error_id': self.error_id,
            'task_id': self.task_id,
            'task_type': self.task_type,
            'error_type': self.error_type,
            'error_message': self.error_message,
            'severity': self.severity,
            'timestamp': self.timestamp,
            'context': self.context,
            'resolution': self.resolution,
            'prevention_applied': self.prevention_applied
        }


class ErrorPatternDatabase:
    """
    错误模式数据库
    
    存储和分析历史错误模式，支持模式匹配和趋势分析。
    """
    
    def __init__(self, storage_path: str = "./data/error_patterns"):
        self.storage_path = storage_path
        self.patterns: Dict[str, ErrorPattern] = {}
        self.error_records: List[ErrorRecord] = []
        
        self._ensure_storage()
        self._load_patterns()
    
    def _ensure_storage(self):
        """确保存储目录存在"""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def _load_patterns(self):
        """加载错误模式"""
        patterns_file = os.path.join(self.storage_path, "patterns.json")
        if os.path.exists(patterns_file):
            try:
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    for p_data in data.get('patterns', []):
                        pattern = ErrorPattern(**p_data)
                        self.patterns[pattern.pattern_id] = pattern
                    
                    for r_data in data.get('records', []):
                        record = ErrorRecord(**r_data)
                        self.error_records.append(record)
                    
                    print(f"📚 Loaded {len(self.patterns)} error patterns, "
                          f"{len(self.error_records)} records")
            except Exception as e:
                print(f"⚠️  Failed to load error patterns: {e}")
    
    def save_patterns(self):
        """保存错误模式"""
        patterns_file = os.path.join(self.storage_path, "patterns.json")
        try:
            data = {
                'patterns': [p.to_dict() for p in self.patterns.values()],
                'records': [r.to_dict() for r in self.error_records[-1000:]]  # 只保留最近1000条
            }
            
            with open(patterns_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved {len(self.patterns)} error patterns")
        except Exception as e:
            print(f"❌ Failed to save error patterns: {e}")
    
    def record_error(self, error_record: ErrorRecord):
        """
        记录错误
        
        Args:
            error_record: 错误记录
        """
        self.error_records.append(error_record)
        
        # 更新或创建错误模式
        self._update_error_pattern(error_record)
        
        # 定期保存
        if len(self.error_records) % 50 == 0:
            self.save_patterns()
    
    def _update_error_pattern(self, error_record: ErrorRecord):
        """更新错误模式"""
        # 使用错误类型作为模式ID
        pattern_id = error_record.error_type
        
        if pattern_id in self.patterns:
            # 更新现有模式
            pattern = self.patterns[pattern_id]
            pattern.occurrence_count += 1
            pattern.last_occurrence = error_record.timestamp
            
            # 更新平均严重程度
            severity_map = {'low': 0.25, 'medium': 0.5, 'high': 0.75, 'critical': 1.0}
            new_severity = severity_map.get(error_record.severity, 0.5)
            pattern.avg_severity = (
                (pattern.avg_severity * (pattern.occurrence_count - 1) + new_severity) /
                pattern.occurrence_count
            )
            
            # 添加任务类型
            if error_record.task_type not in pattern.affected_task_types:
                pattern.affected_task_types.append(error_record.task_type)
        else:
            # 创建新模式
            severity_map = {'low': 0.25, 'medium': 0.5, 'high': 0.75, 'critical': 1.0}
            
            pattern = ErrorPattern(
                pattern_id=pattern_id,
                category=error_record.error_type.split('_')[0] if '_' in error_record.error_type else 'unknown',
                description=f"Error pattern: {error_record.error_type}",
                occurrence_count=1,
                avg_severity=severity_map.get(error_record.severity, 0.5),
                affected_task_types=[error_record.task_type],
                last_occurrence=error_record.timestamp
            )
            
            self.patterns[pattern_id] = pattern
        
        print(f"📝 Recorded error: {error_record.error_type} (count: {pattern.occurrence_count})")
    
    def get_error_frequency(self, error_type: str, task_type: Optional[str] = None) -> float:
        """
        获取错误频率
        
        Args:
            error_type: 错误类型
            task_type: 任务类型（可选）
            
        Returns:
            错误频率（0.0-1.0）
        """
        if error_type not in self.patterns:
            return 0.0
        
        pattern = self.patterns[error_type]
        
        if task_type:
            # 计算该任务类型的错误比例
            total_for_task = sum(
                1 for r in self.error_records
                if r.task_type == task_type
            )
            errors_for_task = sum(
                1 for r in self.error_records
                if r.task_type == task_type and r.error_type == error_type
            )
            
            return errors_for_task / total_for_task if total_for_task > 0 else 0.0
        
        # 总体频率
        total_errors = sum(p.occurrence_count for p in self.patterns.values())
        return pattern.occurrence_count / total_errors if total_errors > 0 else 0.0
    
    def get_common_errors(self, task_type: Optional[str] = None, 
                         top_n: int = 10) -> List[ErrorPattern]:
        """
        获取常见错误
        
        Args:
            task_type: 任务类型（可选）
            top_n: 返回数量
            
        Returns:
            常见错误模式列表
        """
        if task_type:
            filtered = [
                p for p in self.patterns.values()
                if task_type in p.affected_task_types
            ]
        else:
            filtered = list(self.patterns.values())
        
        # 按出现次数排序
        filtered.sort(key=lambda x: x.occurrence_count, reverse=True)
        
        return filtered[:top_n]
    
    def get_prevention_strategies(self, error_type: str) -> List[str]:
        """
        获取预防策略
        
        Args:
            error_type: 错误类型
            
        Returns:
            预防策略列表
        """
        if error_type in self.patterns:
            return self.patterns[error_type].prevention_strategies
        return []
    
    def add_prevention_strategy(self, error_type: str, strategy: str):
        """
        添加预防策略
        
        Args:
            error_type: 错误类型
            strategy: 预防策略
        """
        if error_type in self.patterns:
            if strategy not in self.patterns[error_type].prevention_strategies:
                self.patterns[error_type].prevention_strategies.append(strategy)
                self.save_patterns()
                print(f"✅ Added prevention strategy for {error_type}: {strategy}")


class ErrorPredictor:
    """
    错误预测器
    
    基于历史错误模式预测任务执行中可能出现的错误。
    """
    
    def __init__(self, pattern_db: ErrorPatternDatabase):
        self.db = pattern_db
        self.risk_thresholds = {
            'low': 0.2,
            'medium': 0.4,
            'high': 0.6,
            'critical': 0.8
        }
    
    def predict_errors(self, task_id: str, task_type: str,
                      context: Optional[Dict] = None) -> ErrorPrediction:
        """
        预测可能的错误
        
        Args:
            task_id: 任务ID
            task_type: 任务类型
            context: 上下文信息
            
        Returns:
            错误预测结果
        """
        print(f"🔮 Predicting errors for task: {task_id} (type: {task_type})")
        
        # 获取该任务类型的常见错误
        common_errors = self.db.get_common_errors(task_type, top_n=10)
        
        predicted_errors = []
        total_risk = 0.0
        
        for pattern in common_errors:
            # 计算风险分数
            frequency = self.db.get_error_frequency(pattern.pattern_id, task_type)
            severity = pattern.avg_severity
            
            # 综合风险 = 频率 * 严重程度
            risk_score = frequency * severity
            
            if risk_score > 0.1:  # 只显示有显著风险的错误
                predicted_errors.append({
                    'error_type': pattern.pattern_id,
                    'category': pattern.category,
                    'description': pattern.description,
                    'risk_score': risk_score,
                    'severity': self._classify_severity(risk_score),
                    'common_causes': pattern.common_causes,
                    'prevention_strategies': pattern.prevention_strategies
                })
                
                total_risk += risk_score
        
        # 计算整体风险分数（归一化到 0-1）
        overall_risk = min(1.0, total_risk / len(common_errors)) if common_errors else 0.0
        
        # 生成预防建议
        prevention_suggestions = self._generate_prevention_suggestions(predicted_errors)
        
        # 计算置信度（基于历史数据量）
        total_records = len(self.db.error_records)
        confidence = min(1.0, total_records / 100.0)  # 100条记录达到100%置信度
        
        prediction = ErrorPrediction(
            task_id=task_id,
            predicted_errors=predicted_errors,
            overall_risk_score=overall_risk,
            confidence=confidence,
            prevention_suggestions=prevention_suggestions
        )
        
        print(f"   Overall Risk: {overall_risk:.2f}, Confidence: {confidence:.2%}")
        print(f"   Predicted Errors: {len(predicted_errors)}")
        
        return prediction
    
    def _classify_severity(self, risk_score: float) -> str:
        """分类严重程度"""
        if risk_score >= self.risk_thresholds['critical']:
            return ErrorSeverity.CRITICAL.value
        elif risk_score >= self.risk_thresholds['high']:
            return ErrorSeverity.HIGH.value
        elif risk_score >= self.risk_thresholds['medium']:
            return ErrorSeverity.MEDIUM.value
        else:
            return ErrorSeverity.LOW.value
    
    def _generate_prevention_suggestions(self, predicted_errors: List[Dict]) -> List[str]:
        """生成预防建议"""
        suggestions = []
        
        # 收集所有预防策略
        all_strategies = set()
        for error in predicted_errors:
            for strategy in error.get('prevention_strategies', []):
                all_strategies.add(strategy)
        
        # 根据风险等级排序
        high_risk_errors = [e for e in predicted_errors if e['severity'] in ['high', 'critical']]
        
        if high_risk_errors:
            suggestions.append("⚠️  High-risk errors detected. Consider the following:")
            for error in high_risk_errors[:3]:  # 只显示前3个高风险错误
                suggestions.append(f"   - {error['description']}")
                for strategy in error.get('prevention_strategies', [])[:2]:
                    suggestions.append(f"     • {strategy}")
        
        if all_strategies:
            suggestions.append("\n🛡️  General Prevention Strategies:")
            for strategy in list(all_strategies)[:5]:  # 最多5个通用策略
                suggestions.append(f"   • {strategy}")
        
        if not suggestions:
            suggestions.append("✅ No significant risks detected. Proceed with caution.")
        
        return suggestions
    
    def suggest_dynamic_adjustment(self, prediction: ErrorPrediction) -> Dict:
        """
        建议动态调整策略
        
        Args:
            prediction: 错误预测结果
            
        Returns:
            调整建议
        """
        if prediction.overall_risk_score < 0.3:
            return {
                'action': 'proceed',
                'message': 'Risk is low, proceed normally'
            }
        elif prediction.overall_risk_score < 0.6:
            return {
                'action': 'caution',
                'message': 'Moderate risk detected, enable additional monitoring',
                'recommendations': [
                    'Enable verbose logging',
                    'Set shorter timeout thresholds',
                    'Prepare fallback strategies'
                ]
            }
        else:
            return {
                'action': 'review',
                'message': 'High risk detected, manual review recommended',
                'recommendations': [
                    'Review task requirements',
                    'Break down into smaller subtasks',
                    'Apply all prevention strategies',
                    'Consider alternative approaches'
                ]
            }


class RealTimeErrorPreventionSystem:
    """
    实时错误预防系统
    
    整合错误模式数据库和预测器，提供完整的错误预防能力。
    """
    
    def __init__(self, config: Dict):
        storage_path = config.get('storage_path', './data/error_patterns')
        self.db = ErrorPatternDatabase(storage_path)
        self.predictor = ErrorPredictor(self.db)
        
        # 初始化常见错误的预防策略
        self._initialize_prevention_strategies()
    
    def _initialize_prevention_strategies(self):
        """初始化常见错误的预防策略"""
        default_strategies = {
            'syntax_error': [
                'Use linter before execution',
                'Validate code syntax with AST parser',
                'Check for common syntax mistakes'
            ],
            'runtime_error': [
                'Add comprehensive error handling',
                'Validate input parameters',
                'Check resource availability'
            ],
            'timeout_error': [
                'Optimize algorithm complexity',
                'Implement progress checkpoints',
                'Set appropriate timeout values'
            ],
            'dependency_error': [
                'Verify all dependencies are installed',
                'Check version compatibility',
                'Use virtual environments'
            ],
            'configuration_error': [
                'Validate configuration files',
                'Use schema validation',
                'Provide default values'
            ]
        }
        
        for error_type, strategies in default_strategies.items():
            for strategy in strategies:
                self.db.add_prevention_strategy(error_type, strategy)
    
    async def predict_and_prevent(self, task_id: str, task_type: str,
                                 context: Optional[Dict] = None) -> Dict:
        """
        预测并预防错误
        
        Args:
            task_id: 任务ID
            task_type: 任务类型
            context: 上下文信息
            
        Returns:
            预测结果和预防建议
        """
        # 预测错误
        prediction = self.predictor.predict_errors(task_id, task_type, context)
        
        # 获取调整建议
        adjustment = self.predictor.suggest_dynamic_adjustment(prediction)
        
        result = {
            'prediction': prediction.to_dict(),
            'adjustment': adjustment,
            'should_proceed': prediction.overall_risk_score < 0.7 or adjustment['action'] != 'review'
        }
        
        return result
    
    def record_execution_error(self, task_id: str, task_type: str,
                              error_type: str, error_message: str,
                              severity: str = 'medium',
                              context: Optional[Dict] = None,
                              resolution: Optional[str] = None):
        """
        记录执行错误
        
        Args:
            task_id: 任务ID
            task_type: 任务类型
            error_type: 错误类型
            error_message: 错误消息
            severity: 严重程度
            context: 上下文
            resolution: 解决方案
        """
        import uuid
        
        error_record = ErrorRecord(
            error_id=str(uuid.uuid4()),
            task_id=task_id,
            task_type=task_type,
            error_type=error_type,
            error_message=error_message,
            severity=severity,
            context=context or {},
            resolution=resolution
        )
        
        self.db.record_error(error_record)
    
    def get_error_analytics(self, task_type: Optional[str] = None) -> Dict:
        """
        获取错误分析
        
        Args:
            task_type: 任务类型（可选）
            
        Returns:
            分析结果
        """
        common_errors = self.db.get_common_errors(task_type, top_n=10)
        
        analytics = {
            'total_error_patterns': len(self.db.patterns),
            'total_error_records': len(self.db.error_records),
            'most_common_errors': [
                {
                    'error_type': p.pattern_id,
                    'occurrence_count': p.occurrence_count,
                    'avg_severity': p.avg_severity
                }
                for p in common_errors
            ]
        }
        
        return analytics
    
    def save_state(self):
        """保存状态"""
        self.db.save_patterns()
    
    def load_state(self):
        """加载状态"""
        self.db._load_patterns()
