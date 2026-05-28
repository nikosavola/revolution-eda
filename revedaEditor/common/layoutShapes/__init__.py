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

"""
Layout shapes package.

This package provides all layout shape primitives for the layout editor.
All classes are re-exported here for backward compatibility with:
    import revedaEditor.common.layoutShapes as lshp
"""

from revedaEditor.common.layoutShapes.base import textureCache, layoutShape
from revedaEditor.common.layoutShapes.rectangles import layoutRect
from revedaEditor.common.layoutShapes.instances import layoutInstance, layoutPcell
from revedaEditor.common.layoutShapes.paths import layoutLine, layoutPath, layoutRuler, alignLine
from revedaEditor.common.layoutShapes.labels import layoutLabel, layoutPin
from revedaEditor.common.layoutShapes.vias import layoutVia, layoutViaArray
from revedaEditor.common.layoutShapes.polygons import layoutPolygon

__all__ = [
    "textureCache",
    "layoutShape",
    "layoutRect",
    "layoutInstance",
    "layoutPcell",
    "layoutLine",
    "layoutPath",
    "layoutRuler",
    "alignLine",
    "layoutLabel",
    "layoutPin",
    "layoutVia",
    "layoutViaArray",
    "layoutPolygon",
]
