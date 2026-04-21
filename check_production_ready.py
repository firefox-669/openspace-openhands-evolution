"""
生产环境就绪检查脚本

验证系统是否已正确配置并可以安全部署到生产环境。
"""

import os
import sys
import json
from pathlib import Path


def check_python_version():
    """检查 Python 版本"""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 10):
        print(f"   ❌ Python 3.10+ required, found {sys.version_info.major}.{sys.version_info.minor}")
        return False
    print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def check_dependencies():
    """检查依赖包"""
    print("\n📦 Checking dependencies...")
    required_packages = [
        'litellm',
        'pyyaml',
        'asyncio',
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\n   Install missing packages: pip install {' '.join(missing)}")
        return False
    
    return True


def check_api_keys():
    """检查 API Keys"""
    print("\n🔑 Checking API Keys...")
    
    # 检查环境变量
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    # 检查 .env 文件
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if 'OPENAI_API_KEY=' in content and not openai_key:
                for line in content.split('\n'):
                    if line.startswith('OPENAI_API_KEY='):
                        openai_key = line.split('=', 1)[1].strip()
            if 'ANTHROPIC_API_KEY=' in content and not anthropic_key:
                for line in content.split('\n'):
                    if line.startswith('ANTHROPIC_API_KEY='):
                        anthropic_key = line.split('=', 1)[1].strip()
    
    has_key = False
    if openai_key and openai_key != 'sk-your-openai-key-here':
        print(f"   ✅ OpenAI API Key configured")
        has_key = True
    else:
        print(f"   ⚠️  OpenAI API Key not configured (optional)")
    
    if anthropic_key and anthropic_key != 'sk-ant-your-key-here':
        print(f"   ✅ Anthropic API Key configured")
        has_key = True
    else:
        print(f"   ⚠️  Anthropic API Key not configured (optional)")
    
    if not has_key:
        print(f"\n   ⚠️  Warning: No API keys configured")
        print(f"   You can still use Ollama (local models)")
        print(f"   See DEPLOYMENT.md for configuration instructions")
    
    return True  # 即使没有 API key 也可以继续（使用 Ollama）


def check_directories():
    """检查必要目录"""
    print("\n📁 Checking directories...")
    required_dirs = [
        'data/skills',
        'data/strategy_history',
        'data/knowledge_graph',
        'data/error_patterns',
        'workspace',
        'output',
        'logs',
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"   ✅ {dir_path}")
        else:
            print(f"   ⚠️  {dir_path} (will be created)")
            path.mkdir(parents=True, exist_ok=True)
    
    return all_exist


def check_config_files():
    """检查配置文件"""
    print("\n⚙️  Checking configuration files...")
    
    config_files = {
        'config.example.yaml': 'Example configuration',
        '.env.example': 'Example environment variables',
        'requirements.txt': 'Dependencies list',
    }
    
    all_exist = True
    for filename, description in config_files.items():
        if Path(filename).exists():
            print(f"   ✅ {filename} ({description})")
        else:
            print(f"   ❌ {filename} (missing)")
            all_exist = False
    
    return all_exist


def check_docker_setup():
    """检查 Docker 配置"""
    print("\n🐳 Checking Docker setup...")
    
    docker_files = {
        'Dockerfile': 'Docker build configuration',
        'docker-compose.yml': 'Docker Compose configuration',
        '.dockerignore': 'Docker ignore rules',
    }
    
    all_exist = True
    for filename, description in docker_files.items():
        if Path(filename).exists():
            print(f"   ✅ {filename} ({description})")
        else:
            print(f"   ⚠️  {filename} (optional)")
    
    return all_exist


def check_security():
    """检查安全配置"""
    print("\n🔒 Checking security...")
    
    issues = []
    
    # 检查 .env 是否在 .gitignore 中
    gitignore = Path('.gitignore')
    if gitignore.exists():
        with open(gitignore, 'r') as f:
            content = f.read()
            if '.env' in content:
                print(f"   ✅ .env is in .gitignore")
            else:
                print(f"   ⚠️  .env not in .gitignore")
                issues.append(".env should be in .gitignore")
    else:
        print(f"   ⚠️  .gitignore not found")
        issues.append(".gitignore file missing")
    
    # 检查敏感文件权限（仅 Linux/Mac）
    if os.name != 'nt':  # 非 Windows
        env_file = Path('.env')
        if env_file.exists():
            stat = os.stat(env_file)
            permissions = oct(stat.st_mode)[-3:]
            if permissions == '600':
                print(f"   ✅ .env file permissions are secure (600)")
            else:
                print(f"   ⚠️  .env file permissions: {permissions} (should be 600)")
                print(f"   Run: chmod 600 .env")
    
    if issues:
        print(f"\n   Security issues found:")
        for issue in issues:
            print(f"     - {issue}")
        return False
    
    return True


def check_tests():
    """检查测试套件"""
    print("\n🧪 Checking test suite...")
    
    test_files = [
        'tests/test_orchestrator.py',
        'test_new_features.py',
    ]
    
    all_exist = True
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"   ✅ {test_file}")
        else:
            print(f"   ⚠️  {test_file} (not found)")
            all_exist = False
    
    return all_exist


def check_documentation():
    """检查文档"""
    print("\n📚 Checking documentation...")
    
    docs = {
        'README.md': 'Main documentation',
        'DEPLOYMENT.md': 'Deployment guide',
        'IMPLEMENTATION_SUMMARY.md': 'Implementation details',
        'CHANGELOG.md': 'Version history',
        'CONTRIBUTING.md': 'Contribution guide',
    }
    
    all_exist = True
    for doc_file, description in docs.items():
        if Path(doc_file).exists():
            print(f"   ✅ {doc_file} ({description})")
        else:
            print(f"   ⚠️  {doc_file} (missing)")
    
    return all_exist


def run_production_readiness_check():
    """运行完整的生产就绪检查"""
    print("="*60)
    print("🔍 Production Readiness Check")
    print("="*60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("API Keys", check_api_keys),
        ("Directories", check_directories),
        ("Config Files", check_config_files),
        ("Docker Setup", check_docker_setup),
        ("Security", check_security),
        ("Tests", check_tests),
        ("Documentation", check_documentation),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n   ❌ Error checking {name}: {e}")
            results[name] = False
    
    # 总结
    print("\n" + "="*60)
    print("📊 Summary")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} - {name}")
    
    print("\n" + "="*60)
    if passed == total:
        print(f"✅ All checks passed! Ready for production deployment.")
        print("="*60)
        print("\nNext steps:")
        print("1. Configure your API keys in .env")
        print("2. Run: docker-compose up -d")
        print("3. See DEPLOYMENT.md for more details")
        return 0
    else:
        print(f"⚠️  {passed}/{total} checks passed.")
        print("="*60)
        print("\nPlease fix the issues above before deploying to production.")
        print("See DEPLOYMENT.md for troubleshooting.")
        return 1


if __name__ == "__main__":
    exit_code = run_production_readiness_check()
    sys.exit(exit_code)
