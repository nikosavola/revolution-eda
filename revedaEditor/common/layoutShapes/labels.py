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

"""Label and pin shapes for layout editor."""

from PySide6.QtCore import (
    QPoint,
    QRect,
    QRectF,
    Qt,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QFontMetrics,
    QPainterPath,
    QPen,
    QTextOption,
)
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsSceneMouseEvent,
)

import revedaEditor.backend.dataDefinitions as ddef
from revedaEditor.common.layoutShapes.base import layoutShape
from revedaEditor.common.layoutShapes.rectangles import layoutRect

class layoutLabel(layoutShape):
    LABEL_ALIGNMENTS = ["Left", "Center", "Right"]
    LABEL_ORIENTS = ["R0", "R90", "R180", "R270", "MX", "MX90", "MY", "MY90"]
    LABEL_SCALE = 10

    def __init__(
            self,
            start: QPoint,
            labelText: str,
            fontFamily: str,
            fontStyle: str,
            fontHeight: str,
            labelAlign: str,
            labelOrient: str,
            layer: ddef.layLayer,
    ):
        super().__init__()
        self._start = start
        self._labelText = labelText
        self._fontFamily = fontFamily
        self._fontStyle = fontStyle
        self._fontHeight = fontHeight
        self._labelAlign = labelAlign
        self._labelOrient = labelOrient
        self._layer = layer
        self._definePensBrushes(self._layer)
        self._labelFont = QFont(fontFamily)
        self._labelFont.setStyleName(fontStyle)
        self._labelFont.setKerning(False)
        self._labelFont.setPointSize(int(float(self._fontHeight) * self.LABEL_SCALE))
        # self.setOpacity(1)
        self._fm = QFontMetrics(self._labelFont)
        self._rect = self._fm.boundingRect(self._labelText)
        self._labelOptions = QTextOption()
        if self._labelAlign == layoutLabel.LABEL_ALIGNMENTS[0]:
            self._labelOptions.setAlignment(Qt.AlignmentFlag.AlignLeft)
        elif self._labelAlign == layoutLabel.LABEL_ALIGNMENTS[1]:
            self._labelOptions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        elif self._labelAlign == layoutLabel.LABEL_ALIGNMENTS[2]:
            self._labelOptions.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setOrient()
        self.setZValue(self._layer.z)

    def __repr__(self):
        return (
            f"layoutLabel({self._start}, {self._labelText}, {self._fontFamily}, "
            f"{self._fontStyle}, {self._fontHeight}, {self._labelAlign}, "
            f"{self._labelOrient}, {self._layer})"
        )

    def setOrient(self):
        self.setTransformOriginPoint(self.mapFromScene(self._start))
        if self._labelOrient == layoutLabel.LABEL_ORIENTS[0]:
            self.setRotation(0)
        elif self._labelOrient == layoutLabel.LABEL_ORIENTS[1]:
            self.setRotation(90)
        elif self._labelOrient == layoutLabel.LABEL_ORIENTS[2]:
            self.setRotation(180)
        elif self._labelOrient == layoutLabel.LABEL_ORIENTS[3]:
            self.setRotation(270)
        elif self._labelOrient == layoutLabel.LABEL_ORIENTS[4]:
            self.flipTuple = (-1, 1)
        elif self._labelOrient == layoutLabel.LABEL_ORIENTS[5]:
            self.flipTuple = (-1, 1)
            self.setRotation(90)
        elif self._labelOrient == layoutLabel.LABEL_ORIENTS[6]:
            self.flipTuple = (1, -1)
            self.setRotation(90)

    def boundingRect(self):
        return (
            QRect(
                self._start.x(),
                self._start.y(),
                self._rect.width(),
                self._rect.height(),
            )
            .normalized()
            .adjusted(-2, -2, 2, 2)
        )  #

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def paint(self, painter, option, widget):
        painter.setFont(self._labelFont)
        if self.isSelected():
            painter.setPen(self._selectedPen)
            painter.drawRect(self.boundingRect())
        else:
            painter.setPen(self._pen)
        painter.drawText(
            QPoint(self._start.x(), self._start.y() + self._rect.height()),
            self._labelText,
        )
        painter.drawPoint(self._start)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self._layer.selectable:
            self.setFlag(QGraphicsItem.ItemIsMovable, True)
            self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        else:
            self.setFlag(QGraphicsItem.ItemIsMovable, False)
            self.setFlag(QGraphicsItem.ItemIsSelectable, False)

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value: QPoint):
        self.prepareGeometryChange()
        self._start = value

    @property
    def labelText(self):
        return self._labelText

    @labelText.setter
    def labelText(self, value):
        self.prepareGeometryChange()
        self._labelText = value
        self._rect = self._fm.boundingRect(self._labelText)

    @property
    def labelFont(self):
        return self._labelFont

    @property
    def fontFamily(self) -> str:
        return self._labelFont.family()

    @fontFamily.setter
    def fontFamily(self, familyName):
        fontFamilies = QFontDatabase.families(QFontDatabase.Latin)
        fixedFamilies = [
            family for family in fontFamilies if QFontDatabase.isFixedPitch(family)
        ]
        if familyName in fixedFamilies:
            self._labelFont.setFamily(familyName)
        else:
            self.scene().logger.error(f"Not a valid font name: {familyName}")

    @property
    def fontStyle(self):
        return self._labelFont.styleName()

    @fontStyle.setter
    def fontStyle(self, value):
        if value in QFontDatabase.styles(self._labelFont.family()):
            self._labelFont.setStyleName(value)
        else:
            self.scene().logger.error(f"Not a valid font style: {value}")

    @property
    def fontHeight(self):
        return self._fontHeight

    @fontHeight.setter
    def fontHeight(self, value: str):
        self.prepareGeometryChange()
        self._fontHeight = value
        self._labelFont.setPointSize(int(float(self._fontHeight) * self.LABEL_SCALE))
        self._fm = QFontMetrics(self._labelFont)
        self._rect = self._fm.boundingRect(self._labelText)

    @property
    def labelAlign(self):
        return self._labelAlign

    @labelAlign.setter
    def labelAlign(self, value):
        self.prepareGeometryChange()
        self._labelAlign = value

    @property
    def labelOrient(self):
        return self._labelOrient

    @labelOrient.setter
    def labelOrient(self, value):
        self.prepareGeometryChange()
        self._labelOrient = value



class layoutPin(layoutShape):
    pinDirs = ["Input", "Output", "Inout"]
    pinTypes = ["Signal", "Ground", "Power", "Clock", "Digital", "Analog"]

    def __init__(
            self,
            start,
            end,
            pinName: str,
            pinDir: str,
            pinType: str,
            layer: ddef.layLayer,
    ):
        super().__init__()
        self._pinName = pinName
        self._pinDir = pinDir
        self._pinType = pinType
        self._connected = False  # True if the pin is connected to a net.
        self._rect = QRect(start, end).normalized()
        self._start = self._rect.topLeft()
        self._end = self._rect.bottomRight()
        self._layer = layer
        self._definePensBrushes(self._layer)
        self._label = None
        self._stretchSide = None
        self._stretchPen = QPen(QColor("red"), self._layer.pwidth, Qt.SolidLine)
        self.setZValue(self._layer.z)

    def __repr__(self):
        return (
            f"layoutPin({self._start}, {self._end}, {self._pinName}, {self._pinDir}, "
            f"{self._pinType}, {self._layer})"
        )

    def paint(self, painter, option, widget):
        # Get scale once and cache it
        scale = self.scene().views()[0].transform().m11()
        if self.isSelected():
            painter.setPen(self._selectedPen)
            self._updateTransformedBrush(self._selectedBrush, scale)
        else:
            painter.setPen(self._pen)
            self._updateTransformedBrush(self._brush, scale)
        painter.setBrush(self._brush)
        painter.drawRect(self._rect)

    def boundingRect(self):
        return self._rect.adjusted(-2, 2, 2, 2)

    @property
    def pinName(self):
        return self._pinName

    @pinName.setter
    def pinName(self, value):
        self._pinName = value

    @property
    def pinDir(self):
        return self._pinDir

    @pinDir.setter
    def pinDir(self, value):
        self._pinDir = value

    @property
    def pinType(self):
        return self._pinType

    @pinType.setter
    def pinType(self, value):
        self._pinType = value

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start: QPoint):
        self.prepareGeometryChange()
        self._rect = QRectF(start, self._end).normalized()
        self._start = self._rect.topLeft()

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, end: QPoint):
        self.prepareGeometryChange()
        self._rect = QRectF(self._start, end).normalized()
        self._end = self._rect.bottomRight()

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value: layoutLabel):
        if isinstance(value, layoutLabel):
            self._label = value
        else:
            self.scene().logger.error("Not a Label")

    @property
    def rect(self):
        return self._rect

    @rect.setter
    def rect(self, rect: QRect):
        self.prepareGeometryChange()
        self._rect = rect

    @property
    def stretchSide(self):
        return self._stretchSide

    @stretchSide.setter
    def stretchSide(self, value: str):
        self.prepareGeometryChange()
        self._stretchSide = value

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
        if self._stretch and self._stretchSide:
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

