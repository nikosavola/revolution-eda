#    "Commons Clause" License Condition v1.0
#   #
#    The Software is provided to you by the Licensor under the License, as defined
#    below, subject to the following condition.
#
#    Without limiting other conditions in the License, the grant of rights under the
#    License will not include, and the License does not grant to you, the right to
#    Sell the Software.
#
#    For purposes of the foregoing, "Sell" means practicing any or all of the rights
#    granted to you under the License to provide to third parties, for a fee or other
#    consideration (including without limitation fees for hosting) a product or service whose value
#    derives, entirely or substantially, from the functionality of the Software. Any
#    license notice or attribution required by the License must also include this
#    Commons Clause License Condition notice.
#
#   Add-ons and extensions developed for this software may be distributed
#   under their own separate licenses.
#
#    Software: Revolution EDA
#    License: Mozilla Public License 2.0
#    Licensor: Revolution Semiconductor (Registered in the Netherlands)
#

"""Instance shapes for layout editor."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtWidgets import (
    QGraphicsItem,
    QStyle,
)

from revedaEditor.common.layoutShapes.base import layoutShape


class layoutInstance(layoutShape):
    def __init__(self, shapes: list[layoutShape]):
        super().__init__()

        # Direct attribute initialization
        self._shapes = shapes
        self._draft = False
        self._libraryName = self._cellName = self._viewName = self._instanceName = ""
        self._counter = 0

        # Cache pen creation
        self._selectedPen = self._get_cached_color("yellow")
        pen = QPen(self._selectedPen, 4, Qt.DashLine)
        pen.setCosmetic(True)
        self._selectedPen = pen

        # Batch flag operations
        self.setFiltersChildEvents(True)
        self.setHandlesChildEvents(True)
        self.setFlag(QGraphicsItem.ItemContainsChildrenInShape, True)

        # Defer expensive operations
        self._start = None
        self._shapes_set = False

        # Set shapes only if not empty
        if shapes:
            self.setShapes()

    def setShapes(self):
        if self._shapes_set or not self._shapes:
            return

        # Batch process all shapes
        for item in self._shapes:
            item.setFlags(QGraphicsItem.ItemStacksBehindParent)
            item.setFlag(QGraphicsItem.ItemIsSelectable, False)
            item.setParentItem(self)

        self._shapes_set = True

    def removeShapes(self):
        self.prepareGeometryChange()
        for item in self._shapes:
            item.setParentItem(None)
            del item
        self._shapes = list()

    def __repr__(self):
        return f"{self.__class__.__name__}({self._libraryName}, {self._cellName}, {self._viewName}, {self._instanceName})"

    def boundingRect(self):
        return self.childrenBoundingRect().normalized().adjusted(-2, -2, 2, 2)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.NonCosmeticBrushPatterns)
        if option.state & QStyle.State_Selected:
            # if self in self.scene().selectedItemsSet:
            painter.setPen(self._selectedPen)
            painter.drawRect(self.childrenBoundingRect())

    def sceneEvent(self, event):
        """
        Do not propagate event if shape needs to keep still.
        """
        if not (
                self.scene().selectModes.selectInstance
                or self.scene().selectModes.selectAll
        ):
            return False
        else:
            super().sceneEvent(event)
            return True

    @property
    def libraryName(self):
        return self._libraryName

    @libraryName.setter
    def libraryName(self, value):
        self._libraryName = value

    @property
    def cellName(self):
        return self._cellName

    @cellName.setter
    def cellName(self, value: str):
        self._cellName = value

    @property
    def viewName(self):
        return self._viewName

    @viewName.setter
    def viewName(self, value: str):
        self._viewName = value

    @property
    def instanceName(self):
        return self._instanceName

    @instanceName.setter
    def instanceName(self, value: str):
        assert isinstance(value, str)
        self._instanceName = value

    @property
    def shapes(self):
        return self._shapes

    @shapes.setter
    def shapes(self, value: list[layoutShape]):
        self.removeShapes()
        self._shapes = value
        self.setShapes()

    @property
    def start(self):
        if self._start is None:
            self._start = self.childrenBoundingRect().bottomLeft()
        return self._start.toPoint()

    @property
    def counter(self):
        return self._counter

    @counter.setter
    def counter(self, value: int):
        if isinstance(value, int):
            self._counter = value

    def addShape(self, shape: layoutShape):
        self._shapes.append(shape)
        shape.setParentItem(self)


class layoutPcell(layoutInstance):
    def __init__(self, shapes: list):
        super().__init__(shapes)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._libraryName}, {self._cellName}, {self._viewName}, {self._instanceName})"
