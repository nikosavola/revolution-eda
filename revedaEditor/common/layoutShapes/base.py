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

"""Base classes for layout shapes: textureCache and layoutShape."""

from pathlib import Path
from typing import Tuple, Union

import numpy as np
from PySide6.QtCore import (
    QPoint,
    QPointF,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QImage,
    QPainter,
    QPen,
    QPixmap,
    QTransform,
)
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsSceneHoverEvent,
    QGraphicsSceneMouseEvent,
)

import revedaEditor.backend.dataDefinitions as ddef
from revedaEditor.backend.pdkLoader import importPDKModule


class textureCache:
    _file_content_cache = {}
    _pixmap_cache = {}

    @classmethod
    def readFileContent(cls, filePath):
        if filePath not in cls._file_content_cache:
            with open(filePath, "r") as file:
                cls._file_content_cache[filePath] = file.read()
        return cls._file_content_cache[filePath]

    @classmethod
    def createImage(cls, filePath: Path, color: QColor, scale: int = 1) -> QImage:
        content = cls.readFileContent(str(filePath))

        # Use numpy's loadtxt for faster parsing of text data
        data = np.loadtxt(content.splitlines(), dtype=np.uint8)

        # Scale up the pattern by repeating each pixel
        data_scaled = np.repeat(np.repeat(data, scale, axis=0), scale, axis=1)

        height, width = data_scaled.shape

        # Create QImage with Format_ARGB32 (not premultiplied)
        image = QImage(width, height, QImage.Format.Format_ARGB32)
        # Fill with transparent pixels first
        image.fill(Qt.transparent)

        # Create painter to draw on the image
        painter = QPainter(image)
        if not painter.isActive():  # Add this check
            return image
        painter.setPen(Qt.NoPen)
        # Create semi-transparent color (50% opacity)
        transparent_color = QColor(color)
        transparent_color.setAlpha(230)  # 220 is 90% opacity (range is 0-255)
        painter.setBrush(QBrush(transparent_color))

        # Draw solid rectangles for each pixel that should be colored
        for i in range(height):
            for j in range(width):
                if data_scaled[i, j] == 1:  # Draw colored pixel
                    painter.drawRect(j, i, 1, 1)

        painter.end()
        return image

    @classmethod
    def getCachedPixmap(cls, texturePath, color):
        cache_key = (str(texturePath), color.name())
        if cache_key not in cls._pixmap_cache:
            image = cls.createImage(texturePath, color, 1)
            pixmap = QPixmap.fromImage(image)
            cls._pixmap_cache[cache_key] = pixmap
        return cls._pixmap_cache[cache_key]

    @classmethod
    def clearCaches(cls):
        cls._file_content_cache.clear()
        cls._pixmap_cache.clear()


class layoutShape(QGraphicsItem):
    # Class-level color cache
    _color_cache = {}
    # Class-level pen/brush lookup table
    _pen_brush_cache = {}

    def __init__(self) -> None:
        super().__init__()

        # Batch flag operations for better performance
        flags = (
                QGraphicsItem.ItemIsSelectable
                | QGraphicsItem.ItemSendsGeometryChanges
                | QGraphicsItem.ItemIsFocusable
                | QGraphicsItem.ItemUsesExtendedStyleOption
        )
        self.setFlags(flags)

        # Single method calls
        self.setAcceptHoverEvents(True)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        # Direct attribute initialization (faster than individual assignments)
        self._pen = self._brush = None
        self._angle = 0
        self._stretch = False
        self._offset = QPoint(0, 0)
        self._flipTuple = (1, 1)
        self._transformedBrush = self._lastScale = None

    @classmethod
    def _get_cached_color(cls, color_name):
        if color_name not in cls._color_cache:
            cls._color_cache[color_name] = QColor(color_name)
        return cls._color_cache[color_name]

    def __repr__(self) -> str:
        return "layoutShape()"

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedHasChanged and self.scene():
            # Direct z-value calculation without conditional
            self.setZValue(self.zValue() + (20 * value - 10))
        return super().itemChange(change, value)

    def _definePensBrushes(self, layer):
        # Create cache key from layer properties
        cache_key = (
            layer.name,
            layer.purpose,
            layer.pcolor.name(),
            layer.pwidth,
            layer.pstyle,
            layer.bcolor.name(),
            layer.btexture,
        )

        if cache_key not in self._pen_brush_cache:
            # Import PDK module when needed to avoid circular imports
            laylyr = importPDKModule("layoutLayers")
            # Create objects only once per unique layer configuration
            texturePath = Path(laylyr.__file__).parent.joinpath(layer.btexture)
            _pixmap = textureCache.getCachedPixmap(texturePath, layer.bcolor)

            yellow = self._get_cached_color("yellow")
            red = self._get_cached_color("red")

            self._pen_brush_cache[cache_key] = {
                "pen": QPen(layer.pcolor, layer.pwidth, layer.pstyle),
                "brush": QBrush(layer.bcolor, _pixmap),
                "selectedPen": QPen(yellow, layer.pwidth, Qt.DashLine),
                "selectedBrush": QBrush(yellow, _pixmap),
                "stretchPen": QPen(red, layer.pwidth, Qt.SolidLine),
                "stretchBrush": QBrush(red, _pixmap),
            }

        # Assign from cache
        cached = self._pen_brush_cache[cache_key]
        self._pen = cached["pen"]
        self._brush = cached["brush"]
        self._selectedPen = cached["selectedPen"]
        self._selectedPen.setCosmetic(True)
        self._selectedBrush = cached["selectedBrush"]
        self._stretchPen = cached["stretchPen"]
        self._stretchPen.setCosmetic(True)
        self._stretchBrush = cached["stretchBrush"]

    def _updateTransformedBrush(self, brush: QBrush, scale: float):
        """Update transformed brush only when needed"""
        rounded_scale = max(round(scale, 2), 0.01)  # Prevent division by zero

        if self._transformedBrush is None or self._lastScale != rounded_scale:
            if self._transformedBrush is None:
                self._transformedBrush = QBrush(brush)
            else:
                self._transformedBrush = brush

            transform = QTransform().scale(1 / rounded_scale, 1 / rounded_scale)
            self._transformedBrush.setTransform(transform)
            self._lastScale = rounded_scale

    @property
    def pen(self):
        return self._pen

    @pen.setter
    def pen(self, value: QPen):
        if isinstance(value, QPen):
            self._pen = value

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
        self._stretch = value

    @property
    def view(self):
        if self.scene():
            return self.scene().views()[0]
        else:
            return None

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value: Union[QPoint | QPointF]):
        self._offset = value

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.setSelected(True)
        if self.scene() and self.scene().editModes.moveItem:
            self.setFlag(QGraphicsItem.ItemIsMovable, True)

        super().mousePressEvent(event)

    def sceneEvent(self, event):
        """
        Do not propagate event if shape needs to keep still.
        """
        if self.scene() and (
                self.scene().editModes.changeOrigin or self.scene().drawMode
        ):
            return False
        else:
            super().sceneEvent(event)
            return True

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseReleaseEvent(event)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.setCursor(Qt.ArrowCursor)
        self.setOpacity(0.75)
        self.setFocus()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        super().hoverLeaveEvent(event)
        self.setCursor(Qt.CrossCursor)
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
        # Early exit if no change
        if self._flipTuple == flipState:
            return

        # Cache center calculation
        if not hasattr(self, "_cached_center"):
            self._cached_center = self.boundingRect().center()
        center = self._cached_center

        # Direct transform creation is faster than modifying existing
        cx, cy = center.x(), center.y()
        sx, sy = flipState

        transform = QTransform(sx, 0, 0, sy, cx - sx * cx, cy - sy * cy)
        self.setTransform(transform)
        self._flipTuple = flipState

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, value: ddef.layLayer):
        self.prepareGeometryChange()
        self._layer = value
        self._definePensBrushes(self._layer)
