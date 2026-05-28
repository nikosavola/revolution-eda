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

"""Layout scene properties mixin: property dialogs and editing."""

import inspect

from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QDialog

import revedaEditor.backend.dataDefinitions as ddef
import revedaEditor.common.layoutShapes as lshp
import revedaEditor.gui.layoutDialogues as ldlg
import revedaEditor.gui.propertyDialogues as pdlg
from revedaEditor.backend.pdkLoader import importPDKModule

fabproc = importPDKModule("process")
laylyr = importPDKModule("layoutLayers")
pcells = importPDKModule("pcells")


class LayoutScenePropertiesMixin:
    """Mixin class providing property dialog operations for layoutScene."""

    def viewObjProperties(self):
        """View and edit properties of selected items."""
        selectedItems = [
            item for item in self.selectedItems()
            if item.parentItem() is None
        ]
        for item in selectedItems:
            if isinstance(item, lshp.layoutRect):
                self.layoutRectProperties(item)
            elif isinstance(item, lshp.layoutPath):
                self.layoutPathProperties(item)
            elif isinstance(item, lshp.layoutViaArray):
                self.layoutViaProperties(item)
            elif isinstance(item, lshp.layoutPin):
                self.layoutPinProperties(item)
            elif isinstance(item, lshp.layoutLabel):
                self.layoutLabelProperties(item)
            elif isinstance(item, lshp.layoutPolygon):
                self.layoutPolygonProperties(item)
            elif isinstance(item, lshp.layoutPcell):
                self.layoutInstanceProperties(item, True)
            elif isinstance(item, lshp.layoutInstance):
                self.layoutInstanceProperties(item, False)

    def layoutPolygonProperties(self, item):
        """Show properties dialog for a polygon."""
        dlg = ldlg.layoutPolygonProperties(self.editorWindow, item)
        if dlg.exec() == QDialog.Accepted:
            item.prepareGeometryChange()
            item.layer = laylyr.pdkAllLayers[
                dlg.layerCB.currentIndex()
            ]
            item._definePensBrushes(item.layer)
            item.update()

    def layoutRectProperties(self, item):
        """Show properties dialog for a rectangle."""
        dlg = ldlg.layoutRectProperties(self.editorWindow, item)
        if dlg.exec() == QDialog.Accepted:
            item.prepareGeometryChange()
            left = self.snapToBase(float(dlg.rectLeftLine.text()) * self._scale, self.snapGrid)
            top = self.snapToBase(float(dlg.rectTopLine.text()) * self._scale, self.snapGrid)
            width = self.snapToBase(float(dlg.rectWidthLine.text()) * self._scale, self.snapGrid)
            height = self.snapToBase(float(dlg.rectHeightLine.text()) * self._scale, self.snapGrid)
            item.rect.setLeft(left)
            item.rect.setTop(top)
            item.rect.setWidth(width)
            item.rect.setHeight(height)
            item.layer = laylyr.pdkAllLayers[dlg.layerCB.currentIndex()]
            item._definePensBrushes(item.layer)
            item.update()

    def layoutViaProperties(self, item):
        """Show properties dialog for a via array."""
        dlg = ldlg.layoutViaProperties(self.editorWindow, item)
        if dlg.exec() == QDialog.Accepted:
            item.prepareGeometryChange()
            # Recreate via array with new properties
            startX = self.snapToBase(
                float(dlg.xLocationEdit.text()) * self._scale, self.snapGrid
            )
            startY = self.snapToBase(
                float(dlg.yLocationEdit.text()) * self._scale, self.snapGrid
            )
            newStart = QPoint(startX, startY)
            xnum = int(dlg.xNumEdit.text())
            ynum = int(dlg.yNumEdit.text())
            xs = self.snapToBase(
                float(dlg.xSpacingEdit.text()) * self._scale, self.snapGrid
            )
            ys = self.snapToBase(
                float(dlg.ySpacingEdit.text()) * self._scale, self.snapGrid
            )
            # Get selected via definition
            viaDefIndex = dlg.viaCB.currentIndex()
            viaDef = fabproc.processVias[viaDefIndex]
            width = self.snapToBase(
                float(dlg.widthEdit.text()) * self._scale, self.snapGrid
            )
            height = self.snapToBase(
                float(dlg.heightEdit.text()) * self._scale, self.snapGrid
            )
            # Create prototype via
            protoVia = lshp.layoutVia(newStart, viaDef, width, height)
            # Create new via array
            newViaArray = lshp.layoutViaArray(
                newStart, protoVia, xs, ys, xnum, ynum
            )
            # Copy position
            newViaArray.setPos(item.pos())
            # Replace the item
            self.removeItem(item)
            self.addItem(newViaArray)

    def layoutPathProperties(self, item):
        """Show properties dialog for a path."""
        dlg = ldlg.layoutPathProperties(self.editorWindow, item)
        if dlg.exec() == QDialog.Accepted:
            item.prepareGeometryChange()
            item.layer = laylyr.pdkAllLayers[dlg.layerCB.currentIndex()]
            item.width = self.snapToBase(
                float(dlg.pathWidthEdit.text()) * self._scale, self.snapGrid
            )
            item.startExtend = self.snapToBase(
                float(dlg.startExtendEdit.text()) * self._scale, self.snapGrid
            )
            item.endExtend = self.snapToBase(
                float(dlg.endExtendEdit.text()) * self._scale, self.snapGrid
            )
            item.name = dlg.pathNameEdit.text().strip()
            item._definePensBrushes(item.layer)
            item.update()

    def layoutLabelProperties(self, item):
        """Show properties dialog for a label."""
        dlg = ldlg.layoutLabelProperties(self.editorWindow, item)
        if dlg.exec() == QDialog.Accepted:
            item.prepareGeometryChange()
            item.labelText = dlg.labelTextEdit.text().strip()
            item.fontFamily = dlg.familyCB.currentText()
            item.fontStyle = dlg.fontStyleCB.currentText()
            item.fontHeight = dlg.fontHeightCB.currentText()
            item._labelAlign = dlg.labelAlignCB.currentText()
            item._labelOrient = dlg.labelOrientCB.currentText()
            item.layer = laylyr.pdkAllLayers[dlg.layerCB.currentIndex()]
            item._definePensBrushes(item.layer)
            item.setOrient()
            item.update()

    def layoutPinProperties(self, item):
        """Show properties dialog for a pin."""
        dlg = ldlg.layoutPinProperties(self.editorWindow, item)
        if dlg.exec() == QDialog.Accepted:
            item.prepareGeometryChange()
            item.pinName = dlg.pinNameEdit.text().strip()
            item.pinDir = dlg.pinDirCB.currentText()
            item.pinType = dlg.pinTypeCB.currentText()
            item.layer = laylyr.pdkAllLayers[dlg.layerCB.currentIndex()]
            item._definePensBrushes(item.layer)
            item.update()

    def layoutInstanceProperties(
            self, item, isPcell: bool = False
    ):
        """Show properties dialog for an instance."""
        dlg = ldlg.layoutInstanceProperties(self.editorWindow, item, isPcell)
        if dlg.exec() == QDialog.Accepted:
            item.instanceName = dlg.instanceNameEdit.text().strip()
            if isPcell and hasattr(dlg, 'paramFields'):
                # Handle pcell parameter changes
                newParams = self.extractPcellInstanceParameters(item)
                self.changePcellParameterFields(item, dlg, newParams)

    def changePcellParameterFields(
            self, instance, dlg, newParams: dict
    ):
        """Update pcell instance with new parameters."""
        try:
            if not hasattr(pcells, instance.cellName):
                return

            pcellClass = getattr(pcells, instance.cellName)
            # Regenerate pcell with new parameters
            newShapes = pcellClass(**newParams).shapes
            if newShapes:
                instance.shapes = newShapes
                instance.update()
        except Exception as e:
            self.logger.error(f"Error updating pcell parameters: {str(e)}")

    def extractPcellInstanceParameters(self, instance: lshp.layoutPcell) -> dict:
        """Extract parameters from a pcell instance."""
        params = {}
        if hasattr(pcells, instance.cellName):
            pcellClass = getattr(pcells, instance.cellName)
            if hasattr(pcellClass, '__init__'):
                sig = inspect.signature(pcellClass.__init__)
                for name, param in sig.parameters.items():
                    if name == 'self':
                        continue
                    if param.default is not inspect.Parameter.empty:
                        params[name] = param.default
        return params
