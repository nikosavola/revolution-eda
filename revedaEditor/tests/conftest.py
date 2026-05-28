"""Shared pytest fixtures for Revolution EDA tests."""

import pytest
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView


@pytest.fixture(scope="session")
def qapp():
    """Ensure a single QApplication instance exists for the test session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def scene(qtbot):
    """Provide a QGraphicsScene with a QGraphicsView for item-based tests."""
    view = QGraphicsView()
    qtbot.addWidget(view)
    scene = QGraphicsScene()
    view.setScene(scene)
    return scene
