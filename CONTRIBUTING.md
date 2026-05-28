# Contributing to Revolution EDA

Thank you for your interest in contributing to Revolution EDA! This guide will help you get
started with development, understand our coding standards, and navigate the contribution process.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)

## Development Setup

### Prerequisites

- Python 3.12 or later (< 3.15)
- [Poetry](https://python-poetry.org/) for dependency management
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/eskiyerli/revolution-eda.git
   cd revolution-eda
   ```

2. **Install dependencies with Poetry:**
   ```bash
   poetry install
   ```

3. **Activate the virtual environment:**
   ```bash
   poetry shell
   ```

4. **Run the application:**
   ```bash
   reveda
   ```

### Platform-Specific Notes

- **Linux:** Ensure Qt6 dependencies are installed. On Ubuntu/Debian:
  ```bash
  sudo apt install libgl1-mesa-dev libxkbcommon-x11-0
  ```
- **macOS:** No additional dependencies required.
- **Windows:** No additional dependencies required.

## Project Structure

```
revolution-eda/
├── reveda.py              # Application entry point
├── revedaEditor/          # Main package
│   ├── backend/           # Library management, threading, data definitions
│   ├── common/            # Shared shapes, nets, labels
│   ├── gui/               # Qt windows, editors, dialogs
│   ├── scenes/            # QGraphicsScene implementations
│   ├── fileio/            # File import/export (GDS, SPICE, Verilog-A)
│   ├── netlisting/        # Circuit netlisting (Xyce, Spectre)
│   ├── checks/            # Design rule and schematic checks
│   ├── resources/         # Qt resources
│   └── tests/             # Test suite
├── plugins/               # Plugin directory
├── defaultPDK/            # Default Process Design Kit
├── docs/                  # User documentation
└── pyproject.toml         # Project configuration
```

See [docs/architecture.md](docs/architecture.md) for a detailed architecture overview.

## Coding Standards

### Style Guide

- **Formatter:** [Black](https://github.com/psf/black) with line length of 92 characters
  (configured via `tool.ruff` in `pyproject.toml`)
- **Linter:** [Ruff](https://docs.astral.sh/ruff/) for fast Python linting
- **Type Hints:** Use type annotations for all function signatures and class attributes
- **Naming Conventions:**
  - Classes: `camelCase` (following Qt conventions, e.g., `editorWindow`, `schematicScene`)
  - Functions/methods: `camelCase` (e.g., `createCellView`, `loadJSON`)
  - Constants: `UPPER_SNAKE_CASE`
  - Private members: prefix with `_` (e.g., `_libraryPath`)

### Code Formatting

Before submitting, format your code:
```bash
black .
```

### Docstrings

Use triple-quoted docstrings for all public classes and methods:
```python
class editorScene(QGraphicsScene):
    """Base class for all editor scenes (schematic, symbol, layout).

    Manages the graphics items, grid drawing, selection state, and
    coordinate transformations for a given editor view.
    """

    def addItem(self, item: QGraphicsItem) -> None:
        """Add a graphics item to the scene.

        Args:
            item: The QGraphicsItem to add to the scene.
        """
```

### Qt/PySide6 Conventions

- Use PySide6 imports (not PyQt6)
- Use `Signal` and `Slot` from `PySide6.QtCore`
- Prefer Qt's Model-View architecture for data display
- Use `QGraphicsScene`/`QGraphicsItem` for visual editors

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/description` — New features
- `fix/description` — Bug fixes
- `docs/description` — Documentation changes
- `refactor/description` — Code refactoring

### Commit Messages

Write clear, concise commit messages:
```
type: short description

Longer explanation if needed. Wrap at 72 characters.
Reference issues with #number.
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

### Working with the Codebase

1. **Graphics items** are in `revedaEditor/common/` (shapes, nets, labels)
2. **Editor logic** lives in `revedaEditor/scenes/` (mouse handling, drawing modes)
3. **UI components** are in `revedaEditor/gui/` (windows, dialogs, menus)
4. **Data persistence** is handled in `revedaEditor/fileio/` (JSON-based format)
5. **Background tasks** use `QRunnable` via `revedaEditor/backend/startThread.py`

## Pull Request Process

1. **Create a feature branch** from `master`:
   ```bash
   git checkout -b feature/my-change
   ```

2. **Make your changes** following the coding standards above.

3. **Run tests** to ensure nothing is broken:
   ```bash
   pytest revedaEditor/tests/
   ```

4. **Format your code:**
   ```bash
   black .
   ```

5. **Push and open a Pull Request** against `master`.

6. **PR Requirements:**
   - Clear description of what changed and why
   - Tests for new functionality
   - No regressions in existing tests
   - Code formatted with Black

7. **Review Process:**
   - At least one maintainer review required
   - Address all review comments
   - Squash commits if requested

## Testing

### Running Tests

```bash
# Run all tests
pytest revedaEditor/tests/

# Run a specific test file
pytest revedaEditor/tests/test_netlisting.py

# Run with verbose output
pytest -v revedaEditor/tests/
```

### Writing Tests

- Place tests in `revedaEditor/tests/`
- Use `pytest` as the test framework
- For Qt-related tests, use `pytest-qt` with `qtbot` fixture
- Name test files `test_*.py` and test functions `test_*`

### Test Structure

```python
import pytest
from PySide6.QtCore import Qt

def test_feature_description(qtbot):
    """Test that feature behaves correctly."""
    # Arrange
    widget = MyWidget()
    qtbot.addWidget(widget)

    # Act
    result = widget.doSomething()

    # Assert
    assert result == expected_value
```

## Documentation

- **User docs:** Markdown files in `docs/`
- **Architecture docs:** `docs/architecture.md`
- **API docs:** Docstrings in source code (Sphinx-generated)
- **Plugin docs:** `docs/plugins.md` and `docs/binaryPlugins.md`

When adding new features, update the relevant documentation.

## Getting Help

- Open an issue for bugs or feature requests
- Check existing issues before opening a new one
- For questions about the codebase, refer to `docs/architecture.md`

## License

By contributing, you agree that your contributions will be licensed under the
Mozilla Public License 2.0 with Commons Clause, as specified in the project's license file.

Add-ons and extensions developed for this software may be distributed under their own
separate licenses.
