#    “Commons Clause” License Condition v1.0
#   #
#    The Software is provided to you by the Licensor under the License, as defined
#    below, subject to the following condition.
#
#    Without limiting other conditions in the License, the grant of rights under the
#    License will not include, and the License does not grant to you, the right to
#    Sell the Software.
#
#    For purposes of the foregoing, “Sell” means practicing any or all of the rights
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

import math
from collections import OrderedDict
from functools import cached_property
from typing import Dict, NamedTuple, Tuple, Union

from PySide6.QtCore import (QLine, QLineF, QPoint, QRect, QRectF, Qt, )
from PySide6.QtGui import (QBrush, QFont, QFontDatabase, QFontMetrics,
                           QPainterPath, QPolygon, QPolygonF, QTextOption,
                           QTransform, QPen, QColor)
from PySide6.QtWidgets import (QGraphicsItem, QGraphicsPolygonItem,
                               QGraphicsRectItem, QGraphicsScene,
                               QGraphicsSceneHoverEvent, QGraphicsSceneMouseEvent,
                               QGraphicsSimpleTextItem, QStyle)

from revedaEditor.backend.pdkLoader import importPDKModule

schlyr = importPDKModule("schLayers")
symlyr = importPDKModule("symLayers")


"""Base class for symbol shapes."""

class symbolShape(QGraphicsItem):
    def __init__(self) -> None:
        super().__init__()
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setAcceptHoverEvents(True)
        self._angle: float = 0.0  # rotation angle
        self._stretch: bool = False
        self._pen = symlyr.defaultPen
        self._draft: bool = False
        self._brush: QBrush = schlyr.draftBrush
        self._flipTuple = (1, 1)


    def __repr__(self) -> str:
        return "symbolShape()"

    @property
    def pen(self):
        return self._pen

    @property
    def brush(self):
        return self._brush

    @brush.setter
    def brush(self, value: QBrush):
        if isinstance(value, QBrush):
            self._brush = value

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value
        self.prepareGeometryChange()
        self.setRotation(value)

    @property
    def stretch(self):
        return self._stretch

    @stretch.setter
    def stretch(self, value: bool):
        if self._stretch != value:
            self._stretch = value
            self.update()

    @property
    def draft(self) -> bool:
        return self._draft

    @draft.setter
    def draft(self, value: bool):
        assert isinstance(value, bool)
        self._draft = value
        # all the child items and their children should be also draft.
        for item in self.childItems():
            item.draft = True

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.setSelected(True)
        if self.scene().editModes.moveItem:
            self.setFlag(QGraphicsItem.ItemIsMovable, True)

        super().mousePressEvent(event)

    def sceneEvent(self, event):
        """
        Do not propagate event if shape needs to keep still.
        """
        if self.scene() and (
                self.scene().editModes.changeOrigin or self.scene().drawMode):
            return False
        else:
            super().sceneEvent(event)
            return True

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedHasChanged and self.scene():
            # Direct z-value calculation without conditional
            self.setZValue(self.zValue() + (20 * value - 10))
        return super().itemChange(change, value)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        super().mouseReleaseEvent(event)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setOpacity(0.75)
        self.setFocus()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        super().hoverLeaveEvent(event)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setOpacity(1)
        self.clearFocus()

    def contextMenuEvent(self, event):
        self.setSelected(True)
        self.scene().itemContextMenu.exec_(event.screenPos())

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


