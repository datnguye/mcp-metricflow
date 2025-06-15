# Contributing to `mcp-metricflow`

[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/datnguye/mcp-metricflow/issues)

## Table of Contents

- [Contributing to `mcp-metricflow`](#contributing-to-mcp-metricflow)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Getting Started](#getting-started)
  - [Development Environment Setup](#development-environment-setup)
  - [Making Changes](#making-changes)
  - [Testing](#testing)
  - [Code Quality](#code-quality)
  - [Pull Request Process](#pull-request-process)
  - [Contribution Guidelines](#contribution-guidelines)
  - [Getting Help](#getting-help)

## Overview

Welcome to the `mcp-metricflow` project! We're excited that you're interested in contributing. This is an open source project that welcomes community contributions in various forms:

- **Code contributions**: Bug fixes, new features, performance improvements
- **Documentation**: Improving existing docs, adding examples, fixing typos
- **Testing**: Writing tests, reporting bugs, testing new features
- **Ideas and feedback**: Feature requests, architectural suggestions, use cases

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/mcp-metricflow.git
   cd mcp-metricflow
   ```
3. **Create a new branch** for your proposed changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes** and commit them
5. **Push changes** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Open a pull request** targeting the `main` branch

## Development Environment Setup

This project uses `uv` for dependency management and `poethepoet` for task automation. Follow these steps to set up your development environment:

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Set up the project**:
   ```bash
   # Create virtual environment and install all dependencies
   uv run poe setup

   # Install pre-commit hooks
   uv run poe setup-hooks

   # Copy environment template
   cp .env.template .env
   ```

3. **Configure your environment**:
   Edit the `.env` file with your specific configuration, particularly the `DBT_PROJECT_DIR` path.

## Making Changes

- **Follow the existing code style** and conventions
- **Write clear, descriptive commit messages**
- **Keep changes focused** - one feature or fix per pull request
- **Add tests** for new functionality
- **Update documentation** if your changes affect the public API or user experience

## Testing

Run the test suite to ensure your changes don't break existing functionality:

```bash
# Run all tests
uv run poe test

# Run tests with coverage report
uv run poe test-cov

# Run tests with coverage and fail if under 100%
uv run poe test-cov-fail
```

The project maintains 100% test coverage. Make sure your changes maintain this standard.

## Code Quality

This project uses `ruff` for code formatting and linting. Before submitting your pull request:

```bash
# Format code
uv run poe format

# Check for linting issues
uv run poe lint
```

**Important**: All linting issues must be resolved before your pull request can be merged.

## Pull Request Process

1. **Target the `main` branch** for all pull requests
2. **Provide a clear description** of the changes and why they're needed
3. **Reference any related issues** using GitHub's linking syntax (e.g., "Fixes #123")
4. **Ensure all tests pass** and code quality checks succeed
5. **Be responsive to feedback** from maintainers during the review process

### Automated Checks

Your pull request will automatically run:
- **Tests** with coverage reporting
- **Code quality checks** (ruff formatting and linting)
- **Type checking** (if applicable)

All checks must pass before your pull request can be merged.

## Contribution Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Keep functions focused and modular
- Add type hints where appropriate
- Write docstrings for public functions and classes

### Commit Messages
- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

### Documentation
- Update README.md if your changes affect installation or usage
- Add or update docstrings for new or modified functions
- Include examples in docstrings when helpful

## Getting Help

If you need help or have questions:

- **Check existing issues** on GitHub for similar problems or questions
- **Open a new issue** to report bugs or request features
- **Start a discussion** for general questions or ideas
- **Review the project documentation** in the README.md

We're here to help and appreciate your interest in contributing to `mcp-metricflow`!

---

Thank you for contributing to `mcp-metricflow`! 🎉
