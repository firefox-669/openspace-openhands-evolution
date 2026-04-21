"""
OpenSpace 引擎 - 记忆管理与技能进化

负责：
- 技能注册表管理
- 向量记忆存储
- 技能进化算法
- AAIP 卡片管理
"""

from typing import List, Dict, Optional
from datetime import datetime, timezone
import hashlib
import json


def _now() -> str:
    """Get current UTC time as ISO string"""
    return datetime.now(timezone.utc).isoformat()


class SkillCard:
    """AAIP 技能卡片"""
    
    def __init__(self, skill_id: str, name: str, description: str, 
                 code: str, metadata: Dict = None):
        self.skill_id = skill_id
        self.name = name
        self.description = description
        self.code = code
        self.metadata = metadata or {}
        self.created_at = _now()
        self.version = 1
        self.usage_count = 0
        self.success_rate = 0.0
        self.environment_fingerprint = {}  # V-06: 环境指纹
    
    def to_dict(self) -> Dict:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "description": self.description,
            "code": self.code,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "version": self.version,
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
            "environment_fingerprint": self.environment_fingerprint
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SkillCard':
        card = cls(
            skill_id=data["skill_id"],
            name=data["name"],
            description=data["description"],
            code=data["code"],
            metadata=data.get("metadata", {})
        )
        card.created_at = data.get("created_at", card.created_at)
        card.version = data.get("version", 1)
        card.usage_count = data.get("usage_count", 0)
        card.success_rate = data.get("success_rate", 0.0)
        card.environment_fingerprint = data.get("environment_fingerprint", {})
        return card


class OpenSpaceEngine:
    """OpenSpace 核心引擎"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.skill_registry: Dict[str, SkillCard] = {}  # 技能注册表
        self.memory_store: Dict[str, List[Dict]] = {}  # 记忆存储（按项目分组）
        self.project_skills: Dict[str, List[str]] = {}  # 项目与技能的映射
        
        # 初始化示例技能
        self._initialize_sample_skills()
    
    def _initialize_sample_skills(self):
        """初始化示例技能用于演示"""
        sample_skills = [
            SkillCard(
                skill_id="skill-flask-api",
                name="Flask API Creator",
                description="Create a RESTful API using Flask framework",
                code="# Flask API template\nfrom flask import Flask, jsonify\n\napp = Flask(__name__)\n\n@app.route('/api/data')\ndef get_data():\n    return jsonify({'status': 'ok'})",
                metadata={"language": "python", "framework": "flask", "category": "web"}
            ),
            SkillCard(
                skill_id="skill-data-analysis",
                name="Pandas Data Analysis",
                description="Analyze data using pandas library",
                code="# Data analysis template\nimport pandas as pd\n\ndef analyze_data(filepath):\n    df = pd.read_csv(filepath)\n    return df.describe()",
                metadata={"language": "python", "library": "pandas", "category": "data"}
            ),
            SkillCard(
                skill_id="skill-react-component",
                name="React Component Generator",
                description="Generate React functional components",
                code="// React component template\nimport React from 'react';\n\nconst MyComponent = ({ title }) => {\n  return <div>{title}</div>;\n};\n\nexport default MyComponent;",
                metadata={"language": "javascript", "framework": "react", "category": "frontend"}
            )
        ]
        
        for skill in sample_skills:
            self.skill_registry[skill.skill_id] = skill
            # 默认分配给 demo 项目
            if "demo-project" not in self.project_skills:
                self.project_skills["demo-project"] = []
            self.project_skills["demo-project"].append(skill.skill_id)
    
    async def search_skills(self, query: str, context: Dict) -> List[Dict]:
        """
        基于语义搜索检索技能
        
        Args:
            query: 搜索查询
            context: 上下文信息（project, language, framework等）
            
        Returns:
            匹配的技能列表
        """
        matched_skills = []
        query_lower = query.lower()
        
        # 简单关键词匹配（实际应使用向量检索）
        for skill_id, skill in self.skill_registry.items():
            score = 0.0
            
            # 匹配描述
            if query_lower in skill.description.lower():
                score += 0.5
            
            # 匹配名称
            if query_lower in skill.name.lower():
                score += 0.3
            
            # 匹配元数据
            for key, value in skill.metadata.items():
                if isinstance(value, str) and query_lower in value.lower():
                    score += 0.2
            
            # 上下文过滤
            if context.get('language') and skill.metadata.get('language') != context['language']:
                score *= 0.5  # 语言不匹配，降低分数
            
            if context.get('framework') and skill.metadata.get('framework') != context['framework']:
                score *= 0.7  # 框架不匹配，稍微降低分数
            
            if score > 0.3:  # 阈值
                skill_dict = skill.to_dict()
                skill_dict['relevance_score'] = min(score, 1.0)
                matched_skills.append(skill_dict)
        
        # 按相关性排序
        matched_skills.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return matched_skills[:10]  # 返回 top 10
    
    async def evolve_skill(self, skill_id=None, improvements=None, task=None, execution_trace: Dict=None, quality_score: float=None):
        """
        基于执行结果进化技能
        
        Args:
            skill_id: 技能 ID (for backward compatibility with tests)
            improvements: 改进列表 (for backward compatibility with tests)
            task: 任务对象
            execution_trace: 执行轨迹
            quality_score: 质量评分 (0-1)
            
        Returns:
            进化后的技能或 None
        """
        # Backward compatibility: if skill_id and improvements are provided, use old API
        if skill_id is not None and improvements is not None:
            if skill_id not in self.skill_registry:
                return None
            
            skill = self.skill_registry[skill_id]
            skill.version += 1
            
            if "improvements" not in skill.metadata:
                skill.metadata["improvements"] = []
            skill.metadata["improvements"].extend(improvements)
            
            return skill
        
        # New API: record to memory store
        if task is None:
            return None
            
        project_id = getattr(task, 'project_id', 'unknown')
        if project_id not in self.memory_store:
            self.memory_store[project_id] = []
        
        memory_entry = {
            "task_id": getattr(task, 'id', 'unknown'),
            "timestamp": _now(),
            "quality_score": quality_score or 0.5,
            "execution_trace": execution_trace or {},
            "improvements": []
        }
        
        # 如果质量低于阈值，标记需要改进
        if quality_score and quality_score < 0.7:
            memory_entry["needs_improvement"] = True
            memory_entry["improvements"].append({
                "type": "quality_below_threshold",
                "current_score": quality_score,
                "target_score": 0.8
            })
        
        self.memory_store[project_id].append(memory_entry)
        
        # TODO: 在实际实现中，这里应该调用 LLM 分析失败原因并生成改进版本
        return None
    
    async def fix_skill(self, skill_id=None, error_context: Dict=None, failed_skill_id=None):
        """
        修复失败的技能
        
        Args:
            skill_id: 技能 ID (for backward compatibility with tests)
            error_context: 错误上下文
            failed_skill_id: 失败的技能 ID (alias for skill_id)
            
        Returns:
            SkillCard: 修复后的技能对象
        """
        # Support both parameter names
        actual_skill_id = skill_id or failed_skill_id
        if not actual_skill_id:
            return None
            
        if actual_skill_id not in self.skill_registry:
            return None
        
        skill = self.skill_registry[actual_skill_id]
        
        # 记录失败历史
        if "fix_history" not in skill.metadata:
            skill.metadata["fix_history"] = []
        
        skill.metadata["fix_history"].append({
            "timestamp": _now(),
            "error": error_context.get("error", "Unknown") if error_context else "Unknown",
            "context": error_context or {}
        })
        
        # TODO: 在实际实现中，这里应该分析错误并生成修复版本
        print(f"⚠️  Skill {actual_skill_id} marked for fixing")
        
        return skill
    
    async def get_project_skills(self, project_id: str) -> List[Dict]:
        """获取项目的所有技能"""
        skill_ids = self.project_skills.get(project_id, [])
        skills = []
        
        for skill_id in skill_ids:
            if skill_id in self.skill_registry:
                skills.append(self.skill_registry[skill_id].to_dict())
        
        return skills
    
    async def get_skills_by_ids(self, skill_ids: List[str]) -> List[Dict]:
        """根据 ID 获取技能"""
        skills = []
        for skill_id in skill_ids:
            if skill_id in self.skill_registry:
                skills.append(self.skill_registry[skill_id].to_dict())
        return skills
    
    async def import_skills(self, project_id: str, skills: List[Dict]):
        """
        导入技能到项目
        
        Args:
            project_id: 目标项目 ID
            skills: 技能列表
        """
        if project_id not in self.project_skills:
            self.project_skills[project_id] = []
        
        imported_count = 0
        for skill_data in skills:
            skill_id = skill_data.get('skill_id')
            if not skill_id:
                continue
            
            # 创建或更新技能
            if skill_id in self.skill_registry:
                # 更新现有技能
                existing = self.skill_registry[skill_id]
                existing.version += 1
            else:
                # 创建新技能
                new_skill = SkillCard.from_dict(skill_data)
                self.skill_registry[skill_id] = new_skill
            
            # 添加到项目
            if skill_id not in self.project_skills[project_id]:
                self.project_skills[project_id].append(skill_id)
                imported_count += 1
        
        print(f"✅ Imported {imported_count} skills to project {project_id}")
    
    async def register_skill(self, skill_data: Dict):
        """
        注册单个技能（便捷方法）
        
        Args:
            skill_data: 技能数据字典
            
        Returns:
            SkillCard: 注册的技能对象
        """
        skill_id = skill_data.get('skill_id')
        if not skill_id:
            raise ValueError("skill_id is required")
        
        # 创建或更新技能
        if skill_id in self.skill_registry:
            skill = self.skill_registry[skill_id]
            skill.version += 1
        else:
            skill = SkillCard.from_dict(skill_data)
            self.skill_registry[skill_id] = skill
        
        return skill
    
    async def capture_environment_fingerprint(self, project_id: str) -> Dict:
        """
        V-06: 捕获环境指纹
        
        Returns:
            环境指纹字典
        """
        import platform
        import sys
        
        fingerprint = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": sys.version,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # 存储指纹
        if project_id not in self.memory_store:
            self.memory_store[project_id] = []
        
        self.memory_store[project_id].append({
            "type": "environment_fingerprint",
            "fingerprint": fingerprint,
            "timestamp": fingerprint["timestamp"]
        })
        
        return fingerprint
    
    async def get_status(self) -> Dict:
        """获取引擎状态"""
        total_usage = sum(s.usage_count for s in self.skill_registry.values())
        avg_success_rate = (
            sum(s.success_rate for s in self.skill_registry.values()) / len(self.skill_registry)
            if self.skill_registry else 0.0
        )
        
        return {
            "status": "running",
            "skills_count": len(self.skill_registry),
            "memories_count": sum(len(v) for v in self.memory_store.values()),
            "projects_count": len(self.project_skills),
            "total_skill_usage": total_usage,
            "avg_success_rate": round(avg_success_rate, 2)
        }
