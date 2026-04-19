# OpenSpace-OpenHands-Evolution

Self-evolving AI programming assistant that integrates OpenSpace (memory/evolution) with OpenHands (execution).

## Features

- **Self-Evolution**: Learn from failures and optimize skills automatically
- **Cross-Project Reuse**: Transfer skills between projects using MTL + AAIP
- **Governance**: 4-stage quality control (gatekeeping, monitoring, maintenance, evolution)
- **CLI Interface**: Easy-to-use command-line tool

## Installation

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

**Version**: 0.1.0-alpha

This is an early-stage framework providing:
- ✅ Complete CLI interface
- ✅ Core orchestrator implementation
- ✅ Configuration management
- ⚠️ Engine implementations are stubs (need OpenSpace/OpenHands integration)

See `examples.py` for more usage examples.

## License

MIT
