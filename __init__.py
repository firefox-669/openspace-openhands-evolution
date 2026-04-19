"""
OpenSpace-OpenHands-Evolution 包

完整的自进化 AI 编程助手系统，整合：
- OpenSpace: 记忆管理 + 技能进化
- OpenHands: 代码执行 + 任务规划  
- MTL + AAIP: 跨项目知识迁移 + 标准化互操作
- 四阶段治理: 准入、运行、维护、进化

命令行使用:
    openspace-evolution                    # 交互模式
    openspace-evolution run "创建 API"     # 单查询模式
    openspace-evolution status             # 查看状态
"""

__version__ = "0.1.0"
__author__ = "OpenSpace Team"

from .orchestrator import EvolutionOrchestrator, TaskRequest, TransferRequest
from .config_loader import load_config, save_config, create_default_config

__all__ = [
    'EvolutionOrchestrator',
    'TaskRequest',
    'TransferRequest',
    'load_config',
    'save_config',
    'create_default_config',
]
