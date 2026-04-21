# 生产环境部署指南

> **目标**: 让用户 clone 后 5 分钟内即可在生产环境运行

---

## 🚀 快速开始（3 种方式）

### **方式 1: Docker Compose（推荐）** ⭐

**最简单，适合生产环境**

```bash
# 1. Clone 项目
git clone https://github.com/yourusername/openspace-openhands-evolution.git
cd openspace-openhands-evolution

# 2. 配置 API Keys
cp .env.example .env
nano .env  # 编辑并填入你的 API Keys

# 3. 一键启动
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 进入容器执行任务
docker-compose exec openspace-evolution python -m openspace_openhands_evolution run "Create a Flask API"
```

**停止服务**:
```bash
docker-compose down
```

**更新到最新版本**:
```bash
git pull
docker-compose up -d --build
```

---

### **方式 2: Docker（单容器）**

```bash
# 1. Build 镜像
docker build -t openspace-evolution:latest .

# 2. 运行容器
docker run -d \
  --name openspace-evolution \
  -e OPENAI_API_KEY=sk-your-key \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/workspace:/app/workspace \
  -v $(pwd)/logs:/app/logs \
  openspace-evolution:latest

# 3. 执行任务
docker exec -it openspace-evolution python -m openspace_openhands_evolution run "Your task here"
```

---

### **方式 3: 本地安装（开发环境）**

```bash
# 1. Clone 项目
git clone https://github.com/yourusername/openspace-openhands-evolution.git
cd openspace-openhands-evolution

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -e .

# 4. 配置
cp .env.example .env
# 编辑 .env 文件，填入 API Keys

# 5. 运行
python -m openspace_openhands_evolution
```

---

## ⚙️ 配置说明

### **环境变量 (.env)**

```bash
# === LLM API Keys (必填) ===
OPENAI_API_KEY=sk-xxx          # OpenAI API Key
ANTHROPIC_API_KEY=sk-ant-xxx   # Anthropic API Key

# === 应用配置 ===
LOG_LEVEL=INFO                 # 日志级别: DEBUG, INFO, WARNING, ERROR
QUALITY_THRESHOLD=0.8          # 质量阈值 (0.0-1.0)
MAX_RETRIES=3                  # 最大重试次数
SANDBOX_TIMEOUT=30             # 沙箱超时时间（秒）

# === 存储路径 ===
DATA_DIR=./data                # 数据存储目录
WORKSPACE_DIR=./workspace      # 工作目录
OUTPUT_DIR=./output            # 输出目录
LOG_DIR=./logs                 # 日志目录
```

### **配置文件 (config.yaml)**

```yaml
# LLM 配置
llm:
  provider: openai             # openai, anthropic, ollama
  model: gpt-4                 # 模型名称
  temperature: 0.7             # 温度参数
  max_tokens: 4096             # 最大 token 数

# OpenSpace 配置
openspace:
  registry_path: ./data/skills
  evolution_enabled: true
  quality_threshold: 0.8

# OpenHands 配置
openhands:
  enable_file_operations: true
  allowed_directories:
    - ./workspace
    - ./output
  sandbox_timeout: 30

# 监控配置
monitor:
  quality_threshold: 0.8
  alert_on_failure: true

# 策略引擎配置
strategy:
  storage_path: ./data/strategy_history
  default_strategy: balanced

# 知识图谱配置
knowledge_graph:
  storage_path: ./data/knowledge_graph

# 错误预测配置
error_prediction:
  storage_path: ./data/error_patterns
```

---

## 🔒 安全最佳实践

### **1. API Key 管理**

❌ **不要**:
```bash
# 不要在代码中硬编码
api_key = "sk-xxx"

# 不要提交 .env 到 Git
git add .env  # ❌
```

✅ **应该**:
```bash
# 使用环境变量
export OPENAI_API_KEY=sk-xxx

# 或使用 .env 文件（确保在 .gitignore 中）
cp .env.example .env
# 编辑 .env
```

### **2. 沙箱安全**

默认配置已启用沙箱隔离：
- ✅ 无法访问系统文件
- ✅ 超时保护（30秒）
- ✅ 输出限制（1MB）
- ✅ 危险命令阻止

**自定义安全策略**:
```yaml
openhands:
  enable_file_operations: true
  allowed_directories:
    - ./workspace
    - ./output
  blocked_commands:
    - rm -rf /
    - sudo
    - chmod 777
  sandbox_timeout: 30
  max_output_size: 1048576  # 1MB
```

### **3. 权限控制**

**Linux/Mac**:
```bash
# 设置合适的文件权限
chmod 755 workspace/
chmod 644 config.yaml
chmod 600 .env  # 只有所有者可读写
```

**Docker**:
```yaml
# 以非 root 用户运行
services:
  openspace-evolution:
    user: "1000:1000"  # UID:GID
```

---

## 📊 监控与日志

### **查看实时日志**

```bash
# Docker Compose
docker-compose logs -f

# 或直接查看日志文件
tail -f logs/evolution.log
```

### **日志级别**

```bash
# 在 .env 中设置
LOG_LEVEL=DEBUG    # 最详细，适合调试
LOG_LEVEL=INFO     # 默认，适合生产
LOG_LEVEL=WARNING  # 只记录警告和错误
LOG_LEVEL=ERROR    # 只记录错误
```

### **关键指标监控**

```python
# 获取系统状态
from openspace_openhands_evolution import EvolutionOrchestrator

orchestrator = EvolutionOrchestrator(config)
status = await orchestrator.get_system_status()

print(f"Strategy Records: {status['strategy_engine']['total_records']}")
print(f"Knowledge Items: {status['knowledge_graph']['knowledge_items']}")
print(f"Error Patterns: {status['error_prevention']['error_patterns']}")
```

---

## 🔧 性能优化

### **1. 缓存优化**

技能会自动缓存，重复任务更快。

**手动清理缓存**:
```bash
rm -rf data/skills/cache/*
```

### **2. 并发执行**

```python
import asyncio
from openspace_openhands_evolution import EvolutionOrchestrator, TaskRequest

async def run_parallel_tasks():
    orchestrator = EvolutionOrchestrator(config)
    
    tasks = [
        TaskRequest(id=f"task-{i}", description=f"Task {i}", project_id="proj")
        for i in range(5)
    ]
    
    results = await asyncio.gather(
        *[orchestrator.execute_task(t) for t in tasks]
    )
    
    return results
```

### **3. 资源限制（Docker）**

```yaml
services:
  openspace-evolution:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '0.5'
          memory: 1G
```

---

## 🆘 故障排除

### **问题 1: Docker 启动失败**

```bash
# 检查日志
docker-compose logs

# 常见原因：
# 1. API Key 未配置
# 2. 端口被占用
# 3. 磁盘空间不足
```

**解决**:
```bash
# 检查 .env 文件
cat .env

# 释放端口
docker-compose down

# 清理磁盘
docker system prune -a
```

### **问题 2: API 调用失败**

```
Error: OpenAI API key not configured
```

**解决**:
```bash
# 检查环境变量
echo $OPENAI_API_KEY

# 或在 .env 中配置
nano .env
```

### **问题 3: 执行超时**

```
Error: Execution timed out after 30 seconds
```

**解决**:
```yaml
# 增加超时时间
openhands:
  sandbox_timeout: 60  # 增加到 60 秒
```

### **问题 4: 内存不足**

```
Error: Killed (OOM)
```

**解决**:
```yaml
# 增加内存限制
deploy:
  resources:
    limits:
      memory: 8G
```

---

## 📈 生产环境检查清单

部署前确认：

- [ ] API Keys 已正确配置
- [ ] .env 文件未提交到 Git
- [ ] 防火墙规则已配置
- [ ] 日志轮转已启用
- [ ] 备份策略已制定
- [ ] 监控告警已设置
- [ ] 资源限制已配置
- [ ] 安全策略已审查
- [ ] 性能测试已通过
- [ ] 文档已更新

---

## 🔄 更新与维护

### **定期更新**

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重新构建
docker-compose up -d --build

# 3. 检查日志
docker-compose logs -f

# 4. 验证功能
docker-compose exec openspace-evolution python test_new_features.py
```

### **数据备份**

```bash
# 备份数据目录
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# 或使用 Docker 卷备份
docker run --rm \
  -v openspace-evolution_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/data-backup.tar.gz /data
```

### **日志轮转**

```bash
# 安装 logrotate
sudo apt-get install logrotate

# 配置日志轮转
cat > /etc/logrotate.d/openspace-evolution << EOF
/path/to/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
EOF
```

---

## 🎯 生产环境示例

### **完整的生产部署脚本**

```bash
#!/bin/bash
set -e

echo "🚀 Deploying OpenSpace-Evolution to Production..."

# 1. 拉取最新代码
git pull origin main

# 2. 构建镜像
docker-compose build

# 3. 停止旧容器
docker-compose down

# 4. 启动新容器
docker-compose up -d

# 5. 等待健康检查
echo "⏳ Waiting for service to be healthy..."
sleep 10

# 6. 验证部署
docker-compose exec openspace-evolution python -c "
from openspace_openhands_evolution import __version__
print(f'✅ Deployed version: {__version__}')
"

# 7. 显示日志
echo "📊 Service logs:"
docker-compose logs --tail=20

echo "✅ Deployment complete!"
```

---

## 📞 获取帮助

- **文档**: [README.md](README.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/openspace-openhands-evolution/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/openspace-openhands-evolution/discussions)

---

**Happy Deploying! 🎉**
