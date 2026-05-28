#    “Commons Clause” License Condition v1.0
#   #
#    The Software is provided to you by the Licensor under the License, as defined
#    below, subject to the following condition.
#   #
#    Without limiting other conditions in the License, the grant of rights under the
#    License will not include, and the License does not grant to you, the right to
#    Sell the Software.
#   #
#    For purposes of the foregoing, “Sell” means practicing any or all of the rights
#    granted to you under the License to provide to third parties, for a fee or other
#    consideration (including without limitation fees for hosting) a product or service whose value
#    derives, entirely or substantially, from the functionality of the Software. Any
#    license notice or attribution required by the License must also include this
#    Commons Clause License Condition notice.
#   #
#    Software: Revolution EDA
#    License: Mozilla Public License 2.0
#    Licensor: Revolution Semiconductor (Registered in the Netherlands)

from dataclasses import dataclass
from typing import NamedTuple, Union

from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QColor

from revedaEditor.backend import libBackEnd as libb


@dataclass
class edLayer:
    """Defines an editor layer with visual styling and GDS mapping.

    Editor layers control the appearance of shapes in the schematic and symbol
    editors, including pen/brush colors, line styles, z-ordering, and the
    corresponding GDS layer/datatype for export.
    """

    name: str = ""  # edLayer name
    purpose: str = "drawing"  # edLayer purpose
    pcolor: QColor = Qt.black  # pen colour
    pwidth: int = 1  # pen width
    pstyle: Qt.PenStyle = Qt.SolidLine  # pen style
    bcolor: QColor = Qt.transparent  # brush colour
    bstyle: Qt.BrushStyle = Qt.SolidPattern  # brush texture
    z: int = 1  # z-index
    selectable: bool = True  # selectable
    visible: bool = True  # visible
    gdsLayer: int = 0  # gds Layer
    datatype: int = 0  # gds datatype


@dataclass
class layLayer:
    """Defines a layout layer with visual styling, stipple patterns, and GDS mapping.

    Layout layers extend the base layer concept with stipple texture support for
    fill patterns. They map to specific GDS layer/datatype pairs for physical export.
    """

    name: str = "Default"  # edLayer name
    purpose: str = "drawing"  # edLayer purpose
    pcolor: QColor = Qt.black  # pen colour
    pwidth: int = 1  # pen width
    pstyle: Qt.PenStyle = Qt.SolidLine  # pen style
    bcolor: QColor = Qt.transparent  # brush colour
    btexture: str = ""  # brush texture
    z: int = 1  # z-index
    selectable: bool = True  # selectable
    visible: bool = True  # visible
    gdsLayer: int = 0  # gds Layer
    datatype: int = 0  # gds datatype

    @classmethod
    def filterByGDSLayer(
            cls, layer_list, gdsLayer: int, gdsDatatype: int
    ) -> "layLayer":
        for layer in layer_list:
            if layer.gdsLayer == gdsLayer and layer.datatype == gdsDatatype:
                return layer
        return cls()


@dataclass
class editModes:
    """Base state machine for editor interaction modes.

    Only one mode can be active at a time. The `setMode()` method deactivates all
    modes and activates the specified one. Subclasses add domain-specific modes
    for symbol, schematic, and layout editing.
    """

    selectItem: bool
    deleteItem: bool
    moveItem: bool
    constrainedMoveItem: bool
    copyItem: bool
    rotateItem: bool
    changeOrigin: bool
    panView: bool
    zoomView: bool
    stretchItem: bool
    alignItems: bool

    def setMode(self, attribute):
        for key in self.__dict__.keys():
            self.__dict__[key] = False
        self.__dict__[attribute] = True

    def mode(self):
        for key, value in self.__dict__.items():
            if value:
                return key


@dataclass
class symbolModes(editModes):
    """Edit modes for the symbol editor, adding shape drawing operations."""

    drawPin: bool
    drawArc: bool
    drawRect: bool
    drawLine: bool
    addLabel: bool
    drawCircle: bool
    drawPolygon: bool


@dataclass
class schematicModes(editModes):
    """Edit modes for the schematic editor, adding wiring and instance operations."""

    drawPin: bool
    drawWire: bool
    drawBus: bool
    drawText: bool
    addInstance: bool
    nameNet: bool


@dataclass
class layoutModes(editModes):
    """Edit modes for the layout editor, adding physical design operations."""

    drawPath: bool
    drawPin: bool
    drawArc: bool
    drawPolygon: bool
    addLabel: bool
    addVia: bool
    drawRect: bool
    drawLine: bool
    drawCircle: bool
    drawRuler: bool
    addInstance: bool
    cutShape: bool


@dataclass
class selectModes:
    """Base selection filter state machine.

    Controls which types of items are selectable in the editor.
    """

    selectAll: bool

    def setMode(self, attribute):
        for key in self.__dict__.keys():
            self.__dict__[key] = False
        self.__dict__[attribute] = True


@dataclass
class schematicSelectModes(selectModes):
    """Selection filters for schematic items (devices, nets, pins)."""

    selectDevice: bool
    selectNet: bool
    selectPin: bool


@dataclass
class layoutSelectModes(selectModes):
    """Selection filters for layout items (instances, paths, vias, labels, etc.)."""

    selectInstance: bool
    selectPath: bool
    selectVia: bool
    selectLabel: bool
    selectText: bool
    selectPin: bool


# library editor related named tuples
class viewNameTuple(NamedTuple):
    """Identifies a view by its library, cell, and view names (string-based)."""

    libraryName: str
    cellName: str
    viewName: str


class cellTuple(NamedTuple):
    """Identifies a cell by its library and cell names."""

    libraryName: str
    cellName: str


class viewItemTuple(NamedTuple):
    """References actual Qt model items for a library/cell/view triple."""

    libraryItem: libb.libraryItem
    cellItem: libb.cellItem
    viewItem: libb.viewItem

    def convertToViewNameTuple(self) -> viewNameTuple:
        return viewNameTuple(
            libraryName=self.libraryItem.libraryName,
            cellName=self.cellItem.cellName,
            viewName=self.viewItem.viewName
        )


class layoutPinTuple(NamedTuple):
    """Defines a layout pin with name, direction, type, and layer assignment."""

    pinName: str
    pinDir: str
    pinType: str
    pinLayer: layLayer


class layoutLabelTuple(NamedTuple):
    """Defines a layout label with text, font, alignment, and layer properties."""

    labelText: str
    fontFamily: str
    fontStyle: str
    fontHeight: str
    labelAlign: str
    labelOrient: str
    labelLayer: str


class rulerTuple(NamedTuple):
    """Stores ruler measurement data: anchor point, line segment, and text label."""

    point: Union[QPoint, QPointF]
    line: tuple
    text: str


# # pdk related classes and namedtuples
# # this tuple defines the minimum dimensions of a via
# # This can be extended to define the maximum dimensions


# used in PDK
class viaDefTuple(NamedTuple):
    """PDK via definition with dimension and spacing constraints."""

    name: str
    layer: layLayer
    type: str
    minWidth: float
    maxWidth: float
    minHeight: float
    maxHeight: float
    minSpacing: float
    maxSpacing: float


# Used to define the via prototype
class singleViaTuple(NamedTuple):
    """A single via instance with its definition and specific dimensions."""

    viaDefTuple: viaDefTuple
    width: float
    height: float


# both single vias and vias arrays are defined by this
class arrayViaTuple(NamedTuple):
    """An array of vias with spacing and repetition counts in x and y."""

    singleViaTuple: singleViaTuple
    xs: float
    ys: float
    xnum: int
    ynum: int


# rectangle coordinates tuple
class rectCoords(NamedTuple):
    """Rectangle defined by top-left corner coordinates and dimensions."""

    left: float
    top: float
    w: float
    h: float


class layoutPathDefTuple(NamedTuple):
    """PDK path/routing definition with width, length, and spacing constraints."""

    name: str
    layer: layLayer
    type: str
    minWidth: float
    maxWidth: float
    minLength: float
    maxLength: float
    minSpacing: float
    maxSpacing: float


class layoutPathTuple(NamedTuple):
    """A layout path instance with specific mode, width, and end extensions."""

    name: str
    layer: layLayer
    pathMode: int
    width: float
    startExtend: float
    endExtend: float
