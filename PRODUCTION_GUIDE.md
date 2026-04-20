# 生产环境使用指南

## 🚀 快速开始

### 1. 安装和配置

```bash
# Clone 项目
git clone https://github.com/yourusername/openspace-openhands-evolution.git
cd openspace-openhands-evolution

# 安装依赖
pip install -e .

# 运行设置脚本
python setup_production.py
```

### 2. 配置 API Key

**选项 A: 环境变量（推荐）**

```bash
# OpenAI
export OPENAI_API_KEY=sk-your-openai-key

# Anthropic
export ANTHROPIC_API_KEY=sk-ant-your-key
```

**选项 B: 配置文件**

编辑 `config.yaml`:
```yaml
llm:
  provider: openai
  model: gpt-4
  api_key: "sk-your-key"
```

### 3. 运行第一个任务

```bash
# 交互式模式
openspace-evolution

# 或直接运行任务
openspace-evolution run "Create a Flask REST API with user authentication"
```

---

## 💡 实际用例

### 用例 1: 创建 Web API

```bash
openspace-evolution run "
Create a Flask REST API for a todo list application with:
- CRUD operations (Create, Read, Update, Delete)
- SQLite database
- Input validation
- Error handling
- API documentation
"
```

**输出**: 
- `workspace/app.py` - Flask 应用
- `workspace/models.py` - 数据模型
- `workspace/requirements.txt` - 依赖列表

### 用例 2: 数据分析脚本

```bash
openspace-evolution run "
Write a Python script to:
1. Read a CSV file from 'data/sales.csv'
2. Calculate monthly revenue
3. Generate a summary report
4. Save results to 'output/report.txt'
"
```

### 用例 3: React 组件

```bash
openspace-evolution run "
Create a React component for a user profile card that shows:
- User avatar
- Name and bio
- Social media links
- Follow/unfollow button
Use TypeScript and styled-components.
" --language javascript --framework react
```

---

## 🔧 高级功能

### 跨项目技能迁移

```bash
# 从 project-a 迁移技能到 project-b
openspace-evolution transfer \
  --from project-a \
  --to project-b \
  --min-similarity 0.8
```

### 查看系统状态

```bash
openspace-evolution status
```

输出示例:
```
OpenSpace Engine: ✅ Running (15 skills)
OpenHands Engine: ✅ Running (GPT-4)
Monitor System: ✅ Running (threshold: 0.8)
Governance: ✅ Active (V-02, V-06 enabled)
```

---

## 🛡️ 安全特性

### 沙箱执行

所有代码在隔离环境中执行：
- ✅ 无法访问系统文件
- ✅ 超时保护（默认 30 秒）
- ✅ 输出限制（1MB）
- ✅ 危险命令阻止

### 权限控制

在 `config.yaml` 中配置：

```yaml
openhands:
  enable_file_operations: true
  allowed_directories:
    - ./workspace
    - ./output
  sandbox_timeout: 30
```

---

## 📊 监控和日志

### 查看执行日志

```bash
# 实时日志
tail -f logs/evolution.log

# 查看错误
grep ERROR logs/evolution.log
```

### 质量指标

每次执行都会记录：
- 执行时间
- 成功率
- Token 使用量
- 质量评分

---

## 🎯 最佳实践

### 1. 任务描述要清晰

❌ **不好**: "Create an API"

✅ **好**: "Create a Flask REST API for user management with JWT authentication, including registration, login, and profile update endpoints"

### 2. 指定技术栈

```bash
openspace-evolution run "Build a web scraper" \
  --language python \
  --framework beautifulsoup
```

### 3. 分步执行复杂任务

将大任务分解：
```bash
# Step 1: 设计数据库
openspace-evolution run "Design SQLite schema for blog"

# Step 2: 实现后端
openspace-evolution run "Implement Flask backend for blog"

# Step 3: 创建前端
openspace-evolution run "Create React frontend for blog"
```

### 4. 使用工作目录

```bash
# 生成的文件保存在 workspace/
ls workspace/

# 查看生成的代码
cat workspace/app.py
```

---

## 🔍 故障排除

### 问题 1: API Key 错误

```
Error: OpenAI API key not configured
```

**解决**:
```bash
export OPENAI_API_KEY=sk-your-key
# 或编辑 config.yaml
```

### 问题 2: 执行超时

```
Error: Execution timed out after 30 seconds
```

**解决**: 增加超时时间
```yaml
openhands:
  sandbox_timeout: 60  # 增加到 60 秒
```

### 问题 3: 代码执行失败

检查 `workspace/` 中的错误日志：
```bash
cat logs/evolution.log | grep ERROR
```

---

## 🌐 支持的 LLM 提供商

### OpenAI GPT-4

**优点**: 最强大的代码生成能力
**成本**: $0.03/1K tokens

```yaml
llm:
  provider: openai
  model: gpt-4
```

### Anthropic Claude-3

**优点**: 更好的长上下文理解
**成本**: $0.015/1K tokens

```yaml
llm:
  provider: anthropic
  model: claude-3-opus-20240229
```

### Ollama (本地)

**优点**: 免费、隐私保护
**缺点**: 需要本地 GPU

```bash
# 安装 Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 拉取模型
ollama pull llama2

# 配置
```

```yaml
llm:
  provider: ollama
  model: llama2
  base_url: http://localhost:11434
```

---

## 📈 性能优化

### 1. 缓存常用技能

技能会自动缓存，重复任务更快。

### 2. 并行执行

```python
import asyncio
from openspace_openhands_evolution import EvolutionOrchestrator, TaskRequest

async def run_parallel_tasks():
    orchestrator = EvolutionOrchestrator(config)
    
    tasks = [
        TaskRequest(id="task-1", description="Create API endpoint 1", ...),
        TaskRequest(id="task-2", description="Create API endpoint 2", ...),
    ]
    
    results = await asyncio.gather(
        *[orchestrator.execute_task(t) for t in tasks]
    )
    
    return results
```

### 3. 调整质量阈值

```yaml
monitor:
  quality_threshold: 0.7  # 降低以加快速度（默认 0.8）
```

---

## 🎓 学习资源

- [架构设计文档](ENGINEERING_CHECKLIST.md)
- [API 参考](examples.py)
- [配置选项](config.production.yaml)
- [贡献指南](CONTRIBUTING.md)

---

## 💬 获取帮助

- **Issues**: [GitHub Issues](https://github.com/yourusername/openspace-openhands-evolution/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/openspace-openhands-evolution/discussions)

---

**Happy Coding! 🚀**
