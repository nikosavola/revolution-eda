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

"""Line, path, ruler, and alignment line shapes for layout editor."""

import math

from PySide6.QtCore import (
    QLineF,
    QPoint,
    QPointF,
    QRect,
    QRectF,
    Qt,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QPen,
)
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsSceneMouseEvent,
)

import revedaEditor.backend.dataDefinitions as ddef
from revedaEditor.common.layoutShapes.base import layoutShape

class layoutLine(layoutShape):
    def __init__(
            self,
            draftLine: QLineF,
            width: float = 1,
            mode: int = 0,
    ):
        """
        Initialize the TickLine object.

        Args:
            draftLine (QLineF): The draft line.
            width (float): The width of the line.
            mode (int, optional): The mode. Defaults to 0.
        """
        super().__init__()

        self._draftLine = draftLine
        self._width: int = width
        self._mode = mode
        self._angle = 0
        self._rect = QRect(0, 0, 0, 0)
        penColour = QColor(255, 40, 40)
        self._pen = QPen(penColour, self._width, Qt.SolidLine)
        self._pen.setCosmetic(True)
        self._selectedPen = QPen(Qt.red, self._width + 1, Qt.SolidLine)
        self._selectedPen.setCosmetic(False)
        self._determineAngle(self._draftLine.angle())
        self.setZValue(999)

    def __repr__(self):
        return f"layoutLine({self._draftLine}, {self._width}, {self._mode})"

    def _determineAngle(self, angle: float):
        match self._mode:
            case 0:  # manhattan
                self._createManhattanLine(angle)
            case 1:  # diagonal
                self._createDiagonalLine(angle)
            case 2:
                self._createAnyAngleLine(angle)
        self._draftLine.setAngle(0)
        self.setTransformOriginPoint(self.draftLine.p1())
        self.setRotation(-self._angle)

    def _createManhattanLine(self, angle):
        if 0 <= angle <= 45 or 360 > angle > 315:
            self._angle = 0
        elif 45 < angle <= 135:
            self._angle = 90
        elif 135 < angle <= 225:
            self._angle = 180
        elif 225 < angle <= 315:
            self._angle = 270

    def _createDiagonalLine(self, angle):
        if 0 <= angle <= 22.5 or 360 > angle > 337.5:
            self._angle = 0
        elif 22.5 < angle <= 67.5:
            self._angle = 45
        elif 67.5 < angle <= 112.5:
            self._angle = 90
        elif 112.5 < angle <= 157.5:
            self._angle = 135
        elif 157.5 < angle <= 202.5:
            self._angle = 180
        elif 202.5 < angle <= 247.5:
            self._angle = 225
        elif 247.5 < angle <= 292.5:
            self._angle = 270
        elif 292.5 < angle <= 337.5:
            self._angle = 315

    def _createAnyAngleLine(self, angle):
        self._angle = angle

    def boundingRect(self) -> QRectF:
        half_w = self._width // 2 + 2
        return (
            QRectF(self._draftLine.p1(), self._draftLine.p2())
            .normalized()
            .adjusted(-half_w, -half_w, half_w, half_w)
        )

    def paint(self, painter, option, widget=None):
        if self.isSelected():
            painter.setPen(self._selectedPen)
            painter.drawRect(self.boundingRect())
        else:
            painter.setPen(self._pen)
        painter.drawLine(self._draftLine)

    @property
    def draftLine(self):
        return self._draftLine

    @draftLine.setter
    def draftLine(self, line: QLineF):
        self.prepareGeometryChange()
        self._draftLine = line
        angle = self._draftLine.angle()
        self._determineAngle(angle)

    @property
    def angle(self) -> float:
        return self._angle

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width: float):
        self._width = width

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value: int):
        self._mode = value

    @property
    def sceneEndPoints(self):
        return [
            self.mapToScene(self._draftLine.p1()).toPoint(),
            self.mapToScene(self._draftLine.p2()).toPoint(),
        ]


# "layer", "name", "mode", "width", "startExtend", "endExtend"


class layoutPath(layoutShape):
    def __init__(
            self,
            draftLine: QLineF,
            layer: ddef.layLayer,
            width: float = 1.0,
            startExtend: int = 0,
            endExtend: int = 0,
            mode: int = 0,
    ):
        """
        Initialize the class instance.

        Args:
            draftLine (QLineF): The draft line.
            layer (ddef.layLayer): The layer.
            width (float, optional): The width. Defaults to 1.0.
            startExtend (int, optional): The start extend. Defaults to 0.
            endExtend (int, optional): The end extend. Defaults to 0.
            mode (int, optional): The mode. Defaults to 0.
        """
        super().__init__()
        self.start = None
        self._draftLine = draftLine
        self._startExtend = startExtend
        self._endExtend = endExtend
        self._width = width
        self._layer = layer
        self._mode = mode
        self._name = ""
        self._stretch = False
        self._stretchSide = None
        self._definePensBrushes(self._layer)
        self._rect = QRectF(0, 0, 0, 0)
        self._angle = 0
        self._rectCorners(self._draftLine.angle())
        self.setZValue(self._layer.z)

    def __repr__(self):
        return (
            f"layoutPath({self._draftLine}, {self._layer}"
            f"{self._width}, {self._startExtend}, {self._endExtend}, {self._mode})"
        )

    def _rectCorners(self, angle: float):
        match self._mode:
            case 0:  # manhattan
                self._createManhattanPath(angle)
            case 1:  # diagonal
                self._createDiagonalPath(angle)
            case 2:
                self._createAnyAnglePath(angle)
            case 3:
                self._createHorizontalPath(angle)
            case 4:
                self._createVerticalPath(angle)
        self._draftLine.setAngle(0)
        self._rect = self._extractRect()
        self.setTransformOriginPoint(self.draftLine.p1())
        self.setRotation(-self._angle)

    def _createManhattanPath(self, angle: float) -> None:
        """
        Creates a Manhattan path based on the given angle.

        :param angle: The angle in degrees.
        :type angle: float

        :return: None
        """
        self._angle = 90 * math.floor(((angle + 45) % 360) / 90)

    def _createDiagonalPath(self, angle: float) -> None:
        """
        Creates a manhattan or diagonal path based on the given angle.
        Parameters:
            angle (float): The angle in degrees.
        Returns:
            None
        """
        self._angle = 45 * math.floor(((angle + 22.5) % 360) / 45)

    def _createAnyAnglePath(self, angle: float) -> None:
        self._angle = angle

    def _createHorizontalPath(self, angle: float) -> None:
        self._angle = 180 * math.floor(((angle + 90) % 360) / 180)

    def _createVerticalPath(self, angle: float) -> None:
        angle = angle % 360
        if 0 <= angle < 180:
            self._angle = 90
        else:
            self._angle = 270

    def _extractRect(self):
        direction = self._draftLine.p2() - self._draftLine.p1()
        if direction == QPoint(0, 0):  # when the mouse pressed first time
            rect = (
                QRectF(self._draftLine.p1(), self._draftLine.p2())
                .adjusted(-2, -2, 2, 2)
                .normalized()
            )
        else:
            direction /= direction.manhattanLength()
            perpendicular = QPointF(-direction.y(), direction.x())
            point1 = (
                    self._draftLine.p1()
                    + perpendicular * self._width * 0.5
                    - direction * self._startExtend
            ).toPoint()
            point2 = (
                    self._draftLine.p2()
                    - perpendicular * self._width * 0.5
                    + direction * self._endExtend
            ).toPoint()
            rect = QRectF(point1, point2).normalized()
        return rect

    def paint(self, painter, option, widget):
        # Get scale once and cache it
        scale = self.scene().views()[0].transform().m11()
        if self.isSelected():
            if self._stretch:
                painter.setPen(self._stretchPen)
                self._updateTransformedBrush(self._stretchBrush, scale)
            else:
                painter.setPen(self._selectedPen)
                self._updateTransformedBrush(self._selectedBrush, scale)
        else:
            painter.setPen(self._pen)
            self._updateTransformedBrush(self._brush, scale)
        painter.setBrush(self._transformedBrush)
        painter.drawLine(self._draftLine)
        painter.drawRect(self._rect)

    def boundingRect(self) -> QRectF:
        return self._rect.adjusted(-2, -2, 2, 2)

    @property
    def draftLine(self):
        return self._draftLine

    @draftLine.setter
    def draftLine(self, line: QLineF):
        self.prepareGeometryChange()
        self._draftLine = line
        angle = self._draftLine.angle()
        self._rectCorners(angle)

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width: float):
        self._width = width
        self.prepareGeometryChange()
        self._rectCorners(self._angle)

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value: int):
        self.prepareGeometryChange()
        self._mode = value
        self._rectCorners(self._angle)

    @property
    def stretchSide(self):
        return self._stretchSide

    @stretchSide.setter
    def stretchSide(self, value: str):
        self.prepareGeometryChange()
        self._stretchSide = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def startExtend(self) -> int:
        return self._startExtend

    @startExtend.setter
    def startExtend(self, value: str):
        self.prepareGeometryChange()
        self._startExtend = value
        self._rect = self._extractRect()

    @property
    def endExtend(self) -> int:
        return self._endExtend

    @endExtend.setter
    def endExtend(self, value: str):
        self.prepareGeometryChange()
        self._endExtend = value
        self._rect = self._extractRect()

    @property
    def angle(self) -> float:
        return self._angle

    @angle.setter
    def angle(self, value: float):
        self._angle = value
        self.prepareGeometryChange()
        self._rect = self._extractRect()
        self.setTransformOriginPoint(self.draftLine.p1())
        self.setRotation(-self._angle)

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, layer: ddef.layLayer):
        self.prepareGeometryChange()
        self._layer = layer

    @property
    def sceneEndPoints(self):
        return [
            self.mapToScene(self._draftLine.p1()).toPoint(),
            self.mapToScene(self._draftLine.p2()).toPoint(),
        ]

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mousePressEvent(event)
        if self._layer.selectable:
            eventPos = event.pos().toPoint()
            if self._stretch:
                if (
                        eventPos - self._draftLine.p1().toPoint()
                ).manhattanLength() <= self.scene().snapDistance:
                    self._stretchSide = "p1"
                    self.setCursor(Qt.SizeHorCursor)
                elif (
                        eventPos - self._draftLine.p2().toPoint()
                ).manhattanLength() <= self.scene().snapDistance:
                    self._stretchSide = "p2"
                    self.setCursor(Qt.SizeHorCursor)
                self.scene().stretchPath(self, self._stretchSide)


class layoutRuler(layoutShape):
    def __init__(
            self,
            draftLine: QLineF,
            width: float,
            tickGap: float,
            tickLength: int,
            tickFont: QFont,
            mode: int = 0,
    ):
        """
        Initialize the TickLine object.

        Args:
            draftLine (QLineF): The draft line.
            width (float): The width of the line.
            tickGap (float): The gap between ticks.
            tickLength (int): The length of the ticks.
            tickFont (QFont): The font for tick labels.
            mode (int, optional): The mode. Defaults to 0.
        """
        super().__init__()

        self._draftLine = draftLine
        self._width = width
        self._tickGap = tickGap
        self._tickLength = tickLength
        self._mode = mode
        self._angle = 0
        self._rect = QRect(0, 0, 0, 0)
        penColour = QColor(255, 255, 40)
        self._pen = QPen(penColour, self._width, Qt.SolidLine)
        self._pen.setCosmetic(True)
        self._selectedPen = QPen(Qt.red, self._width + 1, Qt.SolidLine)
        self._selectedPen.setCosmetic(True)
        # self._pen.setCosmetic(True)
        self._tickTuples = list()
        self._tickFont = tickFont
        self._determineAngle(self._draftLine.angle())
        self._fm = QFontMetrics(self._tickFont)
        self._fontHeight = self._fm.boundingRect("0").height()
        self._fontWidth = self._fm.boundingRect("0.000").width()
        # Enable child event filtering for filters and handles
        self.setFiltersChildEvents(True)
        self.setHandlesChildEvents(True)
        # Enable flag to indicate that the item contains children in shape
        self.setFlag(QGraphicsItem.ItemContainsChildrenInShape, True)
        self._createRulerTicks()
        # self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        # self.update(self.boundingRect())
        self.setZValue(999)

    def __repr__(self):
        return (
            f"layoutRuler({self._draftLine}, {self._width}, {self._tickGap}, "
            f"{self._tickLength}, {self._tickFont}, {self._mode})"
        )

    def _determineAngle(self, angle: float):
        match self._mode:
            case 0:  # manhattan
                self._createManhattanRuler(angle)
            case 1:  # diagonal
                self._createDiagonalRuler(angle)
            case 2:
                self._createAnyAngleRuler(angle)
        self._draftLine.setAngle(0)
        self.setTransformOriginPoint(self.draftLine.p1())
        self.setRotation(-self._angle)

    def _createManhattanRuler(self, angle):
        if 0 <= angle <= 45 or 360 > angle > 315:
            self._angle = 0
        elif 45 < angle <= 135:
            self._angle = 90
        elif 135 < angle <= 225:
            self._angle = 180
        elif 225 < angle <= 315:
            self._angle = 270

    def _createDiagonalRuler(self, angle):
        if 0 <= angle <= 22.5 or 360 > angle > 337.5:
            self._angle = 0
        elif 22.5 < angle <= 67.5:
            self._angle = 45
        elif 67.5 < angle <= 112.5:
            self._angle = 90
        elif 112.5 < angle <= 157.5:
            self._angle = 135
        elif 157.5 < angle <= 202.5:
            self._angle = 180
        elif 202.5 < angle <= 247.5:
            self._angle = 225
        elif 247.5 < angle <= 292.5:
            self._angle = 270
        elif 292.5 < angle <= 337.5:
            self._angle = 315

    def _createAnyAngleRuler(self, angle):
        self._angle = angle

    def _createRulerTicks(self):
        self._tickTuples = []
        direction = self._draftLine.p2() - self._draftLine.p1()

        if direction != QPointF(0, 0):
            length = direction.manhattanLength()
            direction = QPointF(direction.x() / length, direction.y() / length)
            perpendicular = QPointF(-direction.y(), direction.x())

            if self._draftLine.length() >= self._tickGap:
                # Pre-calculate common values
                p1 = self._draftLine.p1()
                perp_tick = perpendicular * self._tickLength
                numberOfTicks = math.ceil(self._draftLine.length() / self._tickGap)

                # Generate ticks in single loop
                for i in range(numberOfTicks):
                    tick_pos = p1 + direction * (i * self._tickGap)
                    tick_line = QLineF(tick_pos, tick_pos + perp_tick)
                    self._tickTuples.append(
                        ddef.rulerTuple(
                            tick_pos + perp_tick,
                            (tick_line.p1(), tick_line.p2()),
                            str(float(i)),
                        )
                    )

            # Final tick
            p2 = self._draftLine.p2()
            final_line = QLineF(p2, p2 + perpendicular * self._tickLength)
            self._tickTuples.append(
                ddef.rulerTuple(
                    p2 + direction * 2,
                    (final_line.p1(), final_line.p2()),
                    str(round(self._draftLine.length() / self._tickGap, 3)),
                )
            )

        self._rect = QRectF(
            self._draftLine.p1().toPoint(), self._draftLine.p2().toPoint()
        ).normalized()

    def boundingRect(self) -> QRectF:
        margin = max(self._fontWidth, self._fontHeight, self._tickLength)
        return (
            QRectF(self._rect).normalized().adjusted(-margin, -margin, margin, margin)
        )

    def paint(self, painter, option, widget=None):
        if self.isSelected():
            painter.setPen(self._selectedPen)
            painter.drawRect(self.childrenBoundingRect())
        else:
            painter.setPen(self._pen)
        painter.drawLine(self._draftLine)
        painter.setFont(self._tickFont)
        for tickTuple in self._tickTuples:
            painter.drawLine(tickTuple.line[0], tickTuple.line[1])
            painter.save()
            painter.translate(tickTuple.point)
            painter.rotate(self.angle)
            painter.translate(-tickTuple.point)
            painter.drawText(tickTuple.point.x(), tickTuple.point.y(), tickTuple.text)
            painter.restore()

    @property
    def draftLine(self):
        return self._draftLine

    @draftLine.setter
    def draftLine(self, line: QLineF):
        self.prepareGeometryChange()
        self._draftLine = line
        angle = self._draftLine.angle()
        self._determineAngle(angle)
        self._createRulerTicks()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width: float):
        self._width = width

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value: int):
        self._mode = value

    @property
    def tickFont(self):
        return self._tickFont

    @property
    def tickGap(self):
        return self._tickGap


class alignLine(layoutShape):
    def __init__(
            self,
            draftLine: QLineF,
            width: int = 1,
            mode: int = 0,
    ):
        """
        Initialize the TickLine object.

        Args:
            draftLine (QLineF): The draft line.
            width (float): The width of the line.
            mode (int, optional): The mode. Defaults to 0.
        """
        super().__init__()

        self._draftLine = draftLine
        self._width: int = width
        self._mode = mode
        self._angle = 0
        self._rect = QRect(0, 0, 0, 0)
        penColour = QColor(255, 40, 40)
        self._pen = QPen(penColour, self._width, Qt.SolidLine)
        self._pen.setCosmetic(True)
        self._selectedPen = QPen(Qt.red, self._width + 1, Qt.SolidLine)
        self._selectedPen.setCosmetic(True)
        self._determineAngle(self._draftLine.angle())
        self.setZValue(999)

    def __repr__(self):
        return f"alignLine({self._draftLine}, {self._width}, {self._mode})"

    def _determineAngle(self, angle: float):
        match self._mode:
            case 0:  # horizontal
                self._createHorizontalLine(angle)
            case 1:  # vertical
                self._createVerticalLine(angle)
        self._draftLine.setAngle(0)
        self.setTransformOriginPoint(self.draftLine.p1())
        self.setRotation(-self._angle)

    def _createHorizontalLine(self, angle):
        if 0 <= angle <= 90 or 360 > angle > 270:
            self._angle = 0
        elif 90 < angle <= 270:
            self._angle = 180

    def _createVerticalLine(self, angle):
        if 0 <= angle < 180:
            self._angle = 90
        elif 180 < angle <= 360:
            self._angle = 270

    def boundingRect(self) -> QRectF:
        half_w = self._width // 2 + 2
        return (
            QRectF(self._draftLine.p1(), self._draftLine.p2())
            .normalized()
            .adjusted(-half_w, -half_w, half_w, half_w)
        )

    def paint(self, painter, option, widget=None):
        if self.isSelected():
            painter.setPen(self._selectedPen)
            painter.drawRect(self.boundingRect())
        else:
            painter.setPen(self._pen)
        painter.drawLine(self._draftLine)

    @property
    def draftLine(self):
        return self._draftLine

    @draftLine.setter
    def draftLine(self, line: QLineF):
        self.prepareGeometryChange()
        self._draftLine = line
        angle = self._draftLine.angle()
        self._determineAngle(angle)

    @property
    def angle(self) -> float:
        return self._angle

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width: float):
        self._width = width

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value: int):
        self._mode = value

    @property
    def sceneEndPoints(self):
        return [
            self.mapToScene(self._draftLine.p1()).toPoint(),
            self.mapToScene(self._draftLine.p2()).toPoint(),
        ]
