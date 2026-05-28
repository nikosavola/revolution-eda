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

"""Primitive shapes: rectangle, circle, arc, line, polygon."""

import math

from PySide6.QtCore import (QLine, QLineF, QPoint, QRect, QRectF, Qt)
from PySide6.QtGui import (QBrush, QPainterPath, QPolygonF, QPen, QColor)
from PySide6.QtWidgets import (QGraphicsItem, QGraphicsSceneMouseEvent)

from revedaEditor.backend.pdkLoader import importPDKModule
from revedaEditor.common.shapes.base import symbolShape

schlyr = importPDKModule("schLayers")
symlyr = importPDKModule("symLayers")

class symbolRectangle(symbolShape):
    """
        rect: QRect defined by top left corner and bottom right corner. QRect(Point1,Point2)
    f"""

    sides = ["Left", "Right", "Top", "Bottom"]

    def __init__(self, start: QPoint, end: QPoint) -> None:
        super().__init__()
        self._rect = QRectF(start, end).normalized()
        self._start = self._rect.topLeft()
        self._end = self._rect.bottomRight()
        self._stretchSide = None
        self._pen = symlyr.symbolPen

    def boundingRect(self):
        return self._rect.normalized().adjusted(-2, -2, 2, 2)

    def paint(self, painter, option, widget=None):
        if self.draft:
            painter.setPen(symlyr.draftPen)
            self.setZValue(symlyr.draftLayer.z)
        elif option.state & QStyle.State_Selected:
            painter.setPen(symlyr.selectedSymbolPen)
            self.setZValue(symlyr.symbolLayer.z)
            if self.stretch:
                painter.setPen(symlyr.stretchSymbolPen)
                self.setZValue(symlyr.stretchSymbolLayer.z)
                if self._stretchSide == symbolRectangle.sides[0]:
                    painter.drawLine(self.rect.topLeft(), self.rect.bottomLeft())
                elif self._stretchSide == symbolRectangle.sides[1]:
                    painter.drawLine(self.rect.topRight(),
                                     self.rect.bottomRight())
                elif self._stretchSide == symbolRectangle.sides[2]:
                    painter.drawLine(self.rect.topLeft(), self.rect.topRight())
                elif self._stretchSide == symbolRectangle.sides[3]:
                    painter.drawLine(self.rect.bottomLeft(),
                                     self.rect.bottomRight())
        else:
            painter.setPen(symlyr.symbolPen)
            self.setZValue(symlyr.symbolLayer.z)
        painter.drawRect(self._rect)

    def __repr__(self):
        return f"symbolRectangle({self._start},{self._end})"

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
        return QPoint(int(self._rect.x() + self._rect.width() / 2),
                      int(self._rect.y() + self._rect.height() / 2), )

    @property
    def height(self):
        return self._rect.height()

    @height.setter
    def height(self, height: int):
        self.prepareGeometryChange()
        self._rect.setHeight(height)

    @property
    def width(self):
        return self._rect.width()

    @width.setter
    def width(self, width):
        self.prepareGeometryChange()
        self._rect.setWidth(width)

    @property
    def left(self):
        return self._rect.left()

    @left.setter
    def left(self, left: int):
        self._rect.setLeft(left)

    @property
    def right(self):
        return self._rect.right()

    @right.setter
    def right(self, right: int):
        self.prepareGeometryChange()
        self._rect.setRight(right)

    @property
    def top(self):
        return self._rect.top()

    @top.setter
    def top(self, top: int):
        self.prepareGeometryChange()
        self._rect.setTop(top)

    @property
    def bottom(self):
        return self._rect.bottom()

    @bottom.setter
    def bottom(self, bottom: int):
        self.prepareGeometryChange()
        self._rect.setBottom(bottom)

    @property
    def origin(self):
        return self._rect.bottomLeft()

    @property
    def stretchSide(self):
        return self._stretchSide

    @stretchSide.setter
    def stretchSide(self, value: str):
        self.prepareGeometryChange()
        self._stretchSide = value

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mousePressEvent(event)
        eventPos = event.pos().toPoint()
        if self._stretch:
            self.setFlag(QGraphicsItem.ItemIsMovable, False)
            if (
                    eventPos.x() == self._rect.left() and self._rect.top() <= eventPos.y() <= self._rect.bottom()):
                self.setCursor(Qt.SizeHorCursor)
                self._stretchSide = symbolRectangle.sides[0]
            elif (
                    eventPos.x() == self._rect.right() and self._rect.top() <= eventPos.y() <= self._rect.bottom()):
                self.setCursor(Qt.SizeHorCursor)
                self._stretchSide = symbolRectangle.sides[1]
            elif (
                    eventPos.y() == self._rect.top() and self._rect.left() <= eventPos.x() <= self._rect.right()):
                self.setCursor(Qt.SizeVerCursor)
                self._stretchSide = symbolRectangle.sides[2]
            elif (
                    eventPos.y() == self._rect.bottom() and self._rect.left() <= eventPos.x() <= self._rect.right()):
                self.setCursor(Qt.SizeVerCursor)
                self._stretchSide = symbolRectangle.sides[3]

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        eventPos = event.pos().toPoint()
        if self.stretch:
            self.prepareGeometryChange()
            if self.stretchSide == symbolRectangle.sides[0]:
                self.setCursor(Qt.SizeHorCursor)
                self.rect.setLeft(eventPos.x())
            elif self.stretchSide == symbolRectangle.sides[1]:
                self.setCursor(Qt.SizeHorCursor)
                self.rect.setRight(eventPos.x())
            elif self.stretchSide == symbolRectangle.sides[2]:
                self.setCursor(Qt.SizeVerCursor)
                self.rect.setTop(eventPos.y())
            elif self.stretchSide == symbolRectangle.sides[3]:
                self.setCursor(Qt.SizeVerCursor)
                self.rect.setBottom(eventPos.y())
            self.update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        if self.stretch:
            self._stretch = False
            self._stretchSide = None
            self.setCursor(Qt.ArrowCursor)


class symbolCircle(symbolShape):

    def __init__(self, centre: QPoint, end: QPoint):
        super().__init__()
        xlen = abs(end.x() - centre.x())
        ylen = abs(end.y() - centre.y())
        distance = math.sqrt(xlen ** 2 + ylen ** 2)
        
        self.calculateRadius(distance)

        self._centre = centre
        self._topLeft = self._centre - QPoint(self._radius, self._radius)
        self._rightBottom = self._centre + QPoint(self._radius, self._radius)
        self._end = self._centre + QPoint(self._radius, 0)  # along x-axis
        self._stretch = False
        self._startStretch = False

    def paint(self, painter, option, widget) -> None:
        if self.isSelected():
            painter.setPen(symlyr.selectedSymbolPen)
            self.setZValue(symlyr.selectedSymbolLayer.z)
            painter.drawEllipse(self._centre, 1, 1)
            if self._stretch:
                painter.setPen(symlyr.stretchSymbolPen)
                self.setZValue(symlyr.stretchSymbolLayer.z)
        else:
            painter.setPen(symlyr.symbolPen)
            self.setZValue(symlyr.symbolLayer.z)
        painter.drawEllipse(self._centre, self._radius, self._radius)

    def __repr__(self):
        return f"symbolCircle({self._centre},{self._end})"

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, radius: int):
        self.prepareGeometryChange()
        distance = float(radius)
        
        self.calculateRadius(distance)
        self._end = self._centre + QPoint(self._radius, 0)
        self._topLeft = self._centre - QPoint(self._radius, self._radius)
        self._rightBottom = self._centre + QPoint(self._radius, self._radius)

    @property
    def centre(self):
        return self._centre

    @centre.setter
    def centre(self, value: QPoint):
        self.prepareGeometryChange()
        if isinstance(value, QPoint):
            self._centre = value

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value: QPoint):
        if isinstance(value, QPoint):
            self.prepareGeometryChange()
            self._end = value

    @property
    def rightBottom(self):
        return self._rightBottom

    @rightBottom.setter
    def rightBottom(self, value: QPoint):
        if isinstance(value, QPoint):
            self._rightBottom = value

    @property
    def topLeft(self):
        return self._topLeft

    @topLeft.setter
    def topLeft(self, value: QPoint):
        if isinstance(value, QPoint):
            self._topLeft = value

    def boundingRect(self):
        return (
            QRectF(self._topLeft, self._rightBottom).normalized().adjusted(-2, -2,
                                                                           2, 2))

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mousePressEvent(event)
        if self.isSelected() and self._stretch:
            self.setFlag(QGraphicsItem.ItemIsMovable, False)
            eventPos = event.pos().toPoint()
            distance = math.sqrt((eventPos.x() - self._centre.x()) ** 2 + (
                    eventPos.y() - self._centre.y()) ** 2)
            if distance == self._radius:
                self._startStretch = True
                self.setCursor(Qt.DragMoveCursor)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseMoveEvent(event)
        if self._startStretch:
            eventPos = event.pos().toPoint()
            distance = math.sqrt((eventPos.x() - self._centre.x()) ** 2 + (
                    eventPos.y() - self._centre.y()) ** 2)
            self.prepareGeometryChange()
            
            # Snap to grid
            if self.scene() and hasattr(self.scene(), 'snapTuple'):
                grid = self.scene().snapTuple[0]
                distance = round(distance / grid) * grid
            
            self._radius = int(distance)
            self._topLeft = self._centre - QPoint(self._radius, self._radius)
            self._rightBottom = self._centre + QPoint(self._radius, self._radius)
            self._end = self._centre + QPoint(self._radius, 0)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        if self._startStretch:
            self._startStretch = False
            # self._topLeft = self._centre - QPoint(self._radius, self._radius)
            # self._rightBottom = self._centre + QPoint(self._radius, self._radius)
            # self._end = self._centre + QPoint(self._radius, 0)
            self.setCursor(Qt.ArrowCursor)

    def calculateRadius(self, distance):
        # Snap to grid if scene is available
        if self.scene() and hasattr(self.scene(), 'snapTuple'):
            grid = self.scene().snapTuple[0]
            distance = round(distance / grid) * grid
        
        self._radius = int(distance)


class symbolArc(symbolShape):
    """
    Class to draw arc shapes. Can have four directions.
    """

    arcTypes = ["Up", "Right", "Down", "Left"]
    sides = ["Left", "Right", "Top", "Bottom"]

    def __init__(self, start: QPoint, end: QPoint):
        super().__init__()
        self._start = start
        self._end = end
        self._rect = QRectF(self._start, self._end).normalized()
        self._arcLine = QLineF(self._start, self._end)
        self._arcAngle = 0
        self._width = self._rect.width()
        self._height = self._rect.height()
        self._pen = symlyr.symbolPen
        self._adjustment = int(self._pen.width() / 2)
        self._stretchSide = None
        self._findAngle()
        self._brect = QRectF(0, 0, 0, 0)

    def _findAngle(self):
        self._arcAngle = self._arcLine.angle()
        if 90 >= self._arcAngle >= 0:
            self._arcType = symbolArc.arcTypes[0]
        elif 180 >= self._arcAngle > 90:
            self._arcType = symbolArc.arcTypes[1]
        elif 270 >= self._arcAngle > 180:
            self._arcType = symbolArc.arcTypes[2]
        elif 360 > self._arcAngle > 270:
            self._arcType = symbolArc.arcTypes[3]

    @property
    def arcType(self):
        return self._arcType

    @arcType.setter
    def arcType(self, type: str):
        self.prepareGeometryChange()
        self._arcType = type

    def paint(self, painter, option, widget=None) -> None:
        if self.isSelected():
            painter.setPen(symlyr.selectedSymbolPen)
            painter.drawRect(self.bRect)
            self.setZValue(symlyr.selectedSymbolLayer.z)
            if self._stretch:
                painter.setPen(symlyr.stretchSymbolPen)
                self.setZValue(symlyr.stretchSymbolLayer.z)
                if self._stretchSide == symbolArc.sides[0]:
                    painter.drawLine(self._rect.topLeft(),
                                     self._rect.bottomLeft())
                elif self._stretchSide == symbolArc.sides[1]:
                    painter.drawLine(self._rect.topRight(),
                                     self._rect.bottomRight())
                elif self._stretchSide == symbolArc.sides[2]:
                    painter.drawLine(self._rect.topLeft(), self._rect.topRight())
                elif self._stretchSide == symbolArc.sides[3]:
                    painter.drawLine(self._rect.bottomLeft(),
                                     self._rect.bottomRight())
        else:
            painter.setPen(symlyr.symbolPen)
            self.setZValue(symlyr.symbolLayer.z)

        self.arcDraw(painter)

    def arcDraw(self, painter):
        # Define the mapping of arc types to starting angles
        ARC_ANGLES = {symbolArc.arcTypes[0]: 0, symbolArc.arcTypes[1]: 90,
                      symbolArc.arcTypes[2]: 180, symbolArc.arcTypes[3]: 270, }

        # Get the starting angle and draw the arc
        startAngle = ARC_ANGLES.get(self._arcType, 0) * 16
        painter.drawArc(self._rect, startAngle, 180 * 16)

    def boundingRect(self):
        return self.bRect

    @property
    def bRect(self):
        brect = QRectF(0, 0, 0, 0)
        if self._arcType == symbolArc.arcTypes[0]:
            brect = QRectF(self._rect.left(), self._rect.top(),
                           self._rect.width(),
                           0.5 * self._rect.height()).adjusted(-2, -2, 2, 2)
        elif self._arcType == symbolArc.arcTypes[1]:
            brect = QRectF(self._rect.left(), self._rect.top(),
                           0.5 * self._rect.width(),
                           self._rect.height()).adjusted(-2, -2, 2, 2)
        elif self._arcType == symbolArc.arcTypes[2]:
            brect = QRectF(self._rect.left(),
                           self._rect.top() + self._rect.height() * 0.5,
                           self._rect.width(),
                           0.5 * self._rect.height()).adjusted(-2, -2, 2, 2)
        elif self._arcType == symbolArc.arcTypes[3]:
            brect = QRectF(self._rect.left() + 0.5 * self._rect.width(),
                           self._rect.top(), 0.5 * self._rect.width(),
                           self._rect.height()).adjusted(-2, -2, 2, 2)
        return brect

    @property
    def adjustment(self):
        return self._adjustment

    @property
    def rect(self):
        return self._rect

    @rect.setter
    def rect(self, arcRect: QRectF):
        self._rect = arcRect.normalized()

    def __repr__(self) -> str:
        return f"symbolArc({self._start},{self._end})"

    @property
    def start(self) -> QPoint:
        return self._start

    @start.setter
    def start(self, point: QPoint):
        assert isinstance(point, QPoint)
        self.prepareGeometryChange()
        self._start = point

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, point: QPoint):
        self.prepareGeometryChange()
        self._end = point
        self._arcLine = QLineF(self._start, self._end)
        self._arcAngle = self._arcLine.angle()
        self._findAngle()
        self._rect = QRectF(self._start, self._end).normalized()

    @property
    def width(self) -> int:
        return int(self.rect.width())

    @width.setter
    def width(self, width):
        self._width = width
        self.prepareGeometryChange()
        self.rect.setWidth(self._width)

    @property
    def height(self) -> int:
        return int(self.rect.height())

    @height.setter
    def height(self, height: int):
        self._height = height
        self.prepareGeometryChange()
        self.rect.setHeight(self._height)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mousePressEvent(event)
        eventPos = event.pos().toPoint()
        if self._stretch:
            self.setFlag(QGraphicsItem.ItemIsMovable, False)
            _T = 5  # hit tolerance in pixels
            if (abs(eventPos.x() - self._rect.left()) <= _T and
                    self._rect.top() - _T <= eventPos.y() <= self._rect.bottom() + _T):
                self.setCursor(Qt.CursorShape.SizeHorCursor)
                self._stretchSide = symbolArc.sides[0]
            elif (abs(eventPos.x() - self._rect.right()) <= _T and
                    self._rect.top() - _T <= eventPos.y() <= self._rect.bottom() + _T):
                self.setCursor(Qt.CursorShape.SizeHorCursor)
                self._stretchSide = symbolArc.sides[1]
            elif (abs(eventPos.y() - self._rect.top()) <= _T and
                    self._rect.left() - _T <= eventPos.x() <= self._rect.right() + _T):
                self.setCursor(Qt.CursorShape.SizeVerCursor)
                self._stretchSide = symbolArc.sides[2]
            elif (abs(eventPos.y() - self._rect.bottom()) <= _T and
                    self._rect.left() - _T <= eventPos.x() <= self._rect.right() + _T):
                self.setCursor(Qt.CursorShape.SizeVerCursor)
                self._stretchSide = symbolArc.sides[3]

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseMoveEvent(event)
        eventPos = event.pos().toPoint()
        if self._stretch and self._stretchSide is not None:
            self.prepareGeometryChange()
            rect = QRectF(self._rect)
            if self._stretchSide == symbolArc.sides[0]:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
                rect.setLeft(eventPos.x())
            elif self._stretchSide == symbolArc.sides[1]:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
                rect.setRight(eventPos.x())
            elif self._stretchSide == symbolArc.sides[2]:
                self.setCursor(Qt.CursorShape.SizeVerCursor)
                rect.setTop(eventPos.y())
            elif self._stretchSide == symbolArc.sides[3]:
                self.setCursor(Qt.CursorShape.SizeVerCursor)
                rect.setBottom(eventPos.y())

            # Detect whether normalization will flip the rect (dragged edge crossed
            # the opposite edge). Both the arc type and the active stretch side must
            # be updated to reflect the new orientation so that dragging continues
            # smoothly and the arc renders correctly after the flip.
            if rect.width() < 0:
                # Horizontal flip: swap "Right" ↔ "Left" arc type and "Left" ↔ "Right" side
                _hArcFlip = {symbolArc.arcTypes[1]: symbolArc.arcTypes[3],
                             symbolArc.arcTypes[3]: symbolArc.arcTypes[1]}
                self._arcType = _hArcFlip.get(self._arcType, self._arcType)
                _hSideFlip = {symbolArc.sides[0]: symbolArc.sides[1],
                              symbolArc.sides[1]: symbolArc.sides[0]}
                self._stretchSide = _hSideFlip.get(self._stretchSide, self._stretchSide)

            if rect.height() < 0:
                # Vertical flip: swap "Up" ↔ "Down" arc type and "Top" ↔ "Bottom" side
                _vArcFlip = {symbolArc.arcTypes[0]: symbolArc.arcTypes[2],
                             symbolArc.arcTypes[2]: symbolArc.arcTypes[0]}
                self._arcType = _vArcFlip.get(self._arcType, self._arcType)
                _vSideFlip = {symbolArc.sides[2]: symbolArc.sides[3],
                              symbolArc.sides[3]: symbolArc.sides[2]}
                self._stretchSide = _vSideFlip.get(self._stretchSide, self._stretchSide)

            self._rect = rect.normalized()

            # Rebuild _start/_end from the normalized rect corners that correspond
            # to the (possibly flipped) arc type.
            if self._arcType == symbolArc.arcTypes[0]:      # "Up"
                self._start = self._rect.bottomLeft().toPoint()
                self._end = self._rect.topRight().toPoint()
            elif self._arcType == symbolArc.arcTypes[1]:    # "Right"
                self._start = self._rect.bottomRight().toPoint()
                self._end = self._rect.topLeft().toPoint()
            elif self._arcType == symbolArc.arcTypes[2]:    # "Down"
                self._start = self._rect.topRight().toPoint()
                self._end = self._rect.bottomLeft().toPoint()
            else:                                            # "Left"
                self._start = self._rect.topLeft().toPoint()
                self._end = self._rect.bottomRight().toPoint()
            self._arcLine = QLineF(self._start, self._end)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        if self.stretch:
            self._stretch = False
            self._stretchSide = None
            self.setCursor(Qt.CursorShape.ArrowCursor)


class symbolLine(symbolShape):
    stretchSides = ("start", "end")
    _BOUNDING_OFFSET = 10
    _SHAPE_OFFSET = 2
    _ELLIPSE_SIZE = 2

    def __init__(self, start: QPoint, end: QPoint):
        super().__init__()
        self._end = end
        self._start = start
        self._stretch = False
        self._stretchSide = None
        self._pen = symlyr.symbolPen
        self._updateGeometry()
        self._horizontal = True

    def __repr__(self):
        return f"symbolLine({self._start}, {self._end})"

    def _updateGeometry(self):
        self._line = QLine(self._start, self._end)
        self._rect = QRect(self._start, self._end).normalized()

    def boundingRect(self):
        return self._rect.adjusted(-self._BOUNDING_OFFSET, -self._BOUNDING_OFFSET,
                                   self._BOUNDING_OFFSET, self._BOUNDING_OFFSET, )

    def shape(self):
        path = QPainterPath()
        path.addRect(self._rect.adjusted(-self._SHAPE_OFFSET, -self._SHAPE_OFFSET,
                                         self._SHAPE_OFFSET,
                                         self._SHAPE_OFFSET, ))
        return path

    def paint(self, painter, option, widget):
        is_selected = self.isSelected()
        if is_selected:
            painter.setPen(symlyr.selectedSymbolPen)
            self.setZValue(symlyr.symbolLayer.z)

            if self._stretch:
                painter.setPen(symlyr.stretchSymbolPen)
                self.setZValue(symlyr.stretchSymbolLayer.z)
                # Draw stretch handles
                painter.drawEllipse(self._start, self._ELLIPSE_SIZE,
                                    self._ELLIPSE_SIZE)
                painter.drawEllipse(self._end, self._ELLIPSE_SIZE,
                                    self._ELLIPSE_SIZE)
        else:
            painter.setPen(symlyr.symbolPen)
            self.setZValue(symlyr.symbolLayer.z)

        painter.drawLine(self._line)

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start: QPoint):
        if start != self._start:  # Only update if changed
            self.prepareGeometryChange()
            self._start = start
            self._updateGeometry()

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, end: QPoint):
        if end != self._end:  # Only update if changed
            self.prepareGeometryChange()
            self._end = end
            self._updateGeometry()

    @property
    def length(self):
        dx = self.start.x() - self._end.x()
        dy = self.start.y() - self._end.y()
        return math.hypot(dx, dy)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mousePressEvent(event)
        if self.isSelected() and self._stretch:
            self.setFlag(QGraphicsItem.ItemIsMovable, False)
            eventPos = event.pos().toPoint()
            # Check if click is near start or end point
            if (eventPos - self._start).manhattanLength() <= self._ELLIPSE_SIZE:
                self._stretchSide = "start"
            elif (eventPos - self._end).manhattanLength() <= self._ELLIPSE_SIZE:
                self._stretchSide = "end"
            else:
                self._stretchSide = None

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self._stretchSide:
            self.prepareGeometryChange()
            eventPos = event.pos().toPoint()

            if self._stretchSide == "start":
                self._start = eventPos
            else:
                self._end = eventPos

            self._updateGeometry()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self._stretchSide = None
        super().mouseReleaseEvent(event)


class symbolPolygon(symbolShape):
    _NO_SELECTION = 999  # Constant for no selection
    _DEFAULT_CORNER = QPoint(99999, 99999)  # Constant for default corner
    _CORNER_SIZE = 5  # Size of corner markers

    def __init__(self, points: list):
        super().__init__()
        self._points = points
        self._polygon = QPolygonF(self._points)
        self._selectedCorner = QPoint(0, 0)
        self._selectedCornerIndex = self._NO_SELECTION
        self.setZValue(symlyr.symbolLayer.z)

    def __repr__(self):
        return f"symbolPolygon({self._points})"

    def paint(self, painter, option, widget):
        is_selected = self.isSelected()
        if is_selected:
            painter.setPen(symlyr.selectedSymbolPen)
            self.setZValue(symlyr.selectedSymbolLayer.z)
            if self._stretch:
                painter.setPen(symlyr.stretchSymbolPen)
                self.setZValue(symlyr.stretchSymbolLayer.z)
        else:
            painter.setPen(symlyr.symbolPen)
            self.setZValue(symlyr.symbolLayer.z)
        # Draw the main polygon first
        painter.drawPolygon(self._polygon)

        # Draw corner marker only if necessary
        if all((is_selected, self._stretch,
                self._selectedCorner != self._DEFAULT_CORNER)):
            painter.drawEllipse(self._selectedCorner, self._CORNER_SIZE,
                                self._CORNER_SIZE)

    def boundingRect(self) -> QRectF:
        return self._polygon.boundingRect()

    @property
    def polygon(self):
        return self._polygon

    @property
    def points(self) -> list:
        return self._points

    @points.setter
    def points(self, value: list):
        if value != self._points:  # Only update if points actually changed
            self.prepareGeometryChange()
            self._points = value
            self._updatePolygon()

    def _updatePolygon(self):
        self._polygon = QPolygonF(self._points)

    def addPoint(self, point: QPoint):
        self.prepareGeometryChange()
        self._points.append(point)
        self._updatePolygon()

    @property
    def tempLastPoint(self):
        return self._points[-1]

    @tempLastPoint.setter
    def tempLastPoint(self, value: QPoint):
        self.prepareGeometryChange()
        self._polygon = QPolygonF([*self._points, value])

    def _findNearestPoint(self, eventPos: QPoint) -> tuple[int, QPoint | None]:
        """Find the nearest point to the event position"""
        snapDistance = 10  # default
        if self.scene() and hasattr(self.scene(), 'snapTuple'):
            snapDistance = self.scene().snapTuple[0]
        for i, point in enumerate(self._points):
            if (eventPos - point).manhattanLength() <= snapDistance:
                return i, point
        return self._NO_SELECTION, None

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mousePressEvent(event)
        if self._stretch:
            self.setFlag(QGraphicsItem.ItemIsMovable, False)
            eventPos = event.pos().toPoint()
            index, point = self._findNearestPoint(eventPos)
            if point is not None:
                self._selectedCorner = point
                self._selectedCornerIndex = index

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self._stretch and self._selectedCornerIndex != self._NO_SELECTION:
            eventPos = event.pos().toPoint()
            self._points[self._selectedCornerIndex] = eventPos
            self.prepareGeometryChange()
            self._updatePolygon()
            self._selectedCorner = eventPos
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseReleaseEvent(event)

        if self.stretch:
            self._resetStretchState()
            self._stretch = False

    def _resetStretchState(self):
        """Reset the stretch state of the polygon"""
        self._stretch = False
        self._stretchSide = None
        self.setCursor(Qt.ArrowCursor)
        self._selectedCorner = self._DEFAULT_CORNER
        self._selectedCornerIndex = self._NO_SELECTION


