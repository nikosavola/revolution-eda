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

"""Polygon shape for layout editor."""

from PySide6.QtCore import (
    QPoint,
    QRectF,
    Qt,
)
from PySide6.QtGui import (
    QPolygonF,
)
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsSceneMouseEvent,
)

import revedaEditor.backend.dataDefinitions as ddef
from revedaEditor.common.layoutShapes.base import layoutShape

class layoutPolygon(layoutShape):
    __slots__ = (
        "_points",
        "_layer",
        "_polygon",
        "_selectedCorner",
        "_selectedCornerIndex",
    )

    def __init__(self, points: list, layer: ddef.layLayer):
        super().__init__()
        self._points = points
        self._layer = layer
        self._selectedCorner = QPoint(99999, 99999)
        self._selectedCornerIndex = 999

        # Defer expensive operations
        self._polygon = None
        self._definePensBrushes(self._layer)
        self.setZValue(self._layer.z)
        self._flipTuple = (1, 1)  # Direct assignment instead of property

    def __repr__(self):
        return f"layoutPolygon({self._points}, {self._layer})"

    def paint(self, painter, option, widget):
        # Cache frequently accessed values
        selected = self.isSelected()
        scale = self.scene().views()[0].transform().m11()

        # Set pen and brush based on selection state
        if selected:
            painter.setPen(self._selectedPen)
            self._updateTransformedBrush(self._selectedBrush, scale)
            # Use cached corner coordinates (avoid QPoint creation)
            if self._stretch and self._selectedCorner.x() != 99999:
                painter.drawEllipse(self._selectedCorner, 5, 5)
        else:
            painter.setPen(self._pen)
            self._updateTransformedBrush(self._brush, scale)

        painter.setBrush(self._transformedBrush)
        painter.drawPolygon(self.polygon)

    def boundingRect(self) -> QRectF:
        return self.polygon.boundingRect()

    @property
    def polygon(self):
        if self._polygon is None:
            self._polygon = QPolygonF(self._points)
        return self._polygon

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, layer: ddef.layLayer):
        self.prepareGeometryChange()
        self._layer = layer

    @property
    def points(self) -> list:
        return self._points

    @points.setter
    def points(self, value: list):
        self.prepareGeometryChange()
        self._points = value
        self._polygon = None  # Invalidate cache

    def addPoint(self, point: QPoint):
        self.prepareGeometryChange()
        self._points.append(point)
        self._polygon = None  # Invalidate cache

    @property
    def tempLastPoint(self):
        return self._points[-1]

    @tempLastPoint.setter
    def tempLastPoint(self, value: QPoint):
        self.prepareGeometryChange()
        self._polygon = QPolygonF([*self._points, value])

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mousePressEvent(event)
        if self._layer.selectable:
            self.setFlag(QGraphicsItem.ItemIsMovable, True)
            self.setFlag(QGraphicsItem.ItemIsSelectable, True)
            eventPos = event.pos().toPoint()
            if self._stretch:
                self.setFlag(QGraphicsItem.ItemIsMovable, False)
                for point in self._points:
                    if (
                            eventPos - point
                    ).manhattanLength() <= self.scene().snapDistance:
                        self._selectedCorner = point
                        self._selectedCornerIndex = self._points.index(point)
        else:
            self.setFlag(QGraphicsItem.ItemIsMovable, False)
            self.setFlag(QGraphicsItem.ItemIsSelectable, False)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        eventPos = event.pos().toPoint()
        if self._stretch and self._selectedCornerIndex != 999:
            self._points[self._selectedCornerIndex] = eventPos
            self.points = self._points
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        if self.stretch:
            self._stretch = False
            self._stretchSide = None
            self.setCursor(Qt.ArrowCursor)
            self._selectedCornerIndex = 999

