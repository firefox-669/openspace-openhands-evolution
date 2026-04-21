"""
AAIP (Agent Interoperability Protocol) 协议

负责：
- 技能格式标准化
- Agent 间互操作
- 技能共享协议
"""

from typing import List, Dict, Optional
from datetime import datetime
import json


class AAIPProtocol:
    """Agent 互操作协议实现"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.skill_sharing_enabled = config.get('skill_sharing_enabled', True)
        self.shared_skills_log = []
        
        # AAIP 标准版本
        self.protocol_version = "1.0.0"
    
    async def standardize_skill(self, skill: Dict) -> Dict:
        """
        将技能标准化为 AAIP 格式
        
        Args:
            skill: 原始技能
            
        Returns:
            标准化后的技能
        """
        standardized = {
            "aaip_version": self.protocol_version,
            "skill_id": skill.get("skill_id"),
            "name": skill.get("name"),
            "description": skill.get("description"),
            "code": skill.get("code"),
            "metadata": {
                **skill.get("metadata", {}),
                "standardized_at": datetime.utcnow().isoformat(),
                "protocol_version": self.protocol_version
            },
            "interface": {
                "inputs": self._extract_inputs(skill),
                "outputs": self._extract_outputs(skill),
                "dependencies": skill.get("metadata", {}).get("dependencies", [])
            },
            "quality_metrics": {
                "version": skill.get("version", 1),
                "usage_count": skill.get("usage_count", 0),
                "success_rate": skill.get("success_rate", 0.0)
            }
        }
        
        return standardized
    
    def _extract_inputs(self, skill: Dict) -> List[Dict]:
        """提取技能的输入接口"""
        # 简化实现：从代码中推断
        # 在实际实现中，应该使用 AST 分析
        return [
            {"name": "input_data", "type": "any", "required": True}
        ]
    
    def _extract_outputs(self, skill: Dict) -> List[Dict]:
        """提取技能的输出接口"""
        return [
            {"name": "result", "type": "any", "description": "Execution result"}
        ]
    
    async def validate_aaip_compliance(self, skill: Dict) -> tuple[bool, List[str]]:
        """
        验证技能是否符合 AAIP 标准
        
        Returns:
            (是否合规, 问题列表)
        """
        issues = []
        
        # 检查必需字段
        required_fields = ["skill_id", "name", "description", "code"]
        for field in required_fields:
            if field not in skill:
                issues.append(f"Missing required field: {field}")
        
        # 检查 AAIP 版本
        if "aaip_version" not in skill.get("metadata", {}):
            issues.append("Missing AAIP version in metadata")
        
        # 检查接口定义
        if "interface" not in skill:
            issues.append("Missing interface definition")
        
        is_compliant = len(issues) == 0
        
        return is_compliant, issues
    
    async def share_skill(self, skill: Dict, target_agent: str) -> bool:
        """
        共享技能到其他 Agent
        
        Args:
            skill: 要共享的技能
            target_agent: 目标 Agent ID
            
        Returns:
            是否成功共享
        """
        if not self.skill_sharing_enabled:
            print("⚠️  Skill sharing is disabled")
            return False
        
        # 标准化技能
        standardized_skill = await self.standardize_skill(skill)
        
        # 验证合规性
        is_compliant, issues = await self.validate_aaip_compliance(standardized_skill)
        
        if not is_compliant:
            print(f"❌ Skill not AAIP compliant: {', '.join(issues)}")
            return False
        
        # 记录共享
        share_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "skill_id": skill.get("skill_id"),
            "target_agent": target_agent,
            "protocol_version": self.protocol_version,
            "status": "shared"
        }
        self.shared_skills_log.append(share_record)
        
        print(f"✅ Shared skill '{skill.get('name')}' with {target_agent}")
        
        return True
    
    async def receive_skill(self, skill: Dict, source_agent: str) -> Dict:
        """
        从其他 Agent 接收技能
        
        Args:
            skill: 接收的技能
            source_agent: 源 Agent ID
            
        Returns:
            处理后的技能
        """
        # 验证 AAIP 合规性
        is_compliant, issues = await self.validate_aaip_compliance(skill)
        
        if not is_compliant:
            raise ValueError(f"Received non-compliant skill: {', '.join(issues)}")
        
        # 添加来源信息
        skill['metadata']['source_agent'] = source_agent
        skill['metadata']['received_at'] = datetime.utcnow().isoformat()
        
        print(f"✅ Received skill '{skill.get('name')}' from {source_agent}")
        
        return skill
    
    async def get_shared_skills_catalog(self) -> List[Dict]:
        """获取已共享技能目录"""
        return self.shared_skills_log
    
    async def get_protocol_info(self) -> Dict:
        """获取协议信息"""
        return {
            "protocol_name": "AAIP",
            "version": self.protocol_version,
            "skill_sharing_enabled": self.skill_sharing_enabled,
            "total_shared_skills": len(self.shared_skills_log),
            "supported_features": [
                "skill_standardization",
                "compliance_validation",
                "peer_to_peer_sharing",
                "version_tracking"
            ]
        }
