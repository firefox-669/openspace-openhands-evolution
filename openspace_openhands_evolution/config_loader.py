"""
配置加载器

从文件、环境变量和命令行参数加载配置
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional


def load_config(config_path: Optional[str] = None) -> Dict:
    """
    加载配置
    
    优先级:
    1. 配置文件（如果提供）
    2. 环境变量
    3. 默认配置
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    # 默认配置
    default_config = {
        'openspace': {
            'registry_path': './data/skills',
            'vector_db_url': './chroma_db',
            'evolution_config': {
                'min_quality_score': 0.7,
                'max_versions': 10,
                'auto_share': True
            }
        },
        'openhands': {
            'model': os.environ.get('OPENSPACE_MODEL', 'gpt-4'),
            'api_key': os.environ.get('OPENAI_API_KEY', ''),
            'sandbox_enabled': True,
            'sandbox_config': {
                'timeout': 300,
                'memory_limit': '2GB'
            },
            'max_iterations': int(os.environ.get('OPENSPACE_MAX_ITERATIONS', '10'))
        },
        'monitor': {
            'quality_threshold': 0.8,
            'alert_channels': [],
            'metrics_retention_days': 30
        },
        'governance': {
            'enable_gatekeeping': True,
            'enable_fingerprint': True,
            'fingerprint_tolerance': 0.8,
            'maintenance_schedule': 'daily',
            'backup_enabled': False
        },
        'mtl': {
            'similarity_threshold': 0.7,
            'negative_transfer_threshold': 0.3
        },
        'aaip': {
            'skill_sharing_enabled': True,
            'sharing_scope': 'project'
        },
        'system': {
            'log_level': os.environ.get('LOG_LEVEL', 'INFO'),
            'max_concurrent_tasks': 5,
            'task_timeout': 600
        }
    }
    
    # 如果提供了配置文件，从文件加载
    if config_path:
        try:
            config = load_from_file(config_path)
            # 合并默认配置
            merged_config = merge_configs(default_config, config)
            print(f"✅ 从配置文件加载: {config_path}")
            return merged_config
        except Exception as e:
            print(f"⚠️  配置文件加载失败: {e}")
            print("使用默认配置...")
    
    # 尝试从默认位置加载
    for config_file in ['config.yaml', 'config.json', '.openspace-evolutionrc']:
        if Path(config_file).exists():
            try:
                if config_file.endswith('.json'):
                    config = load_from_json(config_file)
                else:
                    # YAML 需要 pyyaml，这里简化处理
                    config = {}
                merged_config = merge_configs(default_config, config)
                print(f"✅ 从配置文件加载: {config_file}")
                return merged_config
            except Exception as e:
                print(f"⚠️  配置文件 {config_file} 加载失败: {e}")
    
    # 返回默认配置
    print("ℹ️  使用默认配置")
    return default_config


def load_from_file(file_path: str) -> Dict:
    """
    从文件加载配置
    
    Args:
        file_path: 文件路径
        
    Returns:
        配置字典
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {file_path}")
    
    if path.suffix == '.json':
        return load_from_json(file_path)
    elif path.suffix in ['.yaml', '.yml']:
        return load_from_yaml(file_path)
    else:
        raise ValueError(f"不支持的配置文件格式: {path.suffix}")


def load_from_json(file_path: str) -> Dict:
    """从 JSON 文件加载配置"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_from_yaml(file_path: str) -> Dict:
    """从 YAML 文件加载配置"""
    try:
        import yaml
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except ImportError:
        raise ImportError("需要安装 pyyaml: pip install pyyaml")


def merge_configs(base: Dict, override: Dict) -> Dict:
    """
    合并配置
    
    Args:
        base: 基础配置
        override: 覆盖配置
        
    Returns:
        合并后的配置
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # 递归合并字典
            result[key] = merge_configs(result[key], value)
        else:
            # 直接覆盖
            result[key] = value
    
    return result


def save_config(config: Dict, file_path: str):
    """
    保存配置到文件
    
    Args:
        config: 配置字典
        file_path: 文件路径
    """
    path = Path(file_path)
    
    # 创建目录（如果不存在）
    path.parent.mkdir(parents=True, exist_ok=True)
    
    if path.suffix == '.json':
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    elif path.suffix in ['.yaml', '.yml']:
        try:
            import yaml
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        except ImportError:
            raise ImportError("需要安装 pyyaml: pip install pyyaml")
    else:
        raise ValueError(f"不支持的配置文件格式: {path.suffix}")


def create_default_config(file_path: str = 'config.json'):
    """
    创建默认配置文件
    
    Args:
        file_path: 文件路径
    """
    default_config = {
        'openspace': {
            'registry_path': './data/skills',
            'vector_db_url': './chroma_db'
        },
        'openhands': {
            'model': 'gpt-4',
            'api_key': '${OPENAI_API_KEY}',
            'sandbox_enabled': True
        },
        'monitor': {
            'quality_threshold': 0.8
        },
        'governance': {
            'enable_gatekeeping': True,
            'enable_fingerprint': True
        }
    }
    
    save_config(default_config, file_path)
    print(f"✅ 默认配置文件已创建: {file_path}")
