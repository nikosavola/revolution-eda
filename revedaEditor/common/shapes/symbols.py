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

"""Symbol pin, text, and schematic symbol shapes."""

from collections import OrderedDict
from functools import cached_property
from typing import Dict, Tuple, Union

from PySide6.QtCore import (QLine, QLineF, QPoint, QRect, QRectF, Qt)
from PySide6.QtGui import (QBrush, QFont, QFontDatabase, QFontMetrics,
                           QPainterPath, QPolygonF, QTextOption,
                           QTransform, QPen, QColor)
from PySide6.QtWidgets import (QGraphicsItem, QGraphicsSceneHoverEvent,
                               QGraphicsSceneMouseEvent,
                               QGraphicsSimpleTextItem, QStyle)

import revedaEditor.common.net as net
from revedaEditor.backend.pdkLoader import importPDKModule
from revedaEditor.common.labels import symbolLabel
from revedaEditor.common.shapes.base import symbolShape

schlyr = importPDKModule("schLayers")
symlyr = importPDKModule("symLayers")

class symbolPin(symbolShape):
    """
    symbol pin class definition for symbol drawing.
    """

    PIN_HEIGHT = 10
    PIN_WIDTH = 10
    TEXT_MARGIN = 10

    pinDirs = ["Input", "Output", "Inout"]
    pinTypes = ["Signal", "Ground", "Power", "Clock", "Digital", "Analog"]

    def __init__(self, start: QPoint, pinName: str, pinDir: str, pinType: str, ):
        super().__init__()

        self._start = start  # centre of pin
        self._pinName = pinName
        self._pinDir = pinDir
        self._pinType = pinType
        self._connected = False  # True if the pin is connected to a net.
        self._highlighted = False
        self._pinRectItem = QGraphicsRectItem(
            QRect(int(self._start.x() - self.PIN_WIDTH / 2),
                  int(self._start.y() - self.PIN_HEIGHT / 2), self.PIN_WIDTH,
                  self.PIN_HEIGHT, ))
        self._pinRectItem.setPen(symlyr.symbolPinPen)
        self._pinRectItem.setBrush(symlyr.symbolPinBrush)
        self._pinRectItem.setParentItem(self)
        self._pinRect = self._pinRectItem.rect().adjusted(-2, -2, 2, 2)
        self._pinNameItem = QGraphicsSimpleTextItem(self._pinName)
        self._pinNameItem.setZValue(symlyr.symbolPinLayer.z + 10)
        self._font = QFont("Arial", 10)

        self._pinNameItem.setFont(self._font)
        self._pinNameItem.setPos(self._start.x() - self.PIN_WIDTH / 2,
                                 self._start.y() - self.PIN_HEIGHT / 2 + self.TEXT_MARGIN, )
        self._pinNameItem.setBrush(symlyr.symbolPinBrush)
        # self._pinNameItem.setDefaultTextColor(pdk.symLayers.symbolPinLayer.bcolor)
        self._pinNameItem.setParentItem(self)
        self.setFiltersChildEvents(True)
        self.setHandlesChildEvents(True)
        self.setFlag(QGraphicsItem.ItemContainsChildrenInShape, True)

    def __str__(self):
        return f"symbolPin: {self._pinName} {self.mapToScene(self._start)}"

    def boundingRect(self):
        return self.childrenBoundingRect()

    def paint(self, painter, option, widget=None):
        pass

    def __repr__(self):
        return f"pin({self._start},{self._pinName}, {self._pinDir}, {self._pinType})"

    # def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
    #     super().mouseReleaseEvent(event)


    def itemChange(self, change, value):
        # if change == QGraphicsItem.ItemSceneHasChanged:
        #     # The scene change is complete
        #     if self.scene().__class__.__name__ == 'schematicScene':
        #         self._pinNameItem.setVisible(False)
        if change == QGraphicsItem.ItemSelectedHasChanged:
            if value:
                self.scene().selectedSymbolPin = self
            else:
                self.scene().selectedSymbolPin = None
        return super().itemChange(change, value)

    def shape(self):
        path = QPainterPath()
        path.addRect(self._pinRect)
        return path

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start):
        self.prepareGeometryChange()
        self._start = start
        self._pinRectItem = QGraphicsRectItem(
            QRect(self._start.x() - self.PIN_WIDTH / 2,
                  self._start.y() - self.PIN_HEIGHT / 2, self.PIN_WIDTH,
                  self.PIN_HEIGHT, ), self, )
        self._pinRect = self._pinRectItem.rect()

    @property
    def pinName(self):
        return self._pinName

    @pinName.setter
    def pinName(self, pinName):
        if pinName != "":
            self.prepareGeometryChange()
            self._pinName = pinName

    @property
    def pinNameItem(self):
        return self._pinNameItem

    @property
    def pinDir(self):
        return self._pinDir

    @pinDir.setter
    def pinDir(self, direction: str):
        if direction in symbolPin.pinDirs:
            self._pinDir = direction

    @property
    def pinType(self):
        return self._pinType

    @pinType.setter
    def pinType(self, pintype: str):
        if pintype in self.pinTypes:
            self._pinType = pintype

    @property
    def connected(self):
        return self._connected

    @connected.setter
    def connected(self, value: bool):
        if isinstance(value, bool):
            self._connected = value

    @property
    def highlighted(self):
        return self._highlighted

    @highlighted.setter
    def highlighted(self, value: bool):
        if isinstance(value, bool):
            self._highlighted = value

    def toSchematicPin(self, start: QPoint):
        return schematicPin(start, self.pinName, self.pinDir, self.pinType)

    @property
    def flipTuple(self):
        return self._flipTuple

    @flipTuple.setter
    def flipTuple(self, flipState: Tuple[int, int]):
        self.prepareGeometryChange()
        # Get the current transformation
        transform = self.transform()
        # Apply the scaling
        transform.scale(*flipState)
        # Set the new transformation
        self.setTransform(transform)
        self._flipTuple = (transform.m11(), transform.m22())
        pinNameTransform, invertible = transform.inverted()
        if invertible:
            self._pinNameItem.setTransform(pinNameTransform)
        self.update()


class text(symbolShape):
    """
    This class is for text annotations on symbol or schematics.
    """

    textAlignments = ["Left", "Center", "Right"]
    textOrients = ["R0", "R90", "R180", "R270"]

    def __init__(self, start: QPoint, textContent: str, fontFamily: str,
                 fontStyle: str, textHeight: str, textAlign: str,
                 textOrient: str, ):
        super().__init__()
        self._start = start
        self._textContent = textContent
        self._textHeight = textHeight
        self._textAlign = textAlign
        self._textOrient = textOrient
        self._textFont = QFont(fontFamily)
        self._textFont.setStyleName(fontStyle)
        self._textFont.setPointSize(int(float(self._textHeight)))
        self._textFont.setKerning(True)
        self.setOpacity(1)
        self._fm = QFontMetrics(self._textFont)
        self._textOptions = QTextOption()
        self.setOrient()
        if self._textAlign == text.textAlignments[0]:
            self._textOptions.setAlignment(Qt.AlignmentFlag.AlignLeft)
        elif self._textAlign == text.textAlignments[1]:
            self._textOptions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        elif self._textAlign == text.textAlignments[2]:
            self._textOptions.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._rect = self._fm.boundingRect(QRect(0, 0, 400, 400),
                                           Qt.AlignmentFlag.AlignCenter,
                                           self._textContent)

    def __repr__(self):
        return (
            f"text({self._start},{self._textContent}, {self._textFont.family()},"
            f" {self._textFont.style()}, {self._textHeight}, {self._textAlign},"
            f"{self._textOrient})")

    def setOrient(self):
        if self._textOrient == text.textOrients[0]:
            self.setRotation(0)
        elif self._textOrient == text.textOrients[1]:
            self.setRotation(90)
        elif self._textOrient == text.textOrients[2]:
            self.setRotation(180)
        elif self._textOrient == text.textOrients[3]:
            self.setRotation(270)
        elif self._textOrient == text.textOrients[4]:
            self.flip("x")
        elif self._labelOrient == text.textOrients[5]:
            self.flip("x")
            self.setRotation(90)
        elif self._labelOrient == text.textOrients[6]:
            self.flip("y")
            self.setRotation(90)

    def flip(self, direction: str):
        currentTransform = self.transform()
        newTransform = QTransform()
        if direction == "x":
            currentTransform = newTransform.scale(-1, 1) * currentTransform
        elif direction == "y":
            currentTransform = newTransform.scale(1, -1) * currentTransform
        self.setTransform(currentTransform)

    def boundingRect(self):
        if self._textAlign == text.textAlignments[0]:
            self._rect = self._fm.boundingRect(QRect(0, 0, 400, 400),
                                               Qt.AlignmentFlag.AlignLeft,
                                               self._textContent)
        elif self._textAlign == text.textAlignments[1]:
            self._rect = self._fm.boundingRect(QRect(0, 0, 400, 400),
                                               Qt.AlignmentFlag.AlignCenter,
                                               self._textContent)
        elif self._textAlign == text.textAlignments[2]:
            self._rect = self._fm.boundingRect(QRect(0, 0, 400, 400),
                                               Qt.AlignmentFlag.AlignRight,
                                               self._textContent)
        return (QRect(self._start.x(), self._start.y() - self._rect.height(),
                      self._rect.width(),
                      self._rect.height(), ).normalized().adjusted(-2, -2, 2, 2))

    def paint(self, painter, option, widget):
        painter.setFont(self._textFont)
        if option.state & QStyle.State_Selected:
            painter.setPen(schlyr.selectedTextPen)
            painter.drawRect(self.boundingRect().adjusted(2, 2, -2, -2))
            self.setZValue(schlyr.selectedTextLayer.z)
        else:
            painter.setPen(schlyr.textPen)
            self.setZValue(schlyr.textLayer.z)
        painter.drawText(self.boundingRect(), self._textContent,
                         o=self._textOptions)

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value: QPoint):
        self.prepareGeometryChange()
        self._start = value

    @property
    def textContent(self):
        return self._textContent

    @textContent.setter
    def textContent(self, inputText: str):
        if isinstance(inputText, str):
            self._textContent = inputText
        else:
            self.scene().logger.error(f"Not a string: {inputText}")

    @property
    def fontFamily(self) -> str:
        return self._textFont.family()

    @fontFamily.setter
    def fontFamily(self, familyName):
        fontFamilies = QFontDatabase.families(QFontDatabase.Latin)
        fixedFamilies = [family for family in fontFamilies if
                         QFontDatabase.isFixedPitch(family)]
        if familyName in fixedFamilies:
            self._textFont.setFamily(familyName)
        else:
            self.scene().logger.error(f"Not a valid font name: {familyName}")

    @property
    def fontStyle(self) -> str:
        return self._textFont.styleName()

    @fontStyle.setter
    def fontStyle(self, value: str):
        if value in QFontDatabase.styles(self._textFont.family()):
            self._textFont.setStyleName(value)
        else:
            self.scene().logger.error(f"Not a valid font style: {value}")

    @property
    def textHeight(self) -> str:
        return self._textHeight

    @textHeight.setter
    def textHeight(self, value: int):
        fontSizes = [str(size) for size in
                     QFontDatabase.pointSizes(self._textFont.family(),
                                              self._textFont.styleName())]
        if value in fontSizes:
            self._textHeight = value
        else:
            self.scene().logger.error(f"Not a valid font height: {value}")
            self.scene().logger.warning(f"Valid font heights are: {fontSizes}")

    @property
    def textFont(self) -> QFont:
        return self._textFont

    @textFont.setter
    def textFont(self, value: QFont):
        assert isinstance(value, QFont)
        self._textFont = value

    @property
    def textAlignment(self):
        return self._textAlign

    @textAlignment.setter
    def textAlignment(self, value):
        if value in text.textAlignments:
            self._textAlign = value
        else:
            self.scene().logger.error(
                f"Not a valid text alignment value: {value}")

    @property
    def textOrient(self):
        return self._textOrient

    @textOrient.setter
    def textOrient(self, value):
        if value in text.textOrients:
            self._textOrient = value
        else:
            self.scene().logger.error(f"Not a valid text orientation: {value}")


class schematicSymbol(symbolShape):
    def __init__(self, shapes: list, attr: dict):
        super().__init__()
        self._shapes = shapes  # list of shapes in the symbol
        self._symattrs = attr  # parameters common to all instances of symbol
        self._counter = 0  # item's number on schematic
        self._libraryName = ""
        self._cellName = ""
        self._viewName = ""
        self._instanceName = ""
        self._netlistLine = ""
        self._labels: Dict[str, symbolLabel] = dict()  # dict of labels
        self._pins: Dict[str, symbolPin] = dict()  # dict of pins
        self._netlistIgnore: bool = False
        self._draft: bool = False
        self._pinLocations: dict[
            str, Union[QRect, QRectF]] = dict()  # pinName: pinRect
        self.pinNetMap: dict[str, str] = dict()  # pinName: netName
        self._snapLines: dict[symbolPin, set[net.guideLine]] = dict()

        self._pinNetDict: dict[symbolPin, set[net.schematicNet]] = dict()
        self._setup_graphics()
        self.addShapes()
        self._start = self.childrenBoundingRect().bottomLeft()
        # self.sceneRect = QRectF(0,0,0,0)

    def _setup_graphics(self):
        """Setup graphics item properties"""
        self.setFiltersChildEvents(True)
        self.setHandlesChildEvents(True)
        self.setFlag(QGraphicsItem.ItemContainsChildrenInShape, True)

    def addShapes(self):
        for item in self._shapes:
            item.setFlag(QGraphicsItem.ItemIsSelectable, False)
            item.setFlag(QGraphicsItem.ItemStacksBehindParent, True)
            item.setParentItem(self)
            if isinstance(item, symbolPin):
                self._pins[item.pinName] = item
            elif isinstance(item, symbolLabel):
                self._labels[item.labelName] = item

    def __repr__(self):
        return f"schematicSymbol({self._instanceName})"

    def shape(self):
        path = QPainterPath()
        validTypes = (symbolRectangle, symbolLine, symbolArc, symbolCircle,
                      symbolPolygon)

        bounding_rect = QRectF()
        for item in self.childItems():
            if isinstance(item, validTypes):
                bounding_rect = bounding_rect.united(item.sceneBoundingRect())

        if not bounding_rect.isNull():
            path.addRect(self.mapRectFromScene(bounding_rect))

        return path

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if not (scene := self.scene()):
            return super().itemChange(change, value)

        # if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
        #     self.sceneRect = self.sceneBoundingRect().adjusted(-5,-5,5,5)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self._finishSnapLines()
            self._snapLines = dict()
            # self.scene().invalidate(self.sceneRect, QGraphicsScene.BackgroundLayer)
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            if scene.editModes.selectItem:
                scene.selectedSymbol = self if value else None

        return super().itemChange(change, value)

    def generatePinNetDict(self):
        self._pinNetDict = dict()
        for pinItem in self._pins.values():
            netSet: set[net.schematicNet] = set()
            for netItem in pinItem.collidingItems(Qt.IntersectsItemBoundingRect):
                if isinstance(netItem, net.schematicNet):
                    netSet.add(netItem)
            self._pinNetDict[pinItem] = netSet

    def initializeSnapLines(self, scene):
        self._snapLines = dict()
        sceneGrid = scene.snapTuple[0]
        for pinItem, netSet in self._pinNetDict.items():
            if not netSet:
                continue
            snapLinesSet: set[net.guideLine] = set()  # Move outside the loop
            startPoint = pinItem.mapToScene(pinItem.start).toPoint()
            for netItem in netSet:
                endPoint = None
                for point in netItem.sceneEndPoints:
                    if (startPoint - point).manhattanLength() < sceneGrid / 2:
                        endPoint = netItem.sceneOtherEnd(point)
                        break
                if endPoint:
                    snapLine = net.guideLine(startPoint, endPoint)
                    snapLine.inherit(netItem)
                    snapLinesSet.add(snapLine)
                    scene.deleteUndoStack(netItem)
                    scene.addItem(snapLine)
            self._snapLines[pinItem] = snapLinesSet

    def updateSnapLines(self):

        # shape is not connected to any nets
        for pin, snapLinesSet in self._snapLines.items():
            pin_start = pin.mapToScene(pin.start).toPoint()
            if not snapLinesSet:
                continue
            for snapLine in list(snapLinesSet):  # Iterate over a copy
                current_end = snapLine.line().p2()
                new_line = QLineF(pin_start, current_end)

                # Only update if there's a significant change
                if (new_line.length() > 1  # Avoid very short lines
                        and (abs(new_line.dx()) > 1 or abs(
                            new_line.dy()) > 1)):  # Avoid unnecessary updates
                    snapLine.setLine(new_line)
                else:
                    # Remove unnecessary lines
                    self.scene().removeItem(snapLine)
                    snapLinesSet.remove(snapLine)

    def _finishSnapLines(self):
        if self._snapLines:
            try:
                scene = self.scene()
                for snapLinesSet in self._snapLines.values():
                    for snapLine in snapLinesSet:
                        newNets = scene.addStretchWires(
                            snapLine.line().p1().toPoint(),
                            snapLine.line().p2().toPoint())
                        if newNets:
                            for netItem in newNets:
                                netItem.inherit(snapLine)
                            scene.addListUndoStack(newNets)
                        scene.removeItem(snapLine)
                self._snapLines = dict()
            except Exception as e:
                # Log error but continue processing other guidelines
                scene.logger.error(f"Error processing snap lines: {e}")

    def paint(self, painter, option, widget):
        # The shape() method is expensive. It's better to use boundingRect()
        # which is cached by Qt's graphics framework.
        shapeBoundingRect = self.boundingRect().adjusted(5, 5, -5, -5)

        is_selected = option.state & QStyle.State_Selected

        if is_selected:
            painter.setPen(symlyr.selectedSymbolPen)
            painter.drawRect(shapeBoundingRect)
        elif self._draft:
            painter.setPen(symlyr.draftPen)
            painter.drawRect(shapeBoundingRect)

        if self.netlistIgnore:
            painter.setPen(schlyr.ignoreSymbolPen)
            painter.drawLine(shapeBoundingRect.topLeft(),
                             shapeBoundingRect.bottomRight())
            painter.drawLine(shapeBoundingRect.bottomLeft(),
                             shapeBoundingRect.topRight())

    def boundingRect(self):
        return self.childrenBoundingRect()

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mousePressEvent(event)

        for pinItem in self._pins.values():
            if pinItem.contains(self.mapToItem(pinItem, event.pos())):
                self.scene().selectedSymbolPin = pinItem
                pinItem.highlighted = True
                pinItem.mousePressEvent(event)
                return

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

    # TODO: figure out what is wrong here
    @instanceName.setter
    def instanceName(self, value: str):
        """
        If instance name is changed and [@instName] label exists, change it too.
        """
        self._instanceName = value
        if self.labels.get("instanceName", None):
            self.labels["instanceName"].labelValue = value
            self.labels["instanceName"].update()

    @property
    def counter(self) -> int:
        return self._counter

    @counter.setter
    def counter(self, value: int):
        assert isinstance(value, int)
        self._counter = value

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value: float):
        self.setRotation(value)
        self._angle = value
        # for label in self.labels.values():
        #     label.angle = -value

    @property
    def labels(self):
        return self._labels  # dictionary

    @cached_property
    def pins(self):
        """
        Returns a dictionary of pins, ordered by the pinOrder attribute if it exists.
        """

        pinOrder = self.symattrs.get("pinOrder")
        if not pinOrder:
            return self._pins
        outputDict = OrderedDict()
        for key in pinOrder.split(", "):
            key = key.strip()
            if key in pinOrder:
                if key in self._pins:
                    outputDict[key] = self._pins[key]
        return outputDict

    @property
    def shapes(self):
        return self._shapes

    @shapes.setter
    def shapes(self, shapeList: list):
        self.prepareGeometryChange()
        self._shapes = shapeList
        self.addShapes()

    @property
    def symattrs(self):
        return self._symattrs

    @symattrs.setter
    def symattrs(self, attrDict: dict):
        self._symattrs = attrDict

    @property
    def instProps(self):
        return self._instProps

    @property
    def netlistIgnore(self) -> bool:
        return self._netlistIgnore

    @netlistIgnore.setter
    def netlistIgnore(self, value: bool):
        assert isinstance(value, bool)
        self._netlistIgnore = value

    @property
    def flipTuple(self):
        return self._flipTuple

    @flipTuple.setter
    def flipTuple(self, flipState: Tuple[int, int]):
        self.prepareGeometryChange()

        transform = self.transform()
        transform.scale(*flipState)
        self.setTransform(transform)
        self._flipTuple = (transform.m11(), transform.m22())
        inverseTransform, invertible = transform.inverted()

        if not invertible:
            return
        if self.flipTuple[0] < 0:  # Only shift if horizontally flipped
            inverseTransform.translate(-10, 0)
        for pin in self._pins.values():
            pin.pinNameItem.setTransform(inverseTransform)
        if self.flipTuple[0] < 0:  # Only shift if horizontally flipped
            inverseTransform.translate(-20, 0)
        for label in self.labels.values():
            label.setTransform(inverseTransform)

    @property
    def start(self):
        return self._start.toPoint()


