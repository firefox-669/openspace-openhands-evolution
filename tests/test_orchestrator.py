"""Tests for orchestrator module"""

import pytest
import asyncio
from openspace_openhands_evolution import (
    EvolutionOrchestrator,
    TaskRequest,
    TransferRequest,
)
from .conftest import MockLLMProvider


class TestTaskRequest:
    """Test TaskRequest dataclass"""
    
    def test_create_basic_task(self):
        """Test creating a basic task"""
        task = TaskRequest(
            id="test-001",
            description="Test task",
            project_id="test-project"
        )
        
        assert task.id == "test-001"
        assert task.description == "Test task"
        assert task.project_id == "test-project"
        assert task.language == "python"  # default
        assert task.max_iterations == 10  # default
    
    def test_create_task_with_options(self):
        """Test creating task with all options"""
        task = TaskRequest(
            id="test-002",
            description="Complex task",
            project_id="my-project",
            language="javascript",
            framework="react",
            model="gpt-4",
            max_iterations=20,
            context={"key": "value"}
        )
        
        assert task.language == "javascript"
        assert task.framework == "react"
        assert task.model == "gpt-4"
        assert task.max_iterations == 20
        assert task.context == {"key": "value"}


class TestTransferRequest:
    """Test TransferRequest dataclass"""
    
    def test_create_basic_transfer(self):
        """Test creating basic transfer request"""
        transfer = TransferRequest(
            source_project="project-a",
            target_project="project-b"
        )
        
        assert transfer.source_project == "project-a"
        assert transfer.target_project == "project-b"
        assert transfer.min_similarity == 0.7  # default
    
    def test_create_transfer_with_options(self):
        """Test transfer with custom options"""
        transfer = TransferRequest(
            source_project="proj-1",
            target_project="proj-2",
            min_similarity=0.85,
            skill_ids=["skill-1", "skill-2"]
        )
        
        assert transfer.min_similarity == 0.85
        assert transfer.skill_ids == ["skill-1", "skill-2"]


class TestEvolutionOrchestrator:
    """Test EvolutionOrchestrator"""
    
    @pytest.fixture
    def config(self):
        """Basic config for testing with mock LLM"""
        return {
            'openspace': {'registry_path': './test_data/skills'},
            'openhands': {
                'model': 'mock-gpt-4',
                'api_key': 'test-key',
                'llm_provider': MockLLMProvider(),
            },
            'monitor': {'quality_threshold': 0.8},
            'governance': {'enable_gatekeeping': True}
        }
    
    def test_init_orchestrator(self, config):
        """Test orchestrator initialization"""
        orchestrator = EvolutionOrchestrator(config)
        
        assert orchestrator.config == config
        assert orchestrator.quality_threshold == 0.8
        assert orchestrator.skill_sharing_enabled == True
    
    def test_init_with_custom_config(self):
        """Test orchestrator with custom config"""
        config = {
            'openspace': {'registry_path': './custom'},
            'openhands': {
                'model': 'mock-claude-3',
                'api_key': 'test-key',
                'llm_provider': MockLLMProvider(),
            },
            'monitor': {'quality_threshold': 0.9},
            'governance': {'enable_gatekeeping': False},
            'quality_threshold': 0.9,
            'skill_sharing_enabled': False
        }
        
        orchestrator = EvolutionOrchestrator(config)
        assert orchestrator.quality_threshold == 0.9
        assert orchestrator.skill_sharing_enabled == False
    
    @pytest.mark.asyncio
    async def test_execute_task_structure(self, config):
        """Test that execute_task returns correct structure"""
        orchestrator = EvolutionOrchestrator(config)
        
        task = TaskRequest(
            id="test-task",
            description="Test execution",
            project_id="test-project"
        )
        
        # Note: This will use stub engines, so result may not be meaningful
        # but structure should be correct
        result = await orchestrator.execute_task(task)
        
        assert hasattr(result, 'success')
        assert hasattr(result, 'output')
        assert hasattr(result, 'metrics')
        assert hasattr(result, 'evolved_skills')
        assert hasattr(result, 'reasoning_trace')
        assert hasattr(result, 'execution_steps')
    
    @pytest.mark.asyncio
    async def test_get_system_status(self, config):
        """Test getting system status"""
        orchestrator = EvolutionOrchestrator(config)
        
        status = await orchestrator.get_system_status()
        
        assert 'openspace' in status
        assert 'openhands' in status
        assert 'monitor' in status
        assert 'governance' in status
        assert 'timestamp' in status


class TestHierarchicalArchitecture:
    """Test hierarchical agent architecture"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator for testing"""
        config = {
            'openspace': {'registry_path': './test_data'},
            'openhands': {
                'model': 'mock-gpt-4',
                'api_key': 'test-key',
                'llm_provider': MockLLMProvider(),
            },
            'monitor': {'quality_threshold': 0.8},
        }
        return EvolutionOrchestrator(config)
    
    @pytest.mark.asyncio
    async def test_planning_layer_exists(self, orchestrator):
        """Test that planning layer method exists"""
        assert hasattr(orchestrator, '_planning_layer')
    
    @pytest.mark.asyncio
    async def test_planning_layer_output_structure(self, orchestrator):
        """Test planning layer output structure"""
        task = TaskRequest(
            id="plan-test",
            description="Test planning",
            project_id="test"
        )
        
        result = await orchestrator._planning_layer(task)
        
        assert 'task_id' in result
        assert 'description' in result
        assert 'subtasks' in result
        assert 'constraints' in result
        assert 'strategy' in result
        assert result['strategy'] == 'hierarchical_decomposition'


class TestReasoningTrace:
    """Test interpretable reasoning trace"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator for testing"""
        config = {
            'openspace': {'registry_path': './test_data'},
            'openhands': {
                'model': 'mock-gpt-4',
                'api_key': 'test-key',
                'llm_provider': MockLLMProvider(),
            },
            'monitor': {'quality_threshold': 0.8},
        }
        return EvolutionOrchestrator(config)
    
    @pytest.mark.asyncio
    async def test_result_has_reasoning_trace(self, orchestrator):
        """Test that result includes reasoning trace"""
        task = TaskRequest(
            id="trace-test",
            description="Test reasoning trace",
            project_id="test"
        )
        
        result = await orchestrator.execute_task(task)
        
        # Should have reasoning_trace attribute
        assert hasattr(result, 'reasoning_trace')
        assert isinstance(result.reasoning_trace, list)
    
    @pytest.mark.asyncio
    async def test_result_has_execution_steps(self, orchestrator):
        """Test that result includes execution steps"""
        task = TaskRequest(
            id="steps-test",
            description="Test execution steps",
            project_id="test"
        )
        
        result = await orchestrator.execute_task(task)
        
        # Should have execution_steps attribute
        assert hasattr(result, 'execution_steps')
        assert isinstance(result.execution_steps, list)
