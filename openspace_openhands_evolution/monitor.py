"""
监控系统 - 质量评估与异常检测

负责：
- 实时监控任务执行质量
- 异常检测与告警
- 性能指标收集
- 错误日志记录
"""

from typing import Dict, List, Optional
from datetime import datetime
import asyncio


class MonitorSystem:
    """监控系统的核心实现"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.quality_threshold = config.get('quality_threshold', 0.8)
        self.metrics_history: List[Dict] = []
        self.error_log: List[Dict] = []
        self.alerts: List[Dict] = []
        
        # 性能指标
        self.total_tasks_monitored = 0
        self.total_errors_detected = 0
        self.avg_quality_score = 0.0
    
    async def monitor_execution(self, execution_result: Dict) -> Dict:
        """
        监控任务执行
        
        Args:
            execution_result: 执行结果
            
        Returns:
            质量评估指标
        """
        self.total_tasks_monitored += 1
        
        # 计算质量指标
        quality_metrics = self._calculate_quality_metrics(execution_result)
        
        # 检查是否低于阈值
        if quality_metrics['overall_score'] < self.quality_threshold:
            await self._trigger_alert(
                alert_type="low_quality",
                message=f"Quality score {quality_metrics['overall_score']:.2f} below threshold {self.quality_threshold}",
                severity="warning",
                metrics=quality_metrics
            )
        
        # 记录指标历史
        self.metrics_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": quality_metrics
        })
        
        return quality_metrics
    
    def _calculate_quality_metrics(self, execution_result: Dict) -> Dict:
        """
        计算质量指标
        
        Returns:
            质量指标字典
        """
        success = execution_result.get('success', False)
        metrics = execution_result.get('metrics', {})
        
        # 基础指标
        base_score = 0.8 if success else 0.3
        
        # 考虑置信度
        confidence = metrics.get('confidence_score', 0.5)
        
        # 考虑执行时间（越快越好，但有上限）
        exec_time = metrics.get('execution_time', 1.0)
        time_score = max(0.5, min(1.0, 2.0 / (exec_time + 1.0)))
        
        # 综合评分
        overall_score = (base_score * 0.5 + confidence * 0.3 + time_score * 0.2)
        
        return {
            "overall_score": round(overall_score, 2),
            "success": success,
            "confidence": round(confidence, 2),
            "execution_time": round(exec_time, 2),
            "time_score": round(time_score, 2),
            "meets_threshold": overall_score >= self.quality_threshold
        }
    
    async def log_error(self, error: Exception, context: Dict = None):
        """
        记录错误
        
        Args:
            error: 异常对象
            context: 错误上下文
        """
        self.total_errors_detected += 1
        
        error_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        
        self.error_log.append(error_entry)
        
        # 如果错误频繁，触发告警
        if self.total_errors_detected > 5:
            await self._trigger_alert(
                alert_type="frequent_errors",
                message=f"Detected {self.total_errors_detected} errors",
                severity="critical",
                error_count=self.total_errors_detected
            )
        
        print(f"⚠️  Error logged: {type(error).__name__}: {str(error)}")
    
    async def _trigger_alert(self, alert_type: str, message: str, 
                            severity: str, **kwargs):
        """
        触发告警
        
        Args:
            alert_type: 告警类型
            message: 告警消息
            severity: 严重程度 (info, warning, critical)
            **kwargs: 额外信息
        """
        alert = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": alert_type,
            "message": message,
            "severity": severity,
            **kwargs
        }
        
        self.alerts.append(alert)
        
        # 打印告警
        severity_icon = {
            "info": "ℹ️",
            "warning": "⚠️",
            "critical": "🚨"
        }.get(severity, "❓")
        
        print(f"{severity_icon} ALERT [{severity.upper()}]: {message}")
    
    async def get_performance_report(self) -> Dict:
        """
        获取性能报告
        
        Returns:
            性能报告字典
        """
        if not self.metrics_history:
            return {
                "total_tasks": 0,
                "avg_quality": 0.0,
                "error_rate": 0.0,
                "alerts_count": 0
            }
        
        # 计算平均质量
        recent_metrics = self.metrics_history[-100:]  # 最近 100 次
        avg_quality = sum(
            m['metrics']['overall_score'] for m in recent_metrics
        ) / len(recent_metrics)
        
        # 计算错误率
        error_rate = (
            self.total_errors_detected / self.total_tasks_monitored * 100
            if self.total_tasks_monitored > 0 else 0
        )
        
        return {
            "total_tasks": self.total_tasks_monitored,
            "avg_quality": round(avg_quality, 2),
            "error_rate": round(error_rate, 2),
            "total_errors": self.total_errors_detected,
            "alerts_count": len(self.alerts),
            "recent_alerts": self.alerts[-5:]  # 最近 5 个告警
        }
    
    async def get_status(self) -> Dict:
        """获取监控系统状态"""
        return {
            "status": "running",
            "quality_threshold": self.quality_threshold,
            "tasks_monitored": self.total_tasks_monitored,
            "errors_detected": self.total_errors_detected,
            "active_alerts": len([a for a in self.alerts if a['severity'] in ['warning', 'critical']])
        }
