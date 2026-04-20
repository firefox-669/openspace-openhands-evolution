# OpenSpace-OpenHands-Evolution

[![CI](https://github.com/yourusername/openspace-openhands-evolution/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/openspace-openhands-evolution/actions)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.1-orange.svg)](CHANGELOG.md)

Self-evolving AI programming assistant with hierarchical agent architecture and interpretable reasoning.

## ✨ Features

- **🏗️ Hierarchical Agent Architecture** (MM-WebAgent inspired): Planning → Coordination → Execution layers
- **🔍 Interpretable Reasoning** (RadAgent inspired): Complete reasoning trace for every task
- **🧬 Self-Evolution**: Learn from failures and optimize skills automatically
- **🌐 Cross-Project Reuse**: Transfer skills between projects using MTL + AAIP
- **🛡️ Governance**: 4-stage quality control (gatekeeping, monitoring, maintenance, evolution)
- **💻 CLI Interface**: Easy-to-use command-line tool

## 🚀 Installation

```bash
pip install -e .
```

## Quick Start

### Command Line

```bash
# Interactive mode
openspace-evolution

# Run a single task
openspace-evolution run "Create a Flask API"

# Check status
openspace-evolution status

# Cross-project transfer
openspace-evolution transfer --from project-a --to project-b
```

### Python API

```python
import asyncio
from openspace_openhands_evolution import EvolutionOrchestrator, TaskRequest

async def main():
    config = {
        'openspace': {'registry_path': './data/skills'},
        'openhands': {'model': 'gpt-4'},
        'monitor': {'quality_threshold': 0.8},
    }
    
    orchestrator = EvolutionOrchestrator(config)
    
    task = TaskRequest(
        id="task-001",
        description="Create a Flask API",
        project_id="my-app",
        language="python"
    )
    
    result = await orchestrator.execute_task(task)
    print(result.output)

asyncio.run(main())
```

## Project Status

**Version**: 0.1.1-alpha

This is an early-stage framework providing:
- ✅ Complete CLI interface
- ✅ Core orchestrator implementation with hierarchical architecture
- ✅ Interpretable reasoning traces
- ✅ Configuration management
- ✅ Comprehensive test suite
- ✅ CI/CD pipeline
- ⚠️ Engine implementations are stubs (need OpenSpace/OpenHands integration)

See `examples.py` for more usage examples.

## 📁 Project Structure

```
openspace_openhands_evolution/
├── __init__.py              # Package initialization with lazy imports
├── __main__.py              # CLI entry point
├── orchestrator.py          # Core orchestrator (hierarchical architecture)
├── config_loader.py         # Configuration management
├── openspace_engine.py      # OpenSpace engine (stub)
├── openhands_engine.py      # OpenHands engine (stub)
├── examples.py              # Usage examples
├── tests/                   # Test suite
│   ├── __init__.py
│   └── test_orchestrator.py
├── .github/workflows/       # CI/CD
│   └── ci.yml
├── setup.py                 # Package setup
├── requirements.txt         # Dependencies
├── LICENSE                  # MIT License
├── README.md                # This file
├── CHANGELOG.md             # Version history
├── CONTRIBUTING.md          # Contribution guide
└── CODE_OF_CONDUCT.md       # Code of conduct
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

Quick start:
```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/openspace-openhands-evolution.git
cd openspace-openhands-evolution

# Install in development mode
pip install -e .
pip install pytest pytest-asyncio

# Run tests
pytest tests/ -v
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [MM-WebAgent](https://arxiv.org/abs/2604.15309v1) for hierarchical architecture
- Inspired by [RadAgent](https://arxiv.org/abs/2604.15231v1) for interpretable reasoning
- Built on concepts from OpenSpace and OpenHands projects

## 📬 Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/openspace-openhands-evolution/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/openspace-openhands-evolution/discussions)

---

⭐ If you find this project useful, please consider giving it a star!
