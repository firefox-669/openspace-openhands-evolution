"""
MTL (Memory Transfer Learning) 适配器

负责：
- 计算任务结构相似度
- 跨项目技能迁移
- 负迁移风险评估（V-02）
"""

from typing import List, Dict, Optional
from datetime import datetime
import hashlib


class MTLAdapter:
    """记忆迁移学习适配器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.similarity_threshold = config.get('similarity_threshold', 0.7)
        self.transfer_history = []
        
        # 简化的任务特征提取器
        self.task_features_cache = {}
    
    async def calculate_task_similarity(self, task1_desc: str, task2_desc: str) -> float:
        """
        计算两个任务的結構相似度
        
        Args:
            task1_desc: 任务 1 描述
            task2_desc: 任务 2 描述
            
        Returns:
            相似度分数 (0-1)
        """
        # 简化实现：基于关键词重叠
        words1 = set(task1_desc.lower().split())
        words2 = set(task2_desc.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard 相似度
        intersection = words1 & words2
        union = words1 | words2
        
        similarity = len(intersection) / len(union)
        
        return round(min(similarity * 2, 1.0), 2)  # 放大一点
    
    async def transfer_skills(self, source_skills: List[Dict], 
                             target_project: str,
                             similarity_threshold: float = None) -> List[Dict]:
        """
        将技能从源项目迁移到目标项目
        
        Args:
            source_skills: 源技能列表
            target_project: 目标项目 ID
            similarity_threshold: 相似度阈值
            
        Returns:
            适配后的技能列表
        """
        threshold = similarity_threshold or self.similarity_threshold
        
        adapted_skills = []
        
        for skill in source_skills:
            # 检查是否适合目标项目
            is_suitable = await self._assess_skill_suitability(skill, target_project)
            
            if is_suitable['score'] >= threshold:
                # 适配技能
                adapted_skill = await self._adapt_skill_for_project(skill, target_project)
                adapted_skills.append(adapted_skill)
        
        # 记录迁移历史
        transfer_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "source_skills_count": len(source_skills),
            "adapted_skills_count": len(adapted_skills),
            "target_project": target_project,
            "threshold": threshold
        }
        self.transfer_history.append(transfer_record)
        
        print(f"🔄 Transferred {len(adapted_skills)}/{len(source_skills)} skills to {target_project}")
        
        return adapted_skills
    
    async def _assess_skill_suitability(self, skill: Dict, target_project: str) -> Dict:
        """
        评估技能对目标项目的适用性
        
        Returns:
            评估结果（包含分数和原因）
        """
        score = 0.7  # 基础分数
        
        # 考虑语言匹配
        skill_language = skill.get('metadata', {}).get('language', '')
        if skill_language:
            score += 0.1  # 有明确语言，加分
        
        # 考虑框架匹配
        skill_framework = skill.get('metadata', {}).get('framework', '')
        if skill_framework:
            score += 0.1  # 有明确框架，加分
        
        # V-02: 负迁移风险评估
        risk_assessment = await self._assess_negative_transfer_risk(skill, target_project)
        
        if risk_assessment['risk_level'] == 'high':
            score *= 0.5  # 高风险，大幅降低分数
        elif risk_assessment['risk_level'] == 'medium':
            score *= 0.8  # 中风险，适度降低
        
        return {
            "score": min(score, 1.0),
            "risk_assessment": risk_assessment,
            "suitable": score >= self.similarity_threshold
        }
    
    async def _assess_negative_transfer_risk(self, skill: Dict, target_project: str) -> Dict:
        """
        V-02: 评估负迁移风险
        
        Returns:
            风险评估结果
        """
        # 简化实现：基于项目差异度
        # 在实际实现中，应该分析项目特性、依赖、环境等
        
        risk_factors = []
        
        # 检查 1: 技能是否有环境指纹
        env_fingerprint = skill.get('environment_fingerprint', {})
        if not env_fingerprint:
            risk_factors.append("Missing environment fingerprint")
        
        # 检查 2: 技能是否有失败历史
        fix_history = skill.get('metadata', {}).get('fix_history', [])
        if len(fix_history) > 3:
            risk_factors.append("Multiple previous fixes")
        
        # 确定风险等级
        if len(risk_factors) >= 2:
            risk_level = "high"
        elif len(risk_factors) == 1:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommendation": "proceed_with_caution" if risk_level != "low" else "safe_to_transfer"
        }
    
    async def _adapt_skill_for_project(self, skill: Dict, target_project: str) -> Dict:
        """
        为特定项目适配技能
        
        Args:
            skill: 原始技能
            target_project: 目标项目
            
        Returns:
            适配后的技能
        """
        # 创建技能的副本
        adapted_skill = skill.copy()
        adapted_skill['metadata'] = skill.get('metadata', {}).copy()
        
        # 添加适配元数据
        adapted_skill['metadata']['adapted_for'] = target_project
        adapted_skill['metadata']['adaptation_timestamp'] = datetime.utcnow().isoformat()
        adapted_skill['metadata']['original_skill_id'] = skill.get('skill_id')
        
        # 生成新的技能 ID
        original_id = skill.get('skill_id', 'unknown')
        adapted_skill['skill_id'] = f"{original_id}-adapted-{target_project}"
        
        # TODO: 在实际实现中，这里应该调用 LLM 修改代码以适配目标项目
        
        return adapted_skill
    
    async def get_transfer_statistics(self) -> Dict:
        """获取迁移统计信息"""
        if not self.transfer_history:
            return {
                "total_transfers": 0,
                "avg_adaptation_rate": 0.0
            }
        
        total_source = sum(h['source_skills_count'] for h in self.transfer_history)
        total_adapted = sum(h['adapted_skills_count'] for h in self.transfer_history)
        
        avg_rate = total_adapted / total_source if total_source > 0 else 0
        
        return {
            "total_transfers": len(self.transfer_history),
            "total_source_skills": total_source,
            "total_adapted_skills": total_adapted,
            "avg_adaptation_rate": round(avg_rate, 2)
        }
