"""
Shared test fixtures and utilities
"""
import pytest
from unittest.mock import AsyncMock, MagicMock


class MockLLMProvider:
    """Mock LLM provider for testing without API keys"""
    
    async def generate(self, prompt: str) -> str:
        """Mock LLM generation"""
        return '{"action": "test", "output": "mock response from LLM"}'
    
    async def analyze(self, text: str) -> dict:
        """Mock analysis"""
        return {
            "confidence": 0.9,
            "category": "test",
            "intent": "code_generation"
        }


@pytest.fixture
def mock_llm_config():
    """Configuration with mock LLM"""
    return {
        'openspace': {
            'registry_path': './test_data/skills',
        },
        'openhands': {
            'model': 'mock-gpt-4',
            'api_key': 'test-key',
            'provider': 'mock',  # Add provider type
        },
        'monitor': {
            'quality_threshold': 0.8,
            'enable_alerts': False,
        },
        'governance': {
            'enabled': True,
        }
    }
