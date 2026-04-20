#!/usr/bin/env python3
"""
生产环境快速启动脚本

使用方法：
1. 复制 config.production.yaml 为 config.yaml
2. 填入你的 API key
3. 运行此脚本
"""

import os
import sys
from pathlib import Path


def check_dependencies():
    """检查依赖是否安装"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'openai',
        'anthropic',
        'pyyaml',
        'pydantic'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("\nInstall with:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    print("✅ All dependencies installed")
    return True


def check_config():
    """检查配置文件"""
    print("\n📝 Checking configuration...")
    
    config_file = Path("config.yaml")
    if not config_file.exists():
        print("❌ config.yaml not found")
        print("\nCreate from template:")
        print("cp config.production.yaml config.yaml")
        print("\nThen edit config.yaml and add your API keys")
        return False
    
    # 检查是否有 API key
    import yaml
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    llm_config = config.get('llm', {})
    provider = llm_config.get('provider', 'openai')
    api_key = llm_config.get('api_key', '')
    
    # 检查环境变量
    if provider == 'openai' and not api_key:
        api_key = os.getenv('OPENAI_API_KEY', '')
    
    if provider == 'anthropic' and not api_key:
        api_key = os.getenv('ANTHROPIC_API_KEY', '')
    
    if not api_key or api_key == 'your-api-key-here':
        print(f"❌ {provider.upper()} API key not configured")
        print(f"\nSet environment variable:")
        if provider == 'openai':
            print("export OPENAI_API_KEY=sk-your-key")
        elif provider == 'anthropic':
            print("export ANTHROPIC_API_KEY=sk-ant-your-key")
        print("\nOr edit config.yaml and add your API key")
        return False
    
    print(f"✅ {provider.upper()} API key configured")
    return True


def check_directories():
    """检查并创建必要的目录"""
    print("\n📁 Checking directories...")
    
    dirs = [
        'data/skills',
        'workspace',
        'output',
        'logs'
    ]
    
    for dir_path in dirs:
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"   Created: {dir_path}")
    
    print("✅ Directories ready")
    return True


def test_llm_connection():
    """测试 LLM 连接"""
    print("\n🤖 Testing LLM connection...")
    
    try:
        import asyncio
        from openspace_openhands_evolution.llm_integration import LLMRouter
        import yaml
        
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        llm_config = config.get('llm', {})
        router = LLMRouter(llm_config)
        
        async def test():
            response = await router.generate("Say 'Hello from OpenSpace-OpenHands-Evolution!'", max_tokens=50)
            return response
        
        response = asyncio.run(test())
        print(f"✅ LLM connection successful")
        print(f"   Response: {response[:60]}...")
        return True
    
    except Exception as e:
        print(f"❌ LLM connection failed: {e}")
        return False


def main():
    """主函数"""
    print("="*60)
    print("OpenSpace-OpenHands-Evolution Production Setup")
    print("="*60)
    print()
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Configuration", check_config),
        ("Directories", check_directories),
    ]
    
    all_passed = True
    for name, check_func in checks:
        if not check_func():
            all_passed = False
            print(f"\n⚠️  {name} check failed")
            print("Please fix the issues above before continuing.\n")
            sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ All checks passed!")
    print("="*60)
    
    # 询问是否测试 LLM
    test_now = input("\nTest LLM connection? (y/n): ").strip().lower()
    if test_now == 'y':
        if test_llm_connection():
            print("\n🎉 Ready to use!")
            print("\nStart with:")
            print("  openspace-evolution")
            print("\nOr run a task:")
            print('  openspace-evolution run "Create a Flask API"')
        else:
            print("\n⚠️  LLM test failed, but you can still try running")
    else:
        print("\n🎉 Setup complete!")
        print("\nStart with:")
        print("  openspace-evolution")


if __name__ == "__main__":
    main()
