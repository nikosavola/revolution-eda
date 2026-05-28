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

"""Rectangle shape for layout editor."""

from PySide6.QtCore import (
    QPoint,
    QRect,
    QRectF,
    Qt,
)
from PySide6.QtGui import (
    QColor,
    QPen,
)
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsSceneMouseEvent,
)

import revedaEditor.backend.dataDefinitions as ddef
from revedaEditor.common.layoutShapes.base import layoutShape


class layoutRect(layoutShape):
    sides = ["Left", "Right", "Top", "Bottom"]

    def __init__(
            self,
            start: QPoint,
            end: QPoint,
            layer: ddef.layLayer,
    ):
        super().__init__()
        self._rect = QRectF(start, end).normalized()
        self._start = self._rect.topLeft()
        self._end = self._rect.bottomRight()
        self._layer = layer
        if self._layer.selectable:
            self.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        else:
            self.setFlag(QGraphicsItem.ItemIsSelectable, False)
            self.setFlag(QGraphicsItem.ItemIsFocusable, False)
        self._stretch = False
        self._stretchSide = None
        self._stretchPen = QPen(QColor("red"), self._layer.pwidth, Qt.SolidLine)
        self._definePensBrushes(self._layer)
        self.setZValue(self._layer.z)
        self._stretchSidesMap = {
            self.sides[0]: (lambda r: r.topLeft(), lambda r: r.bottomLeft()),
            self.sides[1]: (lambda r: r.topRight(), lambda r: r.bottomRight()),
            self.sides[2]: (lambda r: r.topLeft(), lambda r: r.topRight()),
            self.sides[3]: (lambda r: r.bottomLeft(), lambda r: r.bottomRight()),
        }

    def __repr__(self):
        return f"layoutRect({self._start}, {self._end}, {self._layer})"

    def paint(self, painter, option, widget):
        rect = self._rect

        # Get scale once and cache it
        scale = self.scene().views()[0].transform().m11()

        if self.isSelected():
            painter.setPen(self._selectedPen)
            self._updateTransformedBrush(self._selectedBrush, scale)

            if self.stretch:
                painter.setPen(self._stretchPen)
                # Get the line endpoints from the mapping
                if self._stretchSide in self._stretchSidesMap:
                    start_func, end_func = self._stretchSidesMap[self._stretchSide]
                    painter.drawLine(start_func(rect), end_func(rect))
        else:
            painter.setPen(self._pen)
            self._updateTransformedBrush(self._brush, scale)
        painter.setBrush(self._transformedBrush)
        painter.drawRect(rect)

    def boundingRect(self):
        return self._rect.normalized().adjusted(-2, -2, 2, 2)

    @property
    def rect(self):
        return self._rect

    @rect.setter
    def rect(self, rect: QRect):
        self.prepareGeometryChange()
        self._rect = rect

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start: QPoint):
        self.prepareGeometryChange()
        self._rect = QRectF(start, self.end).normalized()
        self._start = start

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, end: QPoint):
        self.prepareGeometryChange()
        self._rect = QRectF(self.start, end).normalized()
        self._end = end

    @property
    def centre(self):
        return QPoint(
            int(self._rect.x() + self._rect.width() / 2),
            int(self._rect.y() + self._rect.height() / 2),
        )

    @property
    def height(self):
        return self.rect.height()

    @height.setter
    def height(self, height: int):
        self.prepareGeometryChange()
        self._rect.setHeight(height)

    @property
    def width(self):
        return self.rect.width()

    @width.setter
    def width(self, width):
        self.prepareGeometryChange()
        self.rect.setWidth(width)

    @property
    def left(self):
        return self.rect.left()

    @left.setter
    def left(self, left: int):
        self.rect.setLeft(left)

    @property
    def right(self):
        return self.rect.right()

    @right.setter
    def right(self, right: int):
        self.prepareGeometryChange()
        self.rect.setRight(right)

    @property
    def top(self):
        return self.rect.top()

    @top.setter
    def top(self, top: int):
        self.prepareGeometryChange()
        self.rect.setTop(top)

    @property
    def bottom(self):
        return self.rect.bottom()

    @bottom.setter
    def bottom(self, bottom: int):
        self.prepareGeometryChange()
        self.rect.setBottom(bottom)

    @property
    def origin(self):
        return self.rect.bottomLeft()

    @property
    def stretchSide(self):
        return self._stretchSide

    @stretchSide.setter
    def stretchSide(self, value: str):
        self.prepareGeometryChange()
        self._stretchSide = value

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, layer: ddef.layLayer):
        self.prepareGeometryChange()
        self._layer = layer

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mousePressEvent(event)

        if self._layer.selectable:
            self.setFlag(QGraphicsItem.ItemIsMovable, True)
            self.setFlag(QGraphicsItem.ItemIsSelectable, True)
            eventPos = event.pos().toPoint()
            if self._stretch:
                self.setFlag(QGraphicsItem.ItemIsMovable, False)
                if eventPos.x() == self._rect.left():
                    if self._rect.top() <= eventPos.y() <= self._rect.bottom():
                        self.setCursor(Qt.SizeHorCursor)
                        self._stretchSide = layoutRect.sides[0]
                elif eventPos.x() == self._rect.right():
                    if self._rect.top() <= eventPos.y() <= self._rect.bottom():
                        self.setCursor(Qt.SizeHorCursor)
                        self._stretchSide = layoutRect.sides[1]
                elif eventPos.y() == self._rect.top():
                    if self._rect.left() <= eventPos.x() <= self._rect.right():
                        self.setCursor(Qt.SizeVerCursor)
                        self._stretchSide = layoutRect.sides[2]
                elif eventPos.y() == self._rect.bottom():
                    if self._rect.left() <= eventPos.x() <= self._rect.right():
                        self.setCursor(Qt.SizeVerCursor)
                        self._stretchSide = layoutRect.sides[3]
        else:
            self.setFlag(QGraphicsItem.ItemIsMovable, False)
            self.setFlag(QGraphicsItem.ItemIsSelectable, False)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        eventPos = event.pos().toPoint()
        if self.stretch:
            self.prepareGeometryChange()
            if self.stretchSide == layoutRect.sides[0]:
                self.setCursor(Qt.SizeHorCursor)
                self.rect.setLeft(eventPos.x())
            elif self.stretchSide == layoutRect.sides[1]:
                self.setCursor(Qt.SizeHorCursor)
                self.rect.setRight(eventPos.x() - int(self._pen.width() / 2))
            elif self.stretchSide == layoutRect.sides[2]:
                self.setCursor(Qt.SizeVerCursor)
                self.rect.setTop(eventPos.y())
            elif self.stretchSide == layoutRect.sides[3]:
                self.setCursor(Qt.SizeVerCursor)
                self.rect.setBottom(eventPos.y() - int(self._pen.width() / 2))
            self.update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        super().mouseReleaseEvent(event)
        if self.stretch:
            self._stretch = False
            self._stretchSide = None
            self.setCursor(Qt.ArrowCursor)
