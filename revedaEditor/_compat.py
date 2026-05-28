"""
Backward compatibility aliases for renamed classes.

This module provides old (non-PEP 8) names as aliases to the new
PascalCase class names for a smooth transition period.

Usage:
    from revedaEditor._compat import editor_scene  # deprecated
    # Prefer: from revedaEditor.scenes.editor_scene import EditorScene
"""

from defaultPDK.callbacks import (
    BaseInst,
    Dnwpw,
    Ind,
    Npolyf_u,
    Res,
)

baseInst = BaseInst
dnwpw = Dnwpw
ind = Ind
npolyf_u = Npolyf_u
res = Res

from defaultPDK.pcells import (
    Nmos,
    Pmos,
)

nmos = Nmos
pmos = Pmos

from plugins.aiTerminal.ai_terminal import (
    AiTerminal,
)

aiTerminal = AiTerminal

from reveda import (
    RevedaApp,
)

revedaApp = RevedaApp

from revedaEditor.backend.data_definitions import (
    ArrayViaTuple,
    CellTuple,
    EdLayer,
    EditModes,
    LayLayer,
    LayoutLabelTuple,
    LayoutModes,
    LayoutPathDefTuple,
    LayoutPathTuple,
    LayoutPinTuple,
    LayoutSelectModes,
    RectCoords,
    RulerTuple,
    SchematicModes,
    SchematicSelectModes,
    SelectModes,
    SingleViaTuple,
    SymbolModes,
    ViaDefTuple,
    ViewItemTuple,
    ViewNameTuple,
)

arrayViaTuple = ArrayViaTuple
cellTuple = CellTuple
edLayer = EdLayer
editModes = EditModes
layLayer = LayLayer
layoutLabelTuple = LayoutLabelTuple
layoutModes = LayoutModes
layoutPathDefTuple = LayoutPathDefTuple
layoutPathTuple = LayoutPathTuple
layoutPinTuple = LayoutPinTuple
layoutSelectModes = LayoutSelectModes
rectCoords = RectCoords
rulerTuple = RulerTuple
schematicModes = SchematicModes
schematicSelectModes = SchematicSelectModes
selectModes = SelectModes
singleViaTuple = SingleViaTuple
symbolModes = SymbolModes
viaDefTuple = ViaDefTuple
viewItemTuple = ViewItemTuple
viewNameTuple = ViewNameTuple

from revedaEditor.backend.edit_functions import (
    BoldLabel,
    LongLineEdit,
    ShortLineEdit,
)

boldLabel = BoldLabel
longLineEdit = LongLineEdit
shortLineEdit = ShortLineEdit

from revedaEditor.backend.hdl_back_end import (
    SpiceC,
    VerilogaC,
)

spiceC = SpiceC
verilogaC = VerilogaC

from revedaEditor.backend.lib_back_end import (
    CellItem,
    LibraryItem,
    ViewItem,
)

cellItem = CellItem
libraryItem = LibraryItem
viewItem = ViewItem

from revedaEditor.backend.library_model_view import (
    DesignLibrariesColumnView,
    DesignLibrariesModel,
    DesignLibrariesTreeView,
    LayoutViewsModel,
    LibraryCheckListView,
    SchematicViewsModel,
    SymbolViewsModel,
)

designLibrariesColumnView = DesignLibrariesColumnView
designLibrariesModel = DesignLibrariesModel
designLibrariesTreeView = DesignLibrariesTreeView
layoutViewsModel = LayoutViewsModel
libraryCheckListView = LibraryCheckListView
schematicViewsModel = SchematicViewsModel
symbolViewsModel = SymbolViewsModel

from revedaEditor.backend.pdk_loader import (
    PdkConfig,
)

pdkConfig = PdkConfig

from revedaEditor.backend.plugins_loader import (
    PluginsLoader,
)

pluginsLoader = PluginsLoader

from revedaEditor.backend.start_thread import (
    StartThread,
    WorkerSignals,
)

startThread = StartThread
workerSignals = WorkerSignals

from revedaEditor.backend.undo_stack import (
    AddDeleteNetUndo,
    AddDeleteShapeUndo,
    AddDeleteShapesUndo,
    AddShapeUndo,
    AddShapesUndo,
    DeleteShapeUndo,
    DeleteShapesUndo,
    MoveShapeUndo,
    UndoGroupMove,
    UndoMoveByCommand,
    UndoRotateShape,
    UndoStack,
    UpdateSymUndo,
)

addDeleteNetUndo = AddDeleteNetUndo
addDeleteShapeUndo = AddDeleteShapeUndo
addDeleteShapesUndo = AddDeleteShapesUndo
addShapeUndo = AddShapeUndo
addShapesUndo = AddShapesUndo
deleteShapeUndo = DeleteShapeUndo
deleteShapesUndo = DeleteShapesUndo
moveShapeUndo = MoveShapeUndo
undoGroupMove = UndoGroupMove
undoMoveByCommand = UndoMoveByCommand
undoRotateShape = UndoRotateShape
undoStack = UndoStack
updateSymUndo = UpdateSymUndo

from revedaEditor.common.labels import (
    SymbolLabel,
)

symbolLabel = SymbolLabel

from revedaEditor.common.layout_shapes import (
    LayoutInstance,
    LayoutLabel,
    LayoutLine,
    LayoutPath,
    LayoutPcell,
    LayoutPin,
    LayoutPolygon,
    LayoutRect,
    LayoutRuler,
    LayoutShape,
    LayoutVia,
    LayoutViaArray,
    TextureCache,
)

layoutInstance = LayoutInstance
layoutLabel = LayoutLabel
layoutLine = LayoutLine
layoutPath = LayoutPath
layoutPcell = LayoutPcell
layoutPin = LayoutPin
layoutPolygon = LayoutPolygon
layoutRect = LayoutRect
layoutRuler = LayoutRuler
layoutShape = LayoutShape
layoutVia = LayoutVia
layoutViaArray = LayoutViaArray
textureCache = TextureCache

from revedaEditor.common.net import (
    GuideLine,
    NetAnnotation,
    NetFlightLine,
    NetName,
    NetNameStrengthEnum,
    SchematicNet,
)

guideLine = GuideLine
netAnnotation = NetAnnotation
netFlightLine = NetFlightLine
netName = NetName
netNameStrengthEnum = NetNameStrengthEnum
schematicNet = SchematicNet

from revedaEditor.common.shapes import (
    AlignLine,
    PinNetIndexTuple,
    SchematicPin,
    SchematicPinPolygon,
    SchematicSymbol,
    SymbolArc,
    SymbolCircle,
    SymbolLine,
    SymbolPin,
    SymbolPolygon,
    SymbolRectangle,
    SymbolShape,
    Text,
)

alignLine = AlignLine
pinNetIndexTuple = PinNetIndexTuple
schematicPin = SchematicPin
schematicPinPolygon = SchematicPinPolygon
schematicSymbol = SchematicSymbol
symbolArc = SymbolArc
symbolCircle = SymbolCircle
symbolLine = SymbolLine
symbolPin = SymbolPin
symbolPolygon = SymbolPolygon
symbolRectangle = SymbolRectangle
symbolShape = SymbolShape
text = Text

from revedaEditor.fileio.export_gds import (
    GdsExporter,
)

gdsExporter = GdsExporter

from revedaEditor.fileio.extracted_schematic import (
    KlayoutSchematicGenerator,
)

klayoutSchematicGenerator = KlayoutSchematicGenerator

from revedaEditor.fileio.import_gds import (
    GdsImporter,
)

gdsImporter = GdsImporter

from revedaEditor.fileio.import_xschem_sym import (
    ImportXschemSym,
)

import_xschem_sym = ImportXschemSym

from revedaEditor.fileio.layout_encoder import (
    GdsImportEncoder,
    LayoutEncoder,
)

gdsImportEncoder = GdsImportEncoder
layoutEncoder = LayoutEncoder

from revedaEditor.fileio.load_json import (
    LayoutItems,
    SchematicItems,
    SymbolItems,
)

layoutItems = LayoutItems
schematicItems = SchematicItems
symbolItems = SymbolItems

from revedaEditor.fileio.schematic_encoder import (
    SchematicEncoder,
)

schematicEncoder = SchematicEncoder

from revedaEditor.fileio.symbol_encoder import (
    SymbolAttribute,
    SymbolEncoder,
)

symbolAttribute = SymbolAttribute
symbolEncoder = SymbolEncoder

from revedaEditor.gui.align_items import (
    AlignItemsDialogue,
)

alignItemsDialogue = AlignItemsDialogue

from revedaEditor.gui.config_editor import (
    ConfigEditor,
    ConfigEditorContainer,
    ConfigModel,
    ConfigTable,
)

configEditor = ConfigEditor
configEditorContainer = ConfigEditorContainer
configModel = ConfigModel
configTable = ConfigTable

from revedaEditor.gui.editor_views import (
    EditorView,
    LayoutView,
    SchematicView,
    SymbolView,
)

editorView = EditorView
layoutView = LayoutView
schematicView = SchematicView
symbolView = SymbolView

from revedaEditor.gui.editor_window import (
    EditorContainer,
    EditorWindow,
)

editorContainer = EditorContainer
editorWindow = EditorWindow

from revedaEditor.gui.file_dialogues import (
    AppProperties,
    CloseLibDialog,
    CopyCellDialog,
    CopyViewDialog,
    CreateCellDialog,
    CreateConfigViewDialogue,
    DeleteCellDialog,
    DeleteSymbolDialog,
    FileInfoDialogue,
    GdsExportDialogue,
    GdsImportDialogue,
    GoDownHierDialogue,
    ImportCellDialogue,
    ImportSpiceCellDialogue,
    ImportVerilogaCellDialogue,
    KlayoutLaypImportDialogue,
    KlayoutLaytImportDialogue,
    LayoutExportDialogue,
    LibraryPathEditorDialog,
    LibraryPathsModel,
    LibraryPathsTableView,
    NetlistExportDialogue,
    NewCellViewDialog,
    OasExportDialogue,
    RenameCellDialog,
    RenameLibDialog,
    RenameViewDialog,
    SelectCellViewDialog,
    XschemSymIimportDialogue,
)

appProperties = AppProperties
closeLibDialog = CloseLibDialog
copyCellDialog = CopyCellDialog
copyViewDialog = CopyViewDialog
createCellDialog = CreateCellDialog
createConfigViewDialogue = CreateConfigViewDialogue
deleteCellDialog = DeleteCellDialog
deleteSymbolDialog = DeleteSymbolDialog
fileInfoDialogue = FileInfoDialogue
gdsExportDialogue = GdsExportDialogue
gdsImportDialogue = GdsImportDialogue
goDownHierDialogue = GoDownHierDialogue
importCellDialogue = ImportCellDialogue
importSpiceCellDialogue = ImportSpiceCellDialogue
importVerilogaCellDialogue = ImportVerilogaCellDialogue
klayoutLaypImportDialogue = KlayoutLaypImportDialogue
klayoutLaytImportDialogue = KlayoutLaytImportDialogue
layoutExportDialogue = LayoutExportDialogue
libraryPathEditorDialog = LibraryPathEditorDialog
libraryPathsModel = LibraryPathsModel
libraryPathsTableView = LibraryPathsTableView
netlistExportDialogue = NetlistExportDialogue
newCellViewDialog = NewCellViewDialog
oasExportDialogue = OasExportDialogue
renameCellDialog = RenameCellDialog
renameLibDialog = RenameLibDialog
renameViewDialog = RenameViewDialog
selectCellViewDialog = SelectCellViewDialog
xschemSymIimportDialogue = XschemSymIimportDialogue

from revedaEditor.gui.help_browser import (
    AboutDialog,
    HelpBrowser,
    LicenseDialog,
)

aboutDialog = AboutDialog
helpBrowser = HelpBrowser
licenseDialog = LicenseDialog

from revedaEditor.gui.layout_dialogues import (
    CreateLayoutLabelDialog,
    CreateLayoutPinDialog,
    CreateLayoutViaDialog,
    CreatePathDialogue,
    DrcErrorsDialogue,
    FormDictionary,
    LayoutInstanceDialogue,
    LayoutInstancePropertiesDialogue,
    LayoutLabelProperties,
    LayoutPathPropertiesDialog,
    LayoutPinProperties,
    LayoutPolygonProperties,
    LayoutRectProperties,
    LayoutViaProperties,
    PcellLinkDialogue,
)

createLayoutLabelDialog = CreateLayoutLabelDialog
createLayoutPinDialog = CreateLayoutPinDialog
createLayoutViaDialog = CreateLayoutViaDialog
createPathDialogue = CreatePathDialogue
drcErrorsDialogue = DrcErrorsDialogue
formDictionary = FormDictionary
layoutInstanceDialogue = LayoutInstanceDialogue
layoutInstancePropertiesDialogue = LayoutInstancePropertiesDialogue
layoutLabelProperties = LayoutLabelProperties
layoutPathPropertiesDialog = LayoutPathPropertiesDialog
layoutPinProperties = LayoutPinProperties
layoutPolygonProperties = LayoutPolygonProperties
layoutRectProperties = LayoutRectProperties
layoutViaProperties = LayoutViaProperties
pcellLinkDialogue = PcellLinkDialogue

from revedaEditor.gui.layout_editor import (
    LayoutContainer,
    LayoutEditor,
    LswWindow,
)

layoutContainer = LayoutContainer
layoutEditor = LayoutEditor
lswWindow = LswWindow

from revedaEditor.gui.library_browser import (
    LibraryBrowser,
    LibraryBrowserContainer,
    LibraryListView,
)

libraryBrowser = LibraryBrowser
libraryBrowserContainer = LibraryBrowserContainer
libraryListView = LibraryListView

from revedaEditor.gui.lsw import (
    LayerDataModel,
    LayerViewTable,
)

layerDataModel = LayerDataModel
layerViewTable = LayerViewTable

from revedaEditor.gui.lvs_results import (
    LvsResultsDialogue,
)

lvsResultsDialogue = LvsResultsDialogue

from revedaEditor.gui.property_dialogues import (
    ArcPropertyDialog,
    CirclePropertyDialog,
    CreatePinDialog,
    CreateSchematicPinDialog,
    CreateSymbolLabelDialog,
    DisplayConfigDialog,
    InstanceProperties,
    LabelPropertyDialog,
    LayoutDisplayConfigDialog,
    LinePropertyDialog,
    MoveByDialogue,
    NetNameDialog,
    NetProperties,
    NoteTextEdit,
    PinPropertyDialog,
    PointsTableWidget,
    RectPropertyDialog,
    SchematicPinPropertiesDialog,
    SelectConfigDialogue,
    SymbolCreateDialog,
    SymbolLabelsDialogue,
    SymbolNameDialog,
    SymbolPolygonProperties,
)

arcPropertyDialog = ArcPropertyDialog
circlePropertyDialog = CirclePropertyDialog
createPinDialog = CreatePinDialog
createSchematicPinDialog = CreateSchematicPinDialog
createSymbolLabelDialog = CreateSymbolLabelDialog
displayConfigDialog = DisplayConfigDialog
instanceProperties = InstanceProperties
labelPropertyDialog = LabelPropertyDialog
layoutDisplayConfigDialog = LayoutDisplayConfigDialog
linePropertyDialog = LinePropertyDialog
moveByDialogue = MoveByDialogue
netNameDialog = NetNameDialog
netProperties = NetProperties
noteTextEdit = NoteTextEdit
pinPropertyDialog = PinPropertyDialog
pointsTableWidget = PointsTableWidget
rectPropertyDialog = RectPropertyDialog
schematicPinPropertiesDialog = SchematicPinPropertiesDialog
selectConfigDialogue = SelectConfigDialogue
symbolCreateDialog = SymbolCreateDialog
symbolLabelsDialogue = SymbolLabelsDialogue
symbolNameDialog = SymbolNameDialog
symbolPolygonProperties = SymbolPolygonProperties

from revedaEditor.gui.python_console import (
    PythonConsole,
)

pythonConsole = PythonConsole

from revedaEditor.gui.reveda_main import (
    MainwContainer,
)

mainwContainer = MainwContainer

from revedaEditor.gui.schematic_editor import (
    SchematicContainer,
    SchematicEditor,
)

schematicContainer = SchematicContainer
schematicEditor = SchematicEditor

from revedaEditor.gui.stipple_editor import (
    StippleEditor,
    StippleScene,
    StippleView,
)

stippleEditor = StippleEditor
stippleScene = StippleScene
stippleView = StippleView

from revedaEditor.gui.symbol_editor import (
    SymbolContainer,
    SymbolEditor,
)

symbolContainer = SymbolContainer
symbolEditor = SymbolEditor

from revedaEditor.gui.text_editor import (
    JsonEditor,
    SpiceEditor,
    TextEditor,
    VerilogaEditor,
)

jsonEditor = JsonEditor
spiceEditor = SpiceEditor
textEditor = TextEditor
verilogaEditor = VerilogaEditor

from revedaEditor.gui.tools_dialogues import (
    FindProjectEditors,
)

findProjectEditors = FindProjectEditors

from revedaEditor.gui.util_dialogues import (
    RevedaPrintDialog,
)

revedaPrintDialog = RevedaPrintDialog

from revedaEditor.netlisting.spectre_netlist import (
    SpectreNetlist,
)

spectreNetlist = SpectreNetlist

from revedaEditor.netlisting.xyce_netlist import (
    XyceNetlist,
)

xyceNetlist = XyceNetlist

from revedaEditor.scenes.editor_scene import (
    EditorScene,
)

editorScene = EditorScene

from revedaEditor.scenes.layout_scene import (
    LayoutScene,
)

layoutScene = LayoutScene

from revedaEditor.scenes.schematic_scene import (
    SchematicScene,
)

schematicScene = SchematicScene

from revedaEditor.scenes.symbol_scene import (
    SymbolScene,
)

symbolScene = SymbolScene

