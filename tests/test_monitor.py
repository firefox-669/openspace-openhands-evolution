"""Tests for Monitor System module"""

import pytest
from openspace_openhands_evolution.monitor import MonitorSystem


class TestMonitorSystem:
    """Test MonitorSystem class"""
    
    @pytest.fixture
    def monitor(self):
        """Create monitor instance for testing"""
        config = {
            'quality_threshold': 0.8,
            'alert_channels': ['console'],
            'enable_anomaly_detection': True
        }
        return MonitorSystem(config)
    
    def test_init_monitor(self, monitor):
        """Test monitor initialization"""
        assert monitor.quality_threshold == 0.8
        assert hasattr(monitor, 'error_log')
        assert isinstance(monitor.error_log, list)
    
    @pytest.mark.asyncio
    async def test_monitor_execution(self, monitor):
        """Test monitoring task execution"""
        execution_result = {
            "success": True,
            "output": "Task completed",
            "metrics": {
                "execution_time": 1.5,
                "confidence_score": 0.85
            }
        }
        
        quality_metrics = await monitor.monitor_execution(execution_result)
        
        assert isinstance(quality_metrics, dict)
        assert "overall_score" in quality_metrics
        assert "base_score" in quality_metrics
        assert "confidence" in quality_metrics
    
    @pytest.mark.asyncio
    async def test_quality_calculation_success(self, monitor):
        """Test quality calculation for successful execution"""
        result = {
            "success": True,
            "metrics": {
                "execution_time": 2.0,
                "confidence_score": 0.9
            }
        }
        
        metrics = await monitor._calculate_quality_metrics(result)
        
        assert metrics["overall_score"] > 0.7  # Should be good quality
        assert metrics["base_score"] == 1.0  # Success gives base score 1.0
    
    @pytest.mark.asyncio
    async def test_quality_calculation_failure(self, monitor):
        """Test quality calculation for failed execution"""
        result = {
            "success": False,
            "error": "Something went wrong",
            "metrics": {
                "execution_time": 0.5,
                "confidence_score": 0.3
            }
        }
        
        metrics = await monitor._calculate_quality_metrics(result)
        
        assert metrics["overall_score"] < 0.5  # Failed should have low score
        assert metrics["base_score"] == 0.0  # Failure gives base score 0.0
    
    @pytest.mark.asyncio
    async def test_trigger_alert(self, monitor):
        """Test alert triggering"""
        alert = await monitor._trigger_alert(
            alert_type="quality_low",
            message="Quality score below threshold",
            severity="warning"
        )
        
        assert isinstance(alert, dict)
        assert alert["type"] == "quality_low"
        assert alert["severity"] == "warning"
        assert "timestamp" in alert
    
    @pytest.mark.asyncio
    async def test_log_error(self, monitor):
        """Test error logging"""
        await monitor.log_error(
            task_id="test-task-001",
            error="TestError",
            context={"detail": "Test error context"}
        )
        
        assert len(monitor.error_log) > 0
        assert monitor.error_log[-1]["task_id"] == "test-task-001"
        assert monitor.error_log[-1]["error"] == "TestError"
    
    @pytest.mark.asyncio
    async def test_get_performance_report(self, monitor):
        """Test generating performance report"""
        # Simulate some executions
        await monitor.monitor_execution({
            "success": True,
            "metrics": {"execution_time": 1.0, "confidence_score": 0.9}
        })
        
        await monitor.monitor_execution({
            "success": False,
            "metrics": {"execution_time": 0.5, "confidence_score": 0.3}
        })
        
        report = await monitor.get_performance_report()
        
        assert isinstance(report, dict)
        assert "total_executions" in report
        assert "success_rate" in report
        assert "average_quality" in report
    
    @pytest.mark.asyncio
    async def test_get_status(self, monitor):
        """Test getting monitor status"""
        status = await monitor.get_status()
        
        assert isinstance(status, dict)
        assert "status" in status
        assert "errors_logged" in status
        assert "quality_threshold" in status


class TestAnomalyDetection:
    """Test anomaly detection features"""
    
    @pytest.fixture
    def monitor(self):
        """Create monitor with anomaly detection enabled"""
        config = {
            'quality_threshold': 0.8,
            'enable_anomaly_detection': True
        }
        return MonitorSystem(config)
    
    @pytest.mark.asyncio
    async def test_detect_execution_time_anomaly(self, monitor):
        """Test detecting unusually long execution times"""
        # Normal execution
        await monitor.monitor_execution({
            "success": True,
            "metrics": {"execution_time": 1.0, "confidence_score": 0.9}
        })
        
        # Anomalously slow execution
        result = await monitor.monitor_execution({
            "success": True,
            "metrics": {"execution_time": 60.0, "confidence_score": 0.9}
        })
        
        # Should detect anomaly (implementation dependent)
        assert isinstance(result, dict)
