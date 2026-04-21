"""
跨项目知识图谱 (Cross-Project Knowledge Graph)

建立项目之间的关联关系，实现知识的跨项目复用和检索。
"""

import json
import os
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class RelationType(Enum):
    """知识关系类型"""
    SIMILAR_TASK = "similar_task"           # 相似任务
    SHARED_SKILL = "shared_skill"           # 共享技能
    DEPENDENCY = "dependency"               # 依赖关系
    TRANSFERRED_KNOWLEDGE = "transferred"   # 知识迁移
    SAME_DOMAIN = "same_domain"            # 同领域
    COMPLEMENTARY = "complementary"        # 互补关系


@dataclass
class ProjectNode:
    """项目节点"""
    project_id: str
    name: str
    language: str
    framework: Optional[str] = None
    domain: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'project_id': self.project_id,
            'name': self.name,
            'language': self.language,
            'framework': self.framework,
            'domain': self.domain,
            'created_at': self.created_at,
            'metadata': self.metadata
        }


@dataclass
class KnowledgeEdge:
    """知识边"""
    source_project: str
    target_project: str
    relation_type: str
    strength: float  # 关系强度 0.0-1.0
    knowledge_items: List[str] = field(default_factory=list)  # 相关知识项
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'source_project': self.source_project,
            'target_project': self.target_project,
            'relation_type': self.relation_type,
            'strength': self.strength,
            'knowledge_items': self.knowledge_items,
            'created_at': self.created_at,
            'metadata': self.metadata
        }


@dataclass
class KnowledgeItem:
    """知识项"""
    id: str
    type: str  # skill, pattern, solution, error_fix
    title: str
    description: str
    project_id: str
    tags: List[str] = field(default_factory=list)
    quality_score: float = 0.8
    usage_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'description': self.description,
            'project_id': self.project_id,
            'tags': self.tags,
            'quality_score': self.quality_score,
            'usage_count': self.usage_count,
            'created_at': self.created_at
        }


class KnowledgeGraph:
    """
    跨项目知识图谱
    
    管理项目节点、知识边和知识项，支持查询和推荐。
    """
    
    def __init__(self, storage_path: str = "./data/knowledge_graph"):
        self.storage_path = storage_path
        self.projects: Dict[str, ProjectNode] = {}
        self.edges: List[KnowledgeEdge] = []
        self.knowledge_items: Dict[str, KnowledgeItem] = {}
        
        self._ensure_storage()
        self._load_graph()
    
    def _ensure_storage(self):
        """确保存储目录存在"""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def _load_graph(self):
        """加载图谱数据"""
        graph_file = os.path.join(self.storage_path, "graph.json")
        if os.path.exists(graph_file):
            try:
                with open(graph_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 加载项目节点
                    for p_data in data.get('projects', []):
                        project = ProjectNode(**p_data)
                        self.projects[project.project_id] = project
                    
                    # 加载知识边
                    for e_data in data.get('edges', []):
                        edge = KnowledgeEdge(**e_data)
                        self.edges.append(edge)
                    
                    # 加载知识项
                    for k_data in data.get('knowledge_items', []):
                        item = KnowledgeItem(**k_data)
                        self.knowledge_items[item.id] = item
                    
                    print(f"📚 Loaded knowledge graph: {len(self.projects)} projects, "
                          f"{len(self.edges)} edges, {len(self.knowledge_items)} items")
            except Exception as e:
                print(f"⚠️  Failed to load knowledge graph: {e}")
    
    def save_graph(self):
        """保存图谱数据"""
        graph_file = os.path.join(self.storage_path, "graph.json")
        try:
            data = {
                'projects': [p.to_dict() for p in self.projects.values()],
                'edges': [e.to_dict() for e in self.edges],
                'knowledge_items': [k.to_dict() for k in self.knowledge_items.values()]
            }
            
            with open(graph_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved knowledge graph: {len(self.projects)} projects, "
                  f"{len(self.edges)} edges, {len(self.knowledge_items)} items")
        except Exception as e:
            print(f"❌ Failed to save knowledge graph: {e}")
    
    def add_project(self, project_id: str, name: str, language: str,
                   framework: Optional[str] = None, domain: Optional[str] = None,
                   metadata: Optional[Dict] = None) -> ProjectNode:
        """
        添加项目节点
        
        Args:
            project_id: 项目ID
            name: 项目名称
            language: 编程语言
            framework: 框架
            domain: 领域
            metadata: 元数据
            
        Returns:
            创建的项目节点
        """
        if project_id in self.projects:
            print(f"⚠️  Project {project_id} already exists, updating...")
        
        project = ProjectNode(
            project_id=project_id,
            name=name,
            language=language,
            framework=framework,
            domain=domain,
            metadata=metadata or {}
        )
        
        self.projects[project_id] = project
        self.save_graph()
        
        print(f"✅ Added project: {name} ({project_id})")
        return project
    
    def add_knowledge_edge(self, source_project: str, target_project: str,
                          relation_type: str, strength: float,
                          knowledge_items: Optional[List[str]] = None,
                          metadata: Optional[Dict] = None) -> KnowledgeEdge:
        """
        添加知识边
        
        Args:
            source_project: 源项目ID
            target_project: 目标项目ID
            relation_type: 关系类型
            strength: 关系强度 (0.0-1.0)
            knowledge_items: 相关知识项ID列表
            metadata: 元数据
            
        Returns:
            创建的知识边
        """
        # 验证项目存在
        if source_project not in self.projects:
            raise ValueError(f"Source project {source_project} not found")
        if target_project not in self.projects:
            raise ValueError(f"Target project {target_project} not found")
        
        edge = KnowledgeEdge(
            source_project=source_project,
            target_project=target_project,
            relation_type=relation_type,
            strength=min(1.0, max(0.0, strength)),  # 限制在 0-1 范围
            knowledge_items=knowledge_items or [],
            metadata=metadata or {}
        )
        
        self.edges.append(edge)
        self.save_graph()
        
        print(f"🔗 Added edge: {source_project} --[{relation_type}]--> {target_project} "
              f"(strength: {strength:.2f})")
        return edge
    
    def add_knowledge_item(self, item_id: str, item_type: str, title: str,
                          description: str, project_id: str,
                          tags: Optional[List[str]] = None,
                          quality_score: float = 0.8) -> KnowledgeItem:
        """
        添加知识项
        
        Args:
            item_id: 知识项ID
            item_type: 类型 (skill, pattern, solution, error_fix)
            title: 标题
            description: 描述
            project_id: 所属项目ID
            tags: 标签列表
            quality_score: 质量分数
            
        Returns:
            创建的知识项
        """
        if project_id not in self.projects:
            raise ValueError(f"Project {project_id} not found")
        
        item = KnowledgeItem(
            id=item_id,
            type=item_type,
            title=title,
            description=description,
            project_id=project_id,
            tags=tags or [],
            quality_score=quality_score
        )
        
        self.knowledge_items[item_id] = item
        self.save_graph()
        
        print(f"📝 Added knowledge item: {title} ({item_id})")
        return item
    
    def query_related_projects(self, project_id: str, 
                              min_strength: float = 0.3,
                              relation_types: Optional[List[str]] = None) -> List[Dict]:
        """
        查询与指定项目相关的项目
        
        Args:
            project_id: 项目ID
            min_strength: 最小关系强度
            relation_types: 关系类型过滤（可选）
            
        Returns:
            相关项目列表（包含关系信息）
        """
        if project_id not in self.projects:
            return []
        
        related = []
        
        for edge in self.edges:
            # 检查是否涉及该项目
            if edge.source_project == project_id:
                other_project = edge.target_project
            elif edge.target_project == project_id:
                other_project = edge.source_project
            else:
                continue
            
            # 过滤强度
            if edge.strength < min_strength:
                continue
            
            # 过滤关系类型
            if relation_types and edge.relation_type not in relation_types:
                continue
            
            # 获取对方项目信息
            if other_project in self.projects:
                project = self.projects[other_project]
                related.append({
                    'project': project.to_dict(),
                    'edge': edge.to_dict()
                })
        
        # 按关系强度排序
        related.sort(key=lambda x: x['edge']['strength'], reverse=True)
        
        return related
    
    def find_transferable_knowledge(self, source_project: str, target_project: str,
                                   min_quality: float = 0.7) -> List[KnowledgeItem]:
        """
        查找可从源项目迁移到目标项目的知识
        
        Args:
            source_project: 源项目ID
            target_project: 目标项目ID
            min_quality: 最低质量分数
            
        Returns:
            可迁移的知识项列表
        """
        if source_project not in self.projects or target_project not in self.projects:
            return []
        
        transferable = []
        
        # 查找源项目的高质量知识项
        for item in self.knowledge_items.values():
            if item.project_id != source_project:
                continue
            
            if item.quality_score < min_quality:
                continue
            
            # 检查是否已经迁移过
            already_transferred = any(
                edge.source_project == source_project and
                edge.target_project == target_project and
                item.id in edge.knowledge_items
                for edge in self.edges
                if edge.relation_type == RelationType.TRANSFERRED_KNOWLEDGE.value
            )
            
            if not already_transferred:
                transferable.append(item)
        
        # 按质量分数排序
        transferable.sort(key=lambda x: x.quality_score, reverse=True)
        
        return transferable
    
    def record_knowledge_transfer(self, source_project: str, target_project: str,
                                 knowledge_item_ids: List[str],
                                 success: bool, quality_impact: float = 0.0):
        """
        记录知识迁移
        
        Args:
            source_project: 源项目
            target_project: 目标项目
            knowledge_item_ids: 迁移的知识项ID列表
            success: 是否成功
            quality_impact: 对质量的影响
        """
        # 更新知识项的使用次数
        for item_id in knowledge_item_ids:
            if item_id in self.knowledge_items:
                self.knowledge_items[item_id].usage_count += 1
        
        # 添加或更新边
        existing_edge = None
        for edge in self.edges:
            if (edge.source_project == source_project and
                edge.target_project == target_project and
                edge.relation_type == RelationType.TRANSFERRED_KNOWLEDGE.value):
                existing_edge = edge
                break
        
        if existing_edge:
            # 更新现有边
            for item_id in knowledge_item_ids:
                if item_id not in existing_edge.knowledge_items:
                    existing_edge.knowledge_items.append(item_id)
            
            # 调整强度
            if success:
                existing_edge.strength = min(1.0, existing_edge.strength + 0.1)
            else:
                existing_edge.strength = max(0.0, existing_edge.strength - 0.1)
        else:
            # 创建新边
            self.add_knowledge_edge(
                source_project=source_project,
                target_project=target_project,
                relation_type=RelationType.TRANSFERRED_KNOWLEDGE.value,
                strength=0.5 if success else 0.3,
                knowledge_items=knowledge_item_ids,
                metadata={'success': success, 'quality_impact': quality_impact}
            )
        
        self.save_graph()
        print(f"🔄 Recorded knowledge transfer: {source_project} -> {target_project} "
              f"({len(knowledge_item_ids)} items, {'✅' if success else '❌'})")
    
    def search_knowledge(self, query: str, tags: Optional[List[str]] = None,
                        item_type: Optional[str] = None,
                        min_quality: float = 0.5) -> List[KnowledgeItem]:
        """
        搜索知识项
        
        Args:
            query: 搜索关键词
            tags: 标签过滤
            item_type: 类型过滤
            min_quality: 最低质量分数
            
        Returns:
            匹配的知识项列表
        """
        results = []
        query_lower = query.lower()
        
        for item in self.knowledge_items.values():
            # 质量过滤
            if item.quality_score < min_quality:
                continue
            
            # 类型过滤
            if item_type and item.type != item_type:
                continue
            
            # 标签过滤
            if tags and not any(tag in item.tags for tag in tags):
                continue
            
            # 文本搜索
            if (query_lower in item.title.lower() or
                query_lower in item.description.lower()):
                results.append(item)
        
        # 按质量分数和使用次数排序
        results.sort(key=lambda x: (x.quality_score, x.usage_count), reverse=True)
        
        return results
    
    def get_project_statistics(self, project_id: str) -> Dict:
        """
        获取项目统计信息
        
        Args:
            project_id: 项目ID
            
        Returns:
            统计信息字典
        """
        if project_id not in self.projects:
            return {}
        
        # 知识项统计
        project_items = [
            item for item in self.knowledge_items.values()
            if item.project_id == project_id
        ]
        
        # 边的统计
        project_edges = [
            edge for edge in self.edges
            if edge.source_project == project_id or edge.target_project == project_id
        ]
        
        # 计算平均质量
        avg_quality = (
            sum(item.quality_score for item in project_items) / len(project_items)
            if project_items else 0
        )
        
        return {
            'project': self.projects[project_id].to_dict(),
            'total_knowledge_items': len(project_items),
            'avg_quality_score': avg_quality,
            'total_connections': len(project_edges),
            'knowledge_by_type': {
                'skill': len([i for i in project_items if i.type == 'skill']),
                'pattern': len([i for i in project_items if i.type == 'pattern']),
                'solution': len([i for i in project_items if i.type == 'solution']),
                'error_fix': len([i for i in project_items if i.type == 'error_fix'])
            }
        }
    
    def visualize_graph(self, output_file: Optional[str] = None) -> str:
        """
        生成图谱可视化（简化版，输出文本格式）
        
        Args:
            output_file: 输出文件路径（可选）
            
        Returns:
            可视化的文本表示
        """
        lines = []
        lines.append("🕸️  Knowledge Graph Visualization")
        lines.append("=" * 60)
        
        # 列出所有项目
        lines.append("\n📦 Projects:")
        for project_id, project in self.projects.items():
            lines.append(f"  • {project.name} ({project_id})")
            lines.append(f"    Language: {project.language}, Framework: {project.framework or 'N/A'}")
        
        # 列出所有关系
        lines.append("\n🔗 Relationships:")
        for edge in self.edges:
            source_name = self.projects[edge.source_project].name if edge.source_project in self.projects else edge.source_project
            target_name = self.projects[edge.target_project].name if edge.target_project in self.projects else edge.target_project
            
            lines.append(f"  {source_name} --[{edge.relation_type}]--> {target_name}")
            lines.append(f"    Strength: {edge.strength:.2f}, Items: {len(edge.knowledge_items)}")
        
        visualization = "\n".join(lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(visualization)
            print(f"💾 Visualization saved to {output_file}")
        
        return visualization
