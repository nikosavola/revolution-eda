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

"""Schematic pin, alignment line, and utility types."""

from typing import NamedTuple

from PySide6.QtCore import (QLineF, QPoint, QRect, QRectF, Qt)
from PySide6.QtGui import (QBrush, QFont, QFontMetrics,
                           QPainterPath, QPolygonF, QTextOption,
                           QPen, QColor)
from PySide6.QtWidgets import (QGraphicsItem, QGraphicsPolygonItem,
                               QGraphicsSceneMouseEvent)

from revedaEditor.backend.pdkLoader import importPDKModule
from revedaEditor.common.shapes.base import symbolShape

schlyr = importPDKModule("schLayers")
symlyr = importPDKModule("symLayers")

class schematicPinPolygon(QGraphicsPolygonItem):
    def __init__(self, polygon: Union[QPolygonF, QPolygon],
                 parent: QGraphicsScene):
        self._polygon = polygon
        self._parent = parent
        super().__init__(self._polygon, self._parent)

    def paint(self, painter, option, widget=...):
        if self.isSelected():
            painter.setPen(schlyr.selectedSchematicPinPen)
            painter.setBrush(schlyr.selectedSchematicPinBrush)
        else:
            painter.setPen(schlyr.schematicPinPen)
            painter.setBrush(schlyr.schematicPinBrush)
        painter.drawPolygon(self._polygon)


class schematicPin(symbolShape):
    """
    schematic pin class.
    """

    pinDirs = ["Input", "Output", "Inout"]
    pinTypes = ["Signal", "Ground", "Power", "Clock", "Digital", "Analog"]
    PIN_WIDTH = 40
    PIN_HEIGHT = 20
    TEXT_MARGIN = 10

    def __init__(self, start: QPoint, pinName: str, pinDir: str, pinType: str, ):
        super().__init__()
        self._start = start
        # self.setPos(start)
        self._pinName = pinName
        self._pinDir = pinDir
        self._pinType = pinType
        self._pinNetSet: set[net.schematicNet] = set()
        self._snapLines: set[net.guideLine] = set()
        self._font = QFont("Arial", 12)
        self._updateTextMetrics()
        self._pinItem = schematicPinPolygon(self.pinPolygon, self)
        self._centre = self._pinItem.boundingRect().center()
        self._textItem = QGraphicsSimpleTextItem(self._pinName, self)
        self._textItem.setFont(self._font)
        self._textItem.setPos(self._centre.x(), self._centre.y())
        self._textItem.setBrush(QBrush(schlyr.schematicPinNameLayer.bcolor))
        self._textItem.setParentItem(self)
        self.setFiltersChildEvents(True)
        self.setHandlesChildEvents(True)
        self.setFlag(QGraphicsItem.ItemContainsChildrenInShape, True)
        self.flipTuple = (1, 1)

    def _updateTextMetrics(self):
        self.metrics = QFontMetrics(
            self._font)  # self._textHeight = self.metrics.height()

    def setFont(self, font):
        self._font = font
        self._updateTextMetrics()
        self.prepareGeometryChange()

    def __repr__(self) -> str:
        return (f"schematicPin({self._start}, {self._pinName}, {self._pinDir}, "
                f"{self._pinType})")

    def paint(self, painter, option, widget):
        if self.isSelected():
            painter.setPen(schlyr.selectedSchematicPinPen)
            painter.drawRect(self.childrenBoundingRect())
        self.setZValue(schlyr.schematicPinLayer.z)

    @property
    def pinPolygon(self):
        x, y = self._start.x(), self._start.y()
        hw, hh = self.PIN_WIDTH / 2, self.PIN_HEIGHT / 2

        polygons = {
            "Input": [(-hh, -hh), (hh, -hh), (hw, 0), (hh, hh), (-hh, hh)],
            "Output": [(-hw, 0), (-hh, -hh), (hh, -hh), (hh, hh), (-hh, hh)],
            "Inout": [(-hw, 0), (-hh, -hh), (hh, -hh), (hw, 0), (hh, hh),
                      (-hh, hh)]
        }

        return QPolygonF(
            [QPoint(x + dx, y + dy) for dx, dy in polygons[self.pinDir]])

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedHasChanged:
            if value:
                self.scene().selectedPin = self
            else:
                self.scene().selectedPin = None
        elif change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self._finishSnapLines()
            self._snapLines = set()
        return super().itemChange(change, value)

    def boundingRect(self):
        return self.childrenBoundingRect()

    def shape(self):
        path = QPainterPath()
        # Add a shape for the pin
        pin_rect = (QRect(self._start.x() - self.PIN_WIDTH / 2,
                          self._start.y() - self.PIN_HEIGHT / 2, self.PIN_WIDTH,
                          self.PIN_HEIGHT, ).normalized().adjusted(-5, -5, 5, 5))

        path.addRect(pin_rect)
        return path

    def generatePinNetDict(self):
        # unfortunate choice of method name to be compatible with schematicSymbol
        # implementation
        self._pinNetSet = set()

        for netItem in self.collidingItems(Qt.IntersectsItemBoundingRect):
            if isinstance(netItem, net.schematicNet):
                self._pinNetSet.add(netItem)

    def initializeSnapLines(self, scene):
        self._snapLines = set()

        if not self._pinNetSet:
            return None
        centrePoint = self.mapToScene(self._centre).toPoint()
        for netItem in self._pinNetSet:
            endPoint = None
            for point in netItem.sceneEndPoints:
                if (centrePoint - point).manhattanLength() < max(self.PIN_HEIGHT,
                                                                 self.PIN_WIDTH):
                    endPoint = netItem.sceneOtherEnd(point)
                    break
            if endPoint:
                snapLine = net.guideLine(centrePoint, endPoint)
                snapLine.inherit(netItem)
                self._snapLines.add(snapLine)
                scene.deleteUndoStack(netItem)
                scene.addItem(snapLine)

    def updateSnapLines(self):
        if not self._snapLines:
            return None
        pinCentre = self.mapToScene(self._centre).toPoint()
        for snapLine in self._snapLines:
            current_end = snapLine.line().p2()
            new_line = QLineF(pinCentre, current_end)

            # Only update if there's a significant change
            if (new_line.length() > 1  # Avoid very short lines
                    and (abs(new_line.dx()) > 1 or abs(
                        new_line.dy()) > 1)):  # Avoid unnecessary updates
                snapLine.setLine(new_line)
            else:
                # Remove unnecessary lines
                self.scene().removeItem(snapLine)
                self._snapLines.remove(snapLine)

    def _finishSnapLines(self):
        if self._snapLines:
            try:
                scene = self.scene()
                for snapLine in self._snapLines:
                    newNets = scene.addStretchWires(
                        snapLine.line().p1().toPoint(),
                        snapLine.line().p2().toPoint())
                    if newNets:
                        for netItem in newNets:
                            netItem.inherit(snapLine)
                        scene.addListUndoStack(newNets)
                    scene.removeItem(snapLine)
                self._snapLines = set()
            except Exception as e:
                # Log error but continue processing other guidelines
                scene.logger.error(f"Error processing snap lines: {e}")

    # def findPinNetIndexTuples(self, ) -> List[
    #     Tuple["schematicPin", "net.schematicNet", int]]:
    #     # Use a list instead of a set for better performance if order doesn't matter
    #     self._pinNetIndexTupleSet = []
    #
    #     # Create a slightly larger rectangle around the pin for collision detection
    #     pin_rect = QRectF(self._start.x() - 5, self._start.y() - 5, 10, 10)
    #     pin_scene_rect = self.mapRectToScene(pin_rect)
    #
    #     # Use a QPainterPath for more accurate collision detection
    #     pin_path = QPainterPath()
    #     pin_path.addRect(pin_scene_rect)
    #
    #     # Find all items that collide with the pin's path
    #     colliding_items = self.scene().items(pin_path)
    #
    #     # Filter for SchematicNet items and process them
    #     for item in colliding_items:
    #         if isinstance(item, net.schematicNet):
    #             for index, end_point in enumerate(item.sceneEndPoints):
    #                 if pin_scene_rect.contains(end_point):
    #                     self._pinNetIndexTupleSet.append(
    #                         pinNetIndexTuple(self, item, index))
    #                     break  # Assume only one end of a net can connect to a pin
    #
    #     return self._pinNetIndexTupleSet

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mousePressEvent(event)
        # self.findPinNetIndexTuples()
        # for tupleItem in self._pinNetIndexTupleSet:
        #     self._snapLines = set()
        #     snapLine = net.guideLine(self.mapToScene(self.start),
        #                              tupleItem.net.sceneEndPoints[
        #                                  tupleItem.netEndIndex - 1], )
        #     snapLine.inherit(tupleItem.net)
        #
        #     self.scene().addItem(snapLine)
        #     self._snapLines.add(snapLine)
        #     self.scene().removeItem(tupleItem.net)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        # lines: list[net.schematicNet] = []
        # if hasattr(self, "snapLines"):
        #     for snapLine in self._snapLines:
        #         lines = self.scene().addStretchWires(
        #             self.mapToScene(self.start).toPoint(),
        #             snapLine.mapToScene(snapLine.line().p2()).toPoint(), )
        #         if lines:
        #             for line in lines:
        #                 line.inherit(snapLine)
        #             self.scene().addListUndoStack(lines)
        #         self.scene().removeItem(snapLine)
        # self._snapLines = dict()

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseMoveEvent(event)
        if self._snapLines:
            for snapLine in self._snapLines:
                snapLine.setLine(
                    QLineF(snapLine.mapFromScene(self.mapToScene(self.start)),
                           snapLine.line().p2(), ))

    def toSymbolPin(self, start: QPoint):
        return symbolPin(start, self.pinName, self.pinDir, self.pinType)

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start):
        self.prepareGeometryChange()
        self._pinItem.setPos(self.mapToScene(start).toPoint())
        self._textItem.setPos(start.x(), start.y())
        self._start = start

    @property
    def pinName(self):
        return self._pinName

    @pinName.setter
    def pinName(self, pinName):
        if pinName != "":
            self._pinName = pinName

    @property
    def pinDir(self):
        return self._pinDir

    @pinDir.setter
    def pinDir(self, direction: str):
        if direction in self.pinDirs:
            self._pinDir = direction

    @property
    def pinType(self):
        return self._pinType

    @pinType.setter
    def pinType(self, pintype: str):
        if pintype in self.pinTypes:
            self._pinType = pintype

    @property
    def flipTuple(self):
        return self._flipTuple

    @flipTuple.setter
    def flipTuple(self, flipState: Tuple[int, int]):
        self.prepareGeometryChange()
        # Get the current transformation
        transform = self._pinItem.transform()
        # Apply the scaling
        polygonStart = self._pinItem.boundingRect().center().toPoint()
        transform.translate(polygonStart.x(), polygonStart.y())
        transform.scale(*flipState)
        self._flipTuple = (transform.m11(), transform.m22())
        transform.translate(-polygonStart.x(), -polygonStart.y())
        # textTransform, invertible =transform.inverted()
        # if invertible:
        #     textTransform.translate(self.PIN_WIDTH*0.5*self._flipTuple[0],self.PIN_HEIGHT*0.5*self._flipTuple[1])
        #     self._textItem.setTransform(textTransform)

        # Set the new transformation
        self._pinItem.setTransform(transform, combine=False)


class alignLine(symbolShape):
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
        self._pen.setCosmetic(False)
        self._selectedPen = QPen(Qt.red, self._width + 1, Qt.SolidLine)
        self._selectedPen.setCosmetic(False)
        self._determineAngle(self._draftLine.angle())
        self.setZValue(999)

    def __repr__(self):
        return (
            f"alignLine({self._draftLine}, {self._width}, {self._mode})"
        )

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
        return QRectF(self._draftLine.p1(),
                      self._draftLine.p2()).normalized().adjusted(
            -half_w, -half_w, half_w, half_w)

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


class pinNetIndexTuple(NamedTuple):
    pin: Union[symbolPin, schematicPin]
    net: net.schematicNet
    netEndIndex: int
