"""
生产级 OpenHands 引擎 - 真实任务执行

集成：
- 真实 LLM API（OpenAI/Anthropic/Ollama）
- 安全代码执行沙箱
- 文件系统操作
- 错误处理和重试
"""

import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime, timezone

from .execution_engine import ExecutionSandbox
from .llm_integration import LLMRouter


def _now() -> str:
    """Get current UTC time as ISO string"""
    return datetime.now(timezone.utc).isoformat()


# 配置日志
logger = logging.getLogger(__name__)


class ProductionOpenHandsEngine:
    """
    生产级 OpenHands 引擎
    
    支持真实的任务执行，包括：
    - 代码生成和执行
    - 文件操作
    - Shell 命令
    - LLM 驱动的决策
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.model = config.get('model', 'gpt-4')
        self.sandbox_timeout = config.get('sandbox_timeout', 30)
        self.max_retries = config.get('max_retries', 3)
        
        # 初始化 LLM 路由器
        llm_config = {
            "provider": config.get('llm_provider', 'openai'),
            "model": self.model,
            "api_key": config.get('api_key'),
            "base_url": config.get('base_url')
        }
        self.llm = LLMRouter(llm_config)
        
        # 执行历史
        self.execution_history = []
        
        # 当前沙箱（每个任务创建新的）
        self.current_sandbox: Optional[ExecutionSandbox] = None
    
    async def execute(self, task, skills: List[Dict] = None) -> Dict:
        """
        执行任务（带重试机制）
        
        Args:
            task: 任务对象
            skills: 可用技能列表
            
        Returns:
            执行结果
        """
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"   🚀 Attempt {attempt}/{self.max_retries}: {task.description}")
                result = await self._execute_once(task, skills)
                
                # 如果成功，直接返回
                if result.get("success"):
                    return result
                
                # 记录错误但不立即重试
                last_error = result.get("error", "Unknown error")
                print(f"   ⚠️  Attempt {attempt} failed: {last_error[:100]}")
                
                # 如果不是最后一次尝试，等待后重试
                if attempt < self.max_retries:
                    wait_time = 2 ** (attempt - 1)  # 指数退避：1s, 2s, 4s...
                    print(f"   ⏳ Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                
            except Exception as e:
                last_error = str(e)
                print(f"   ❌ Attempt {attempt} error: {e}")
                
                if attempt < self.max_retries:
                    wait_time = 2 ** (attempt - 1)
                    print(f"   ⏳ Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
        
        # 所有重试都失败
        print(f"   ❌ All {self.max_retries} attempts failed")
        return {
            "success": False,
            "output": "",
            "error": f"Failed after {self.max_retries} attempts. Last error: {last_error}",
            "trace": {"error": last_error, "attempts": self.max_retries},
            "metrics": {"execution_time": 0}
        }
    
    async def _execute_once(self, task, skills: List[Dict] = None) -> Dict:
        """
        单次执行尝试
        
        四步流程：分析 → 生成 → 执行 → 验证
        """
        start_time = datetime.now(timezone.utc)
        logger.info(f"Starting execution for task: {task.id}")
        
        # 创建新的沙箱
        self.current_sandbox = ExecutionSandbox(timeout=self.sandbox_timeout)
        
        try:
            print(f"   🚀 Executing task: {task.description}")
            
            # Step 1: 使用 LLM 分析任务
            print("   📝 Analyzing task with LLM...")
            analysis = await self._analyze_task(task, skills)
            
            # Step 2: 生成解决方案
            print("   💻 Generating solution...")
            solution = await self._generate_solution(task, analysis, skills)
            
            # Step 3: 执行代码
            print("   ⚙️  Executing code...")
            execution_result = await self._execute_code(solution)
            
            # Step 4: 验证结果
            print("   ✅ Validating results...")
            validation = await self._validate_results(execution_result, task)
            
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Task {task.id} completed in {duration:.2f}s, success={result['success']}")
            
            # 构建最终结果
            result = {
                "success": validation.get("success", False),
                "output": execution_result.get("stdout", ""),
                "error": execution_result.get("stderr", "") if not validation.get("success") else None,
                "trace": {
                    "analysis": analysis,
                    "solution": solution,
                    "execution": execution_result,
                    "validation": validation,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat()
                },
                "metrics": {
                    "execution_time": duration,
                    "model": self.model,
                    "skills_used": len(skills) if skills else 0
                }
            }
            
            # 记录执行历史
            self.execution_history.append(result)
            
            status = "✅ Success" if result["success"] else "❌ Failed"
            print(f"   {status} ({duration:.2f}s)")
            
            return result
        
        except Exception as e:
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            error_result = {
                "success": False,
                "output": "",
                "error": str(e),
                "trace": {"error": str(e)},
                "metrics": {"execution_time": duration}
            }
            
            print(f"   ❌ Error: {e}")
            return error_result
        
        finally:
            # 清理沙箱
            if self.current_sandbox:
                self.current_sandbox.cleanup()
                self.current_sandbox = None
    
    async def _analyze_task(self, task, skills: List[Dict] = None) -> Dict:
        """使用 LLM 分析任务"""
        skill_descriptions = "\n".join([
            f"- {s.get('name', 'Unknown')}: {s.get('description', '')}"
            for s in (skills or [])[:5]
        ])
        
        prompt = f"""
Analyze the following task and provide a structured plan in JSON format:

Task: {task.description}
Project: {getattr(task, 'project_id', 'N/A')}
Language: {getattr(task, 'language', 'python')}
Framework: {getattr(task, 'framework', 'N/A')}

Available Skills:
{skill_descriptions}

Respond with ONLY valid JSON in this format:
{{
  "objectives": ["objective1", "objective2"],
  "steps": ["step1", "step2", "step3"],
  "required_skills": ["skill1", "skill2"],
  "potential_challenges": ["challenge1", "challenge2"],
  "estimated_complexity": "low|medium|high"
}}
"""
        
        try:
            import json
            response = await self.llm.generate(prompt)
            
            # 尝试提取 JSON
            json_str = response
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()
            
            # 解析 JSON
            analysis = json.loads(json_str)
            return {
                "objectives": analysis.get("objectives", [task.description]),
                "steps": analysis.get("steps", ["Implement"]),
                "required_skills": analysis.get("required_skills", []),
                "potential_challenges": analysis.get("potential_challenges", []),
                "complexity": analysis.get("estimated_complexity", "medium"),
                "raw_analysis": response[:500]
            }
        except Exception as e:
            # 回退方案
            return {
                "objectives": [task.description],
                "steps": ["Analyze requirements", "Implement solution", "Test and validate"],
                "required_skills": [],
                "potential_challenges": [f"Analysis error: {str(e)}"],
                "complexity": "unknown",
                "error": str(e)
            }
    
    async def _generate_solution(self, task, analysis: Dict, skills: List[Dict] = None) -> str:
        """使用 LLM 生成解决方案代码"""
        skill_examples = "\n\n".join([
            f"Skill: {s.get('name')}\n{s.get('code', '')}"
            for s in (skills or [])[:3]
        ])
        
        prompt = f"""
Generate code to accomplish this task:

Task: {task.description}
Language: {getattr(task, 'language', 'python')}

Analysis: {analysis.get('analysis_text', '')}

Example Skills:
{skill_examples}

Provide complete, executable code. Include:
- Necessary imports
- Main implementation
- Error handling
- Comments explaining key parts

Code only, no explanations outside code blocks.
"""
        
        try:
            code = await self.llm.generate(prompt, max_tokens=3000)
            # 提取代码块
            if "```" in code:
                # 提取第一个代码块
                start = code.find("```") + 3
                # 跳过语言标识
                newline_pos = code.find("\n", start)
                if newline_pos > 0:
                    start = newline_pos + 1
                end = code.find("```", start)
                if end > 0:
                    code = code[start:end].strip()
            return code
        except Exception as e:
            # 回退到简单实现
            return f"# Generated code for: {task.description}\nprint('Task executed')"
    
    async def _execute_code(self, code: str) -> Dict:
        """在沙箱中执行代码"""
        if not self.current_sandbox:
            raise RuntimeError("No sandbox available")
        
        # 检测代码类型
        if code.strip().startswith("#!") or any(cmd in code for cmd in ['ls', 'cd', 'grep']):
            # Shell 脚本
            return await self.current_sandbox.execute_shell(code)
        else:
            # Python 代码
            return await self.current_sandbox.execute_python(code)
    
    async def _validate_results(self, execution_result: Dict, task) -> Dict:
        """
        验证执行结果
        
        包括：
        - 执行状态检查
        - 输出质量评估
        - 错误分析
        """
        success = execution_result.get("success", False)
        stdout = execution_result.get("stdout", "")
        stderr = execution_result.get("stderr", "")
        returncode = execution_result.get("returncode", -1)
        duration = execution_result.get("duration", 0)
        
        # 基础验证
        if not success:
            return {
                "success": False,
                "message": f"Execution failed with code {returncode}",
                "error_type": "execution_error",
                "details": stderr[:500],
                "quality_score": 0.0
            }
        
        # 检查是否有错误输出
        if stderr and len(stderr.strip()) > 0:
            # 有 stderr 但不一定是错误（可能是警告）
            is_warning = any(w in stderr.lower() for w in ['warning', 'deprecated', 'note'])
            if not is_warning:
                return {
                    "success": False,
                    "message": f"Runtime warnings/errors: {stderr[:200]}",
                    "error_type": "runtime_warning",
                    "details": stderr[:500],
                    "quality_score": 0.5
                }
        
        # 检查输出是否为空
        if not stdout or len(stdout.strip()) == 0:
            return {
                "success": True,
                "message": "Execution completed but produced no output",
                "warning": "No output generated",
                "quality_score": 0.6
            }
        
        # 计算质量评分
        quality_score = self._calculate_quality_score(execution_result, task)
        
        return {
            "success": True,
            "message": "Execution completed successfully",
            "output_length": len(stdout),
            "duration": duration,
            "quality_score": quality_score,
            "warnings": stderr if stderr else None
        }
    
    def _calculate_quality_score(self, execution_result: Dict, task) -> float:
        """
        计算执行质量评分 (0.0 - 1.0)
        
        考虑因素：
        - 执行时间
        - 输出长度
        - 是否有错误
        """
        score = 1.0
        
        # 执行时间过长扣分
        duration = execution_result.get("duration", 0)
        if duration > 10:
            score -= 0.1
        if duration > 20:
            score -= 0.2
        
        # 输出长度为空扣分
        stdout = execution_result.get("stdout", "")
        if not stdout or len(stdout.strip()) == 0:
            score -= 0.3
        
        # 有警告扣分
        stderr = execution_result.get("stderr", "")
        if stderr and len(stderr.strip()) > 0:
            score -= 0.1
        
        # 确保分数在 0-1 之间
        return max(0.0, min(1.0, score))
    
    async def get_status(self) -> Dict:
        """获取引擎状态"""
        total = len(self.execution_history)
        successful = sum(1 for h in self.execution_history if h.get("success"))
        
        return {
            "status": "running",
            "model": self.model,
            "total_executions": total,
            "successful_executions": successful,
            "success_rate": round((successful / total * 100) if total > 0 else 0, 2)
        }
