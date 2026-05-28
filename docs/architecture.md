# Revolution EDA Architecture Guide

This document describes the internal architecture of Revolution EDA, including module
interactions, the data model, threading patterns, and plugin system.

## High-Level Architecture

Revolution EDA follows a layered architecture built on the Qt Graphics View framework
(PySide6). Each layer has clear responsibilities:

```
┌──────────────────────────────────────────────────────────────┐
│                    GUI Layer (gui/)                           │
│  Main window, editor windows, dialogs, property panels       │
│  Classes: revedaMain, editorWindow, schematicEditor,         │
│           layoutEditor, symbolEditor, fileDialogues           │
└────────────────────────────┬─────────────────────────────────┘
                             │ creates/manages
┌────────────────────────────▼─────────────────────────────────┐
│                  Scenes Layer (scenes/)                        │
│  QGraphicsScene subclasses handling drawing, selection,        │
│  mouse events, mode switching, item placement                 │
│  Classes: editorScene, schematicScene, symbolScene,           │
│           layoutScene                                          │
└────────────────────────────┬─────────────────────────────────┘
                             │ contains/manages
┌────────────────────────────▼─────────────────────────────────┐
│                  Common Layer (common/)                        │
│  QGraphicsItem subclasses: shapes, nets, labels, pins         │
│  Shared data types and geometry primitives                    │
│  Classes: symbolShape, schematicNet, layoutShapes, labels     │
└────────────────────────────┬─────────────────────────────────┘
                             │ uses
┌────────────────────────────▼─────────────────────────────────┐
│                  Backend Layer (backend/)                      │
│  Library model, data definitions, undo stack, PDK/plugin      │
│  loaders, thread management, process management               │
│  Classes: libraryItem, cellItem, viewItem, pluginsLoader,     │
│           startThread, undoStack                               │
└────────────────────────────┬─────────────────────────────────┘
                             │ reads/writes
┌────────────────────────────▼─────────────────────────────────┐
│                  I/O & Processing Layer                        │
│  fileio/: JSON load/save, GDS/SPICE/Verilog-A import/export  │
│  netlisting/: Xyce and Spectre netlist generation             │
│  checks/: Schematic validation and DRC                        │
└──────────────────────────────────────────────────────────────┘
```

## Module Dependency Diagram

```
reveda.py (entry point)
    └── revedaEditor/
        ├── gui/revedaMain.py ─────────────────┐
        │   ├── gui/editorWindow.py            │
        │   │   ├── gui/schematicEditor.py     │
        │   │   ├── gui/layoutEditor.py        │
        │   │   └── gui/symbolEditor.py        │
        │   ├── gui/libraryBrowser.py          │
        │   └── gui/pythonConsole.py           │
        │                                      │
        ├── scenes/ ◄──────────────────────────┤
        │   ├── editorScene.py (base)          │
        │   ├── schematicScene.py              │
        │   ├── layoutScene.py                 │
        │   └── symbolScene.py                 │
        │                                      │
        ├── common/ ◄──────────────────────────┤
        │   ├── shapes.py                      │
        │   ├── layoutShapes.py                │
        │   ├── net.py                         │
        │   └── labels.py                      │
        │                                      │
        ├── backend/ ◄─────────────────────────┘
        │   ├── dataDefinitions.py (shared types)
        │   ├── libBackEnd.py (library model)
        │   ├── libraryModelView.py
        │   ├── pluginsLoader.py
        │   ├── pdkLoader.py
        │   ├── startThread.py (threading)
        │   ├── undoStack.py
        │   └── processManager.py
        │
        ├── fileio/
        │   ├── loadJSON.py
        │   ├── importGDS.py / exportGDS.py
        │   ├── importSpice.py
        │   ├── importVeriloga.py
        │   ├── symbolEncoder.py / schematicEncoder.py / layoutEncoder.py
        │   └── extractedSchematic.py
        │
        ├── netlisting/
        │   ├── xyceNetlist.py
        │   └── spectreNetlist.py
        │
        └── checks/
            └── schematic.py
```

## Data Model

### Library Hierarchy

Revolution EDA uses a three-level library hierarchy modeled with Qt's `QStandardItem`:

```
Library (libraryItem)
  └── Cell (cellItem)
       └── View (viewItem)
            ├── schematic
            ├── symbol
            ├── layout
            └── veriloga (HDL)
```

**Key classes in `backend/libBackEnd.py`:**

| Class | Description |
|-------|-------------|
| `libraryItem` | Represents a design library on disk (a directory) |
| `cellItem` | Represents a cell within a library (a subdirectory) |
| `viewItem` | Represents a specific view of a cell (schematic, symbol, layout) |

### Data Definitions (`backend/dataDefinitions.py`)

Core data structures used throughout the application:

#### Layer Definitions

| Dataclass | Purpose |
|-----------|---------|
| `edLayer` | Editor layer with pen/brush colors, GDS mapping, visibility |
| `layLayer` | Layout layer extending edLayer with stipple pattern support |

#### Edit Mode State Machines

| Dataclass | Purpose |
|-----------|---------|
| `editModes` | Base editing modes (select, delete, move, copy, rotate, etc.) |
| `symbolModes` | Symbol-specific modes (drawPin, drawArc, drawRect, etc.) |
| `schematicModes` | Schematic modes (drawWire, drawBus, addInstance, etc.) |
| `layoutModes` | Layout modes (drawPath, addVia, drawPolygon, etc.) |
| `selectModes` | Selection filter base class |
| `schematicSelectModes` | Schematic selection filters (device, net, pin) |
| `layoutSelectModes` | Layout selection filters (instance, path, via, etc.) |

#### Named Tuples (Immutable Data Transfer)

| Tuple | Purpose |
|-------|---------|
| `viewNameTuple` | Identifies a view by (libraryName, cellName, viewName) |
| `cellTuple` | Identifies a cell by (libraryName, cellName) |
| `viewItemTuple` | References actual Qt items (libraryItem, cellItem, viewItem) |
| `layoutPinTuple` | Pin definition (name, direction, type, layer) |
| `viaDefTuple` | Via definition with min/max dimensions and spacing |
| `singleViaTuple` | Single via instance with specific width/height |
| `arrayViaTuple` | Array of vias with x/y spacing and counts |
| `rectCoords` | Rectangle coordinates (left, top, width, height) |
| `layoutPathDefTuple` | Path definition with width/length/spacing constraints |
| `layoutPathTuple` | Path instance with specific mode, width, and extensions |

### File Format

Revolution EDA uses JSON as its native file format. Each view is stored as a JSON file
with custom encoders for Qt types:

- `symbolEncoder.py` — Serializes symbol shapes and pins
- `schematicEncoder.py` — Serializes schematic nets, instances, and wires
- `layoutEncoder.py` — Serializes layout paths, vias, and polygons
- `loadJSON.py` — Deserializes all view types from JSON

## Graphics Architecture

### Qt Graphics View Framework

The application is built on Qt's Graphics View Framework:

```
QMainWindow (editorWindow)
  └── QGraphicsView (editorView)
       └── QGraphicsScene (editorScene)
            ├── QGraphicsItem (symbolShape, schematicNet, ...)
            ├── QGraphicsItem (...)
            └── ...
```

### Scene Hierarchy

All scenes inherit from `editorScene` which provides:
- Grid drawing and snapping
- Common selection handling
- Copy/paste clipboard management
- Undo/redo integration
- Mode-based event dispatch

Specialized scenes add domain-specific behavior:

| Scene | Responsibilities |
|-------|-----------------|
| `symbolScene` | Pin placement, shape drawing, symbol origin |
| `schematicScene` | Wire routing, instance placement, net naming |
| `layoutScene` | Path routing, via arrays, DRC-aware operations |

### Shape Hierarchy

```
QGraphicsItem
  └── symbolShape (base for all shapes)
       ├── symbolRectangle
       ├── symbolCircle
       ├── symbolArc
       ├── symbolLine
       ├── symbolPolygon
       ├── symbolPin
       ├── text
       └── schematicSymbol
            └── schematicPin
```

Layout shapes have a parallel hierarchy in `common/layoutShapes.py`.

## Threading Model

Revolution EDA uses Qt's thread pool pattern for background operations.

### Architecture

```
Main Thread (GUI)
  │
  ├── QThreadPool (global pool)
  │     ├── startThread (QRunnable) ──► workerSignals
  │     ├── startThread (QRunnable) ──► workerSignals
  │     └── ...
  │
  └── QTimer (event loop integration)
```

### Implementation (`backend/startThread.py`)

The `startThread` class wraps any callable for asynchronous execution:

```python
class workerSignals(QObject):
    """Signal bridge between worker thread and main thread."""
    finished = Signal()       # Emitted when work completes (success or failure)
    error = Signal(tuple)     # Emitted on exception: (type, args, traceback)
    result = Signal(object)   # Emitted with return value on success

class startThread(QRunnable):
    """Executes a callable in Qt's thread pool."""
    def __init__(self, fn: Callable, *args, **kwargs):
        ...
    def run(self):
        # Execute fn, emit result or error, always emit finished
```

### Usage Pattern

```python
from PySide6.QtCore import QThreadPool
from revedaEditor.backend.startThread import startThread

# Create and configure worker
worker = startThread(expensive_function, arg1, arg2)
worker.signals.result.connect(self.handleResult)
worker.signals.error.connect(self.handleError)
worker.signals.finished.connect(self.onComplete)

# Submit to thread pool
QThreadPool.globalInstance().start(worker)
```

### Thread Safety Rules

1. **Never modify GUI elements from worker threads** — Use signals to communicate results
   back to the main thread
2. **The `finished` signal always fires** — Even on exceptions (via `try/finally`)
3. **Use `QTimer` for periodic main-thread tasks** — Not threads
4. **Scene modifications must happen on the main thread** — Connect worker signals to
   scene update slots

## Plugin System

### Plugin Architecture

Plugins are dynamically loaded Python packages from the `plugins/` directory:

```
plugins/
  └── myPlugin/
       ├── __init__.py      # Package entry point
       ├── myPlugin.py      # Plugin implementation
       └── config.json      # Menu integration configuration
```

### Plugin Loading (`backend/pluginsLoader.py`)

The `pluginsLoader` class:
1. Scans `plugins/` for Python packages using `pkgutil.iter_modules`
2. Imports each package with `importlib.import_module`
3. Reads `config.json` for menu integration
4. Registers menu actions with editor windows

### config.json Schema

```json
{
  "plugin_name": "myPlugin",
  "plugin_version": "1.0.0",
  "description": "Description of the plugin",
  "menu_items": [
    {
      "location": "menuBar",
      "menu": "Tools",
      "action": "My Action",
      "module": "myPlugin",
      "callback": "myCallback",
      "shortcut": "Ctrl+M",
      "apply": ["schematicEditor", "symbolEditor", "layoutEditor"]
    }
  ]
}
```

### Plugin Capabilities

Plugins can:
- **Add menu items** to any editor window (schematic, symbol, layout)
- **Register custom view types** via `viewTypes` module attribute
- **Create and open custom cell views** via `createCellView` and `openCellView`
- **Access the application instance** via `QApplication.instance()`

### Editor Applicability

The `"apply"` field in config.json controls which editors receive the menu item:
- `"schematicEditor"` — Schematic editor windows
- `"symbolEditor"` — Symbol editor windows
- `"layoutEditor"` — Layout editor windows

## PDK (Process Design Kit) System

PDKs are loaded dynamically via `backend/pdkLoader.py`:

- PDK modules define layer stacks, via definitions, and design rules
- The `defaultPDK/` directory contains the built-in PDK
- PDKs can be switched at runtime via the PDK Registry (`gui/pdkRegistry.py`)

## Undo/Redo System

Implemented in `backend/undoStack.py` using Qt's `QUndoStack`:

- Each editor scene has its own undo stack
- Operations are encapsulated as `QUndoCommand` subclasses
- Supports command compression for continuous operations (e.g., dragging)

## Netlisting

The netlisting subsystem (`netlisting/`) traverses the schematic hierarchy and generates
simulator-compatible netlists:

| Module | Target Simulator |
|--------|-----------------|
| `xyceNetlist.py` | Sandia Xyce (open-source SPICE) |
| `spectreNetlist.py` | Cadence Spectre |

Both modules perform:
1. Hierarchical design traversal
2. Instance parameter resolution
3. Net connectivity extraction
4. Subcircuit generation
5. Top-level netlist assembly

## Design Checks

The `checks/` module provides:
- **Schematic checks** (`schematic.py`): Floating nets, unconnected pins, naming
  conflicts
- **LVS** (`backend/LVSModelView.py`): Layout vs. Schematic comparison
- **DRC** (`backend/drcModelView.py`): Design Rule Check results display

## Key Design Patterns

| Pattern | Where Used |
|---------|-----------|
| Qt Model-View | Library browser, LVS results, DRC results |
| Qt Graphics View | All editors (schematic, symbol, layout) |
| Signal-Slot | All inter-component communication |
| State Machine | Edit modes (dataclass with `setMode()`) |
| Factory | PDK/Plugin loaders, view creation |
| Command | Undo/redo operations |
| Thread Pool | Background file I/O, netlisting |
| Observer | Property change notification via Qt signals |
