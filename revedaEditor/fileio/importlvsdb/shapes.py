#     "Commons Clause" License Condition v1.0
#
#     The Software is provided to you by the Licensor under the License, as defined
#     below, subject to the following condition.
#
#     Without limiting other conditions in the License, the grant of rights under the
#     License will not include, and the License does not grant to you, the right to
#     Sell the Software.
#
#     For purposes of the foregoing, "Sell" means practicing any or all of the rights
#     granted to you under the License to provide to third parties, for a fee or other
#     consideration (including without limitation fees for hosting) a product or service whose value
#     derives, entirely or substantially, from the functionality of the Software. Any
#     license notice or attribution required by the License must also include this
#     Commons Clause License Condition notice.
#
#     Add-ons and extensions developed for this software may be distributed
#     under their own separate licenses.
#
#     Software: Revolution EDA
#     License: Mozilla Public License 2.0
#     Licensor: Revolution Semiconductor (Registered in the Netherlands)

"""LVS error highlighting shapes."""

from PySide6.QtCore import QRect
from PySide6.QtWidgets import QGraphicsRectItem


class LVSErrorRect(QGraphicsRectItem):
    def __init__(self, rect: QRect) -> None:
        super().__init__(rect)
        self.lvsRect = rect
        self.setZValue(100)
        self._cell = ""

    def __repr__(self) -> str:
        return f"LVSErrorRect({self.lvsRect})"

    def __str__(self) -> str:
        return f"LVSErrorRect({self.lvsRect})"

    @property
    def cell(self):
        return self._cell

    @cell.setter
    def cell(self, value: str):
        self._cell = value
