# Contributing to OpenSpace-OpenHands-Evolution

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🚀 Quick Start

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/openspace-openhands-evolution.git`
3. **Create** a branch: `git checkout -b feature/your-feature`
4. **Make** your changes
5. **Test** your changes: `pytest tests/`
6. **Commit**: `git commit -m "Add your feature"`
7. **Push**: `git push origin feature/your-feature`
8. **Submit** a Pull Request

## 📋 Development Setup

```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/openspace-openhands-evolution.git
cd openspace-openhands-evolution

# Install in development mode
pip install -e .

# Install dev dependencies
pip install pytest pytest-asyncio flake8 black mypy
```

## 🧪 Testing

### Run all tests
```bash
pytest tests/ -v
```

### Run specific test file
```bash
pytest tests/test_orchestrator.py -v
```

### Run with coverage
```bash
pytest tests/ --cov=openspace_openhands_evolution
```

## 💻 Code Style

We use **Black** for code formatting and **flake8** for linting.

```bash
# Format code
black openspace_openhands_evolution/

# Check linting
flake8 openspace_openhands_evolution/

# Type checking
mypy openspace_openhands_evolution/
```

## 📝 Commit Messages

Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat(orchestrator): add hierarchical agent architecture
fix(config): handle missing config file gracefully
docs(readme): update installation instructions
test(orchestrator): add unit tests for TaskRequest
```

## 🎯 Areas Needing Contribution

### High Priority
- [ ] Implement real OpenSpace engine integration
- [ ] Implement real OpenHands engine integration
- [ ] Add more comprehensive tests
- [ ] Improve error handling and logging

### Medium Priority
- [ ] Add visualization for reasoning traces
- [ ] Implement skill marketplace
- [ ] Add plugin system
- [ ] Create tutorial notebooks

### Low Priority
- [ ] Add internationalization support
- [ ] Create web dashboard
- [ ] Add performance benchmarks
- [ ] Write blog posts and tutorials

## 🐛 Reporting Bugs

Use GitHub Issues with the following template:

```markdown
**Describe the bug**
A clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. ...
2. ...
3. ...

**Expected behavior**
What should happen.

**Environment:**
- OS: [e.g., Windows 11, Ubuntu 22.04]
- Python: [e.g., 3.12]
- Version: [e.g., 0.1.1]

**Additional context**
Any other information.
```

## 💡 Feature Requests

We welcome feature requests! Please:

1. Check existing issues first
2. Describe the use case
3. Explain why it's valuable
4. Suggest implementation approach (optional)

## 📖 Documentation

When adding features, please also:
- Update docstrings
- Add examples if applicable
- Update README if needed
- Add type hints

## 🔍 Code Review Process

All submissions require review:

1. **Automated checks**: CI must pass
2. **Code quality**: Follow style guidelines
3. **Tests**: New features need tests
4. **Documentation**: Must be documented
5. **Reviewer approval**: At least one maintainer

## 🏆 Recognition

Contributors will be recognized in:
- README contributors section
- Release notes
- Special thanks in documentation

## ❓ Questions?

- Open an issue with "question" label
- Join our community discussions
- Email: [maintainer email]

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
