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

"""Via and via array shapes for layout editor."""

import itertools

from PySide6.QtCore import (
    QPoint,
    QRectF,
    Qt,
)
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import (
    QGraphicsItem,
    QStyle,
)

import revedaEditor.backend.dataDefinitions as ddef
from revedaEditor.common.layoutShapes.base import layoutShape

class layoutVia(layoutShape):
    def __init__(
            self,
            start: QPoint,
            viaDefTuple: ddef.viaDefTuple,
            width: int,
            height: int,
    ):
        super().__init__()
        end = start + QPoint(width, height)
        self._rect = QRectF(start, end).normalized().toRect()
        self._start = self._rect.topLeft()
        self._end = self._rect.bottomRight()
        self._viaDefTuple = viaDefTuple
        self._layer = viaDefTuple.layer
        self._type = viaDefTuple.type
        self._width = width
        self._height = height
        self._definePensBrushes(self._layer)
        self.setZValue(self._layer.z)

    def __repr__(self):
        return f"layoutVia({self._start}, {self._end}, {self._layer})"

    def paint(self, painter, option, widget):
        scale = self.scene().views()[0].transform().m11()
        if self.isSelected():
            painter.setPen(self._selectedPen)
        else:
            painter.setPen(self._pen)
        self._updateTransformedBrush(self._brush, scale)
        painter.setBrush(self._transformedBrush)
        painter.drawRect(self._rect)
        painter.drawLine(self._rect.bottomLeft(), self._rect.topRight())
        painter.drawLine(self._rect.topLeft(), self._rect.bottomRight())

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self._layer.selectable:
            self.setFlag(QGraphicsItem.ItemIsMovable, True)
            self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        else:
            self.setFlag(QGraphicsItem.ItemIsMovable, False)
            self.setFlag(QGraphicsItem.ItemIsSelectable, False)

    def boundingRect(self):
        return self._rect.normalized().adjusted(-2, -2, 2, 2)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

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
        self._rect.moveTo(self.mapFromScene(start))

    @property
    def width(self):
        return self._rect.width()

    @width.setter
    def width(self, value: int):
        self.prepareGeometryChange()
        self._rect.setWidth(value)

    @property
    def height(self):
        return self._rect.height()

    @height.setter
    def height(self, value: int):
        self._rect.setHeight(value)

    @property
    def viaDefTuple(self):
        return self._viaDefTuple

    @property
    def type(self):
        return self._type



class layoutViaArray(layoutShape):
    def __init__(
            self,
            start: QPoint,
            prototype_via,
            xs: float,
            ys: float,
            xnum: int,
            ynum: int,
    ):
        super().__init__()
        self._prototype_via = prototype_via
        self._ynum = ynum  # number of rows
        self._xnum = xnum  # number of columns
        self._xs = xs  # column spacing
        self._ys = ys  # row spacing
        self._start = start  # top-left corner location
        self._via = layoutVia(
            self._start,
            self._prototype_via.viaDefTuple,
            self._prototype_via.width,
            self._prototype_via.height,
        )
        self._via_array = []
        self._create_array()
        self.setFiltersChildEvents(True)
        self.setHandlesChildEvents(True)
        self.setFlag(QGraphicsItem.ItemContainsChildrenInShape, True)
        self._selectedPen = QPen(QColor("yellow"), 4, Qt.DashLine)
        self._selectedPen.setCosmetic(True)

    def __repr__(self):
        return (f"layoutViaArray({self._xnum}, "
                f"{self._ynum}, {self._xs}, "
                f"{self._ys}, {self._start}, {self._via})")

    def _create_array(self):
        # Pre-calculate constants
        x_step = self._xs + self._prototype_via.width
        y_step = self._ys + self._prototype_via.height
        start_x, start_y = self._start.x(), self._start.y()
        via_def = self._prototype_via.viaDefTuple
        via_width = self._prototype_via.width
        via_height = self._prototype_via.height

        # Create flat list using itertools.product
        vias = [
            self._create_via(
                start_x + col * x_step,
                start_y + row * y_step,
                via_def,
                via_width,
                via_height,
            )
            for row, col in itertools.product(range(self._ynum), range(self._xnum))
        ]

        # Reshape into 2D array
        self._via_array = [
            vias[i: i + self._xnum] for i in range(0, len(vias), self._xnum)
        ]

    def _create_via(self, x, y, via_def, width, height):
        via = layoutVia(QPoint(x, y), via_def, width, height)
        via.setFlag(QGraphicsItem.ItemIsSelectable, False)
        via.setFlag(QGraphicsItem.ItemStacksBehindParent, True)
        via.setParentItem(self)
        return via

    def boundingRect(self) -> QRectF:
        return self.childrenBoundingRect()

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addRect(self.childrenBoundingRect())
        return path

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.NonCosmeticBrushPatterns)
        if option.state & QStyle.State_Selected:
            painter.setPen(self._selectedPen)
            painter.drawRect(self.childrenBoundingRect())

    @property
    def via_array(self):
        return self._via_array

    @property
    def ynum(self):
        return self._ynum

    @property
    def xnum(self):
        return self._xnum

    @property
    def start(self) -> QPoint:
        return self._start

    @property
    def xs(self) -> float:
        return self._xs

    @property
    def ys(self):
        return self._ys

    @property
    def via(self):
        return self._via

    @property
    def height(self):
        return self._via.height

    @property
    def width(self):
        return self._via.width


