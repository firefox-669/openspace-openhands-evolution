# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Hierarchical agent architecture (MM-WebAgent inspired)
- Interpretable reasoning traces (RadAgent inspired)
- Planning layer for task decomposition
- Execution step tracking
- Complete test suite with pytest
- GitHub Actions CI/CD pipeline
- CONTRIBUTING.md guide
- CODE_OF_CONDUCT.md

### Changed
- Improved `__init__.py` with lazy imports (OpenSpace pattern)
- Enhanced TaskResult with reasoning_trace and execution_steps
- Updated README with new features

## [0.1.1] - 2026-04-20

### Added
- Three-layer agent architecture: Planning → Coordination → Execution
- Complete reasoning trace for every task execution
- `_planning_layer()` method for hierarchical task decomposition
- Example demonstrating interpretable AI (`example_interpretable_reasoning`)
- Unit tests for core components
- CI/CD workflow with multi-platform testing

### Changed
- Upgraded version from 0.1.0 to 0.1.1
- Enhanced orchestrator with detailed execution tracking
- Improved code documentation

## [0.1.0] - 2026-04-19

### Added
- Initial release
- Core EvolutionOrchestrator implementation
- Four-stage governance process
- Cross-project skill transfer (MTL + AAIP)
- CLI interface with interactive mode
- Configuration management system
- Environment fingerprint system
- Basic monitoring and quality metrics

---

## Version History

- **0.1.1** (2026-04-20): Hierarchical architecture & interpretable reasoning
- **0.1.0** (2026-04-19): Initial framework release
