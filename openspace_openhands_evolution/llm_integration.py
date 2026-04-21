"""
LLM 集成模块

支持多个 LLM 提供商：
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- 本地模型（通过 Ollama）
"""

import os
from typing import Dict, List, Optional
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """LLM 提供商抽象基类"""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        pass
    
    @abstractmethod
    async def generate_with_tools(self, prompt: str, tools: List[Dict], **kwargs) -> Dict:
        """使用工具调用生成"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API 提供商"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        # 延迟导入，避免依赖问题
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")
    
    async def generate(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7, **kwargs) -> str:
        """生成文本"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    async def generate_with_tools(self, prompt: str, tools: List[Dict], **kwargs) -> Dict:
        """使用工具调用生成"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                tools=tools,
                **kwargs
            )
            
            choice = response.choices[0]
            
            if choice.message.tool_calls:
                return {
                    "type": "tool_call",
                    "tool_calls": choice.message.tool_calls,
                    "content": choice.message.content
                }
            else:
                return {
                    "type": "text",
                    "content": choice.message.content
                }
        
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API 提供商"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable.")
        
        try:
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("anthropic package is required. Install with: pip install anthropic")
    
    async def generate(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7, **kwargs) -> str:
        """生成文本"""
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            
            return response.content[0].text
        
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}")
    
    async def generate_with_tools(self, prompt: str, tools: List[Dict], **kwargs) -> Dict:
        """Claude 暂不支持工具调用，返回普通文本"""
        content = await self.generate(prompt, **kwargs)
        return {
            "type": "text",
            "content": content
        }


class OllamaProvider(LLMProvider):
    """本地 Ollama 模型提供商"""
    
    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        
        try:
            import aiohttp
            self.session = aiohttp.ClientSession(base_url=base_url)
        except ImportError:
            raise ImportError("aiohttp package is required. Install with: pip install aiohttp")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            async with self.session.post("/api/generate", json=payload) as response:
                result = await response.json()
                return result.get("response", "")
        
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")
    
    async def generate_with_tools(self, prompt: str, tools: List[Dict], **kwargs) -> Dict:
        """Ollama 暂不支持工具调用"""
        content = await self.generate(prompt, **kwargs)
        return {
            "type": "text",
            "content": content
        }
    
    async def close(self):
        """关闭会话"""
        await self.session.close()


class LLMRouter:
    """
    LLM 路由器
    
    根据配置自动选择合适的提供商
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.provider = self._create_provider()
    
    def _create_provider(self) -> LLMProvider:
        """根据配置创建提供商"""
        provider_type = self.config.get("provider", "openai").lower()
        model = self.config.get("model", "gpt-4")
        
        if provider_type == "openai":
            api_key = self.config.get("api_key") or os.getenv("OPENAI_API_KEY")
            return OpenAIProvider(api_key=api_key, model=model)
        
        elif provider_type == "anthropic":
            api_key = self.config.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
            return AnthropicProvider(api_key=api_key, model=model)
        
        elif provider_type == "ollama":
            base_url = self.config.get("base_url", "http://localhost:11434")
            return OllamaProvider(model=model, base_url=base_url)
        
        else:
            raise ValueError(f"Unsupported provider: {provider_type}")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        return await self.provider.generate(prompt, **kwargs)
    
    async def generate_with_tools(self, prompt: str, tools: List[Dict], **kwargs) -> Dict:
        """使用工具调用生成"""
        return await self.provider.generate_with_tools(prompt, tools, **kwargs)
    
    async def close(self):
        """关闭连接"""
        if hasattr(self.provider, 'close'):
            await self.provider.close()
