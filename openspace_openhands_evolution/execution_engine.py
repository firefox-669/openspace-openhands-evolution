"""
真实代码执行引擎

负责：
- 安全的代码执行沙箱
- 文件系统操作
- Shell 命令执行
- 结果捕获和错误处理
"""

import asyncio
import subprocess
import tempfile
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime, timezone


def _now() -> str:
    """Get current UTC time as ISO string"""
    return datetime.now(timezone.utc).isoformat()


class ExecutionSandbox:
    """
    安全的代码执行沙箱
    
    提供隔离的执行环境，防止恶意代码破坏系统
    """
    
    def __init__(self, work_dir: Optional[str] = None, timeout: int = 30):
        self.work_dir = work_dir or tempfile.mkdtemp(prefix="sandbox_")
        self.timeout = timeout
        self.execution_log = []
        
        # 创建工作目录
        Path(self.work_dir).mkdir(parents=True, exist_ok=True)
    
    async def execute_python(self, code: str, input_data: Optional[Dict] = None) -> Dict:
        """
        执行 Python 代码
        
        Args:
            code: Python 代码字符串
            input_data: 输入数据（可选）
            
        Returns:
            执行结果字典
        """
        start_time = datetime.now(timezone.utc)
        
        # 创建临时文件
        script_path = Path(self.work_dir) / f"script_{int(start_time.timestamp())}.py"
        
        try:
            # 写入代码
            with open(script_path, 'w', encoding='utf-8') as f:
                # 添加安全限制
                safe_code = self._sanitize_code(code)
                f.write(safe_code)
            
            # 如果有输入数据，保存为 JSON
            input_file = None
            if input_data:
                import json
                input_file = Path(self.work_dir) / "input.json"
                with open(input_file, 'w', encoding='utf-8') as f:
                    json.dump(input_data, f)
            
            # 执行代码
            cmd = [sys.executable, str(script_path)]
            if input_file:
                cmd.append(str(input_file))
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.work_dir,
                limit=1024 * 1024  # 1MB output limit
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout
                )
                
                end_time = datetime.now(timezone.utc)
                duration = (end_time - start_time).total_seconds()
                
                success = process.returncode == 0
                
                result = {
                    "success": success,
                    "stdout": stdout.decode('utf-8', errors='replace') if stdout else "",
                    "stderr": stderr.decode('utf-8', errors='replace') if stderr else "",
                    "returncode": process.returncode,
                    "duration": duration,
                    "timestamp": _now()
                }
                
                # 记录执行日志
                self.execution_log.append(result)
                
                return result
                
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Execution timed out after {self.timeout} seconds",
                    "returncode": -1,
                    "duration": self.timeout,
                    "timestamp": _now()
                }
        
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "returncode": -1,
                "duration": 0,
                "timestamp": _now()
            }
        
        finally:
            # 清理临时文件
            try:
                if script_path.exists():
                    script_path.unlink()
            except:
                pass
    
    async def execute_shell(self, command: str) -> Dict:
        """
        执行 Shell 命令
        
        Args:
            command: Shell 命令
            
        Returns:
            执行结果
        """
        start_time = datetime.now(timezone.utc)
        
        # 安全检查：阻止危险命令
        if not self._is_safe_command(command):
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command blocked for security reasons",
                "returncode": -1,
                "duration": 0,
                "timestamp": _now()
            }
        
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.work_dir
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout
                )
                
                end_time = datetime.now(timezone.utc)
                duration = (end_time - start_time).total_seconds()
                
                result = {
                    "success": process.returncode == 0,
                    "stdout": stdout.decode('utf-8', errors='replace'),
                    "stderr": stderr.decode('utf-8', errors='replace'),
                    "returncode": process.returncode,
                    "duration": duration,
                    "timestamp": _now()
                }
                
                self.execution_log.append(result)
                return result
                
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Command timed out after {self.timeout} seconds",
                    "returncode": -1,
                    "duration": self.timeout,
                    "timestamp": _now()
                }
        
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command execution error: {str(e)}",
                "returncode": -1,
                "duration": 0,
                "timestamp": _now()
            }
    
    def write_file(self, filename: str, content: str) -> bool:
        """
        在工作目录中写入文件
        
        Args:
            filename: 文件名
            content: 文件内容
            
        Returns:
            是否成功
        """
        try:
            # 安全检查：防止路径遍历攻击
            file_path = Path(self.work_dir) / filename
            file_path = file_path.resolve()
            
            # 确保文件在工作目录内
            if not str(file_path).startswith(str(Path(self.work_dir).resolve())):
                return False
            
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
            return True
        
        except Exception:
            return False
    
    def read_file(self, filename: str) -> Optional[str]:
        """
        读取工作目录中的文件
        
        Args:
            filename: 文件名
            
        Returns:
            文件内容或 None
        """
        try:
            file_path = Path(self.work_dir) / filename
            file_path = file_path.resolve()
            
            # 安全检查
            if not str(file_path).startswith(str(Path(self.work_dir).resolve())):
                return None
            
            if file_path.exists():
                return file_path.read_text(encoding='utf-8')
            return None
        
        except Exception:
            return None
    
    def list_files(self) -> list:
        """列出工作目录中的所有文件"""
        try:
            files = []
            for file_path in Path(self.work_dir).rglob('*'):
                if file_path.is_file():
                    rel_path = file_path.relative_to(Path(self.work_dir))
                    files.append(str(rel_path))
            return files
        except Exception:
            return []
    
    def cleanup(self):
        """清理沙箱环境"""
        import shutil
        try:
            if Path(self.work_dir).exists():
                shutil.rmtree(self.work_dir, ignore_errors=True)
        except Exception:
            pass
    
    def _sanitize_code(self, code: str) -> str:
        """
        清理代码，移除潜在的危险操作
        
        Args:
            code: 原始代码
            
        Returns:
            清理后的代码
        """
        # 这里可以添加更多的安全检查
        # 例如：阻止导入某些模块、阻止访问特定路径等
        
        dangerous_imports = ['os.system', 'subprocess.call', '__import__']
        
        for dangerous in dangerous_imports:
            if dangerous in code:
                # 可以选择移除或替换
                code = code.replace(dangerous, f'# Blocked: {dangerous}')
        
        return code
    
    def _is_safe_command(self, command: str) -> bool:
        """
        检查命令是否安全
        
        Args:
            command: Shell 命令
            
        Returns:
            是否安全
        """
        # 阻止危险命令
        dangerous_patterns = [
            'rm -rf /',
            'mkfs',
            'dd if=',
            ':(){:|:&};:',  # fork bomb
            '> /dev/sda',
        ]
        
        command_lower = command.lower()
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                return False
        
        return True
    
    def __del__(self):
        """析构时清理"""
        self.cleanup()
