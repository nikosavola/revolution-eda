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

"""Layout scene I/O mixin: save, load, and export operations."""

import json
import pathlib
from typing import Any, Dict, List, Union

import orjson

import revedaEditor.backend.dataDefinitions as ddef
import revedaEditor.backend.libraryMethods as libm
import revedaEditor.backend.libraryModelView as lmview
import revedaEditor.common.layoutShapes as lshp
import revedaEditor.fileio.exportGDS as gdse
import revedaEditor.fileio.layoutEncoder as layenc
import revedaEditor.fileio.loadJSON as lj
import revedaEditor.gui.fileDialogues as fd
from revedaEditor.backend.pdkLoader import importPDKModule

fabproc = importPDKModule("process")
laylyr = importPDKModule("layoutLayers")
schlyr = importPDKModule("schLayers")


class LayoutSceneIOMixin:
    """Mixin class providing file I/O operations for layoutScene."""

    def saveLayoutCell(self, filePathObj: pathlib.Path) -> None:
        """Save the layout cell to a JSON file."""

        def safeJsonWrite(file_obj, data: list) -> None:
            json.dump(
                data,
                file_obj,
                cls=layenc.layoutEncoder,
                separators=(",", ":"),
                check_circular=False,
            )

        try:
            filePathObj.parent.mkdir(parents=True, exist_ok=True)
            self.itemsRefSet = set(self.items())
            topLevelItems = [
                item
                for item in self.itemsRefSet
                if item.parentItem() is None
                   and isinstance(item, tuple(self.LAYOUT_SHAPES))
            ]
            layoutData = [
                {"viewType": "layout"},
                {"snapGrid": (self.majorGrid, self.snapGrid)},
                *topLevelItems,
            ]

            temp_path = filePathObj.with_suffix(".tmp")
            try:
                with temp_path.open(mode="w", buffering=65536) as f:
                    safeJsonWrite(f, layoutData)
                temp_path.replace(filePathObj)
            finally:
                if temp_path.exists():
                    temp_path.unlink()

            self.logger.info(
                f"Saved layout to {self.editorWindow.cellName}:{self.editorWindow.viewName}"
            )
        except ValueError as e:
            self.logger.error(f"Invalid layout data: {str(e)}")
            raise
        except (IOError, TypeError) as e:
            self.logger.error(f"Failed to save layout to {filePathObj}: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while saving layout: {str(e)}")
            raise

    def _exportCell(
            self, export_dir: pathlib.Path, unit: float, precision: float, dbu: int, format_type: str = "GDS"
    ):
        """Export cell in the specified format (GDS or OAS)."""
        format_upper = format_type.upper()
        file_extension = ".gds" if format_upper == "GDS" else ".oas"
        export_path = export_dir / f"{self.cellName}{file_extension}"

        self.itemsRefSet = set(self.items())
        topLevelItems = [
            item
            for item in self.itemsRefSet
            if item.parentItem() is None
               and isinstance(item, tuple(self.LAYOUT_SHAPES))
        ]
        layoutData = [
            {"viewType": "layout"},
            {"snapGrid": (self.majorGrid, self.snapGrid)},
            *topLevelItems,
        ]

        gdse.exportLayout(
            layoutData,
            self.cellName,
            export_path,
            unit,
            precision,
            dbu,
            format_type=format_upper,
        )
        self.logger.info(f"Exported {format_upper} to {export_path}")

    def exportCellGDS(
            self, export_dir: pathlib.Path, unit: float, precision: float, dbu: int
    ):
        self._exportCell(export_dir, unit, precision, dbu, format_type="GDS")

    def exportCellOAS(
            self, export_dir: pathlib.Path, unit: float, precision: float, dbu: int
    ):
        self._exportCell(export_dir, unit, precision, dbu, format_type="OAS")

    def loadDesign(self, filePathObj: pathlib.Path) -> bool:
        """Load a layout design from a JSON file."""
        try:
            with filePathObj.open(mode="rb") as f:
                decoded_data = orjson.loads(f.read())

            header = decoded_data[0]
            if header.get("viewType") != "layout":
                self.logger.error("Not a layout file")
                return False

            grid_data = decoded_data[1].get("snapGrid", (self.majorGrid, self.snapGrid))
            self.majorGrid, self.snapGrid = grid_data

            items_data = decoded_data[2:]
            self.createLayoutItems(items_data)
            return True

        except (FileNotFoundError, KeyError, json.JSONDecodeError, orjson.JSONDecodeError) as e:
            self.logger.error(f"Error loading layout: {str(e)}")
            return False

    def createLayoutItems(self, decoded_data: List[Dict[str, Any]]) -> None:
        """Create layout items from decoded JSON data."""
        items = lj.createLayoutItems(decoded_data, self.snapGrid)
        for item in items:
            self.addItem(item)
            if isinstance(item, (lshp.layoutInstance, lshp.layoutPcell)):
                self.itemCounter += 1

    def loadSchematicInstances(self, schematicTuple: ddef.viewItemTuple) -> None:
        """Load instances from a schematic view to match in layout."""
        try:
            schematicPath = schematicTuple.viewPath
            if not schematicPath.exists():
                self.logger.warning(f"Schematic file not found: {schematicPath}")
                return

            with schematicPath.open(mode="rb") as f:
                decoded_data = orjson.loads(f.read())

            if not decoded_data:
                return

            header = decoded_data[0]
            if header.get("viewType") != "schematic":
                self.logger.error("Not a schematic file")
                return

            instances = [
                item for item in decoded_data[2:]
                if "inst" in item
            ]

            for sch_inst in instances:
                inst_data = sch_inst["inst"]
                lib_name = inst_data.get("lib", "")
                cell_name = inst_data.get("cell", "")

                viewTuple = self._resolveLayoutView(lib_name, cell_name)
                if viewTuple:
                    self._createLayoutInstanceFromSch(viewTuple, inst_data)

        except Exception as e:
            self.logger.error(f"Error loading schematic instances: {str(e)}")

    def _resolveLayoutView(self, lib_name: str, cell_name: str) -> Union[ddef.viewItemTuple, None]:
        """Resolve a layout view for a given library and cell name."""
        try:
            appMainW = self.editorWindow.appMainW
            libraryDict = appMainW.libraryDict
            libraryModel = appMainW.libraryBrowserCont.libraryModel

            if lib_name not in libraryDict:
                return None

            lib_item = libm.getLibItem(libraryModel, lib_name)
            if lib_item is None:
                return None

            cell_item = libm.getCellItem(lib_item, cell_name)
            if cell_item is None:
                return None

            # Try to find layout view
            for view_name in ["layout", "abstract"]:
                view_item = libm.getViewItem(cell_item, view_name)
                if view_item is not None:
                    view_path = pathlib.Path(
                        libraryDict[lib_name].joinpath(cell_name, view_name + ".json")
                    )
                    return ddef.viewItemTuple(view_item, view_path)

            return None
        except Exception as e:
            self.logger.error(f"Error resolving layout view: {str(e)}")
            return None

    def _createLayoutInstanceFromSch(self, viewTuple: ddef.viewItemTuple, sch_inst: dict) -> bool:
        """Create a layout instance based on schematic instance data."""
        try:
            viewPath = viewTuple.viewPath
            if not viewPath.exists():
                return False

            with viewPath.open(mode="rb") as f:
                decoded_data = orjson.loads(f.read())

            if not decoded_data:
                return False

            items_data = decoded_data[2:]
            items = lj.createLayoutItems(items_data, self.snapGrid)

            if not items:
                return False

            # Determine if it's a pcell
            view_name = viewPath.stem
            lib_name = viewPath.parent.parent.name
            cell_name = viewPath.parent.name

            instance = lshp.layoutInstance(items)
            instance.libraryName = lib_name
            instance.cellName = cell_name
            instance.viewName = view_name
            instance.counter = self.itemCounter
            instance.instanceName = f"I{self.itemCounter}"

            self.addItem(instance)
            self.itemCounter += 1
            return True

        except Exception as e:
            self.logger.error(f"Error creating layout instance: {str(e)}")
            return False
