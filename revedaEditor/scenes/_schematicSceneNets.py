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

"""Schematic scene net operations mixin: net merging, splitting, finding, and naming."""

from typing import List, Set, Tuple, Union

from PySide6.QtCore import QLineF, QPoint, QPointF, QRect, QRectF
from PySide6.QtWidgets import QGraphicsItem

import revedaEditor.common.net as snet
import revedaEditor.common.shapes as shp


class SchematicSceneNetsMixin:
    """Mixin class providing net operations for schematicScene."""

    def _updateNets(self, nets_to_remove: set, nets_to_add: set, name_source_net):
        """Helper to update nets in scene"""
        for net in nets_to_remove:
            self.removeItem(net)
        for net in nets_to_add:
            self.addItem(net)
            net.mergeNetName(name_source_net)

    def mergeSplitNets(self, inputNet: snet.schematicNet):
        merged, outputNet, processedNets = self.mergeNets(inputNet)

        if merged:
            splitDone, splitOutputNets = self.splitInputNet(outputNet)
            if splitDone:
                self._updateNets(processedNets - splitOutputNets,
                                 splitOutputNets - processedNets, outputNet)
            else:
                for net in processedNets:
                    self.removeItem(net)
                self.addItem(outputNet)
        else:
            splitDone, splitOutputNets = self.splitInputNet(inputNet)
            if splitDone:
                self._updateNets({inputNet} - splitOutputNets,
                                 splitOutputNets - {inputNet}, inputNet)

    def mergeNets(self, inputNet: snet.schematicNet) -> Tuple[
        bool, snet.schematicNet, Set[snet.schematicNet]]:
        """Merges overlapping nets and returns the merged net."""
        otherNets = inputNet.findOverlapNets()
        if not otherNets:
            return False, inputNet, set()

        parallelNets = {net for net in otherNets if inputNet.isParallel(net)}
        if not parallelNets:
            return False, inputNet, set()

        points = list(inputNet.sceneEndPoints)
        busExists = int(any(net.width for net in parallelNets) or inputNet.width)

        for net in parallelNets:
            points.extend(net.sceneEndPoints)

        furthestPoints = self.findFurthestPoints(points)
        mergedNet = snet.schematicNet(*furthestPoints, width=busExists)

        processedNets = parallelNets | {inputNet}
        for net in processedNets:
            mergedNet.mergeNetName(net)

        return True, mergedNet, processedNets

    def splitInputNet(self, inputNet) -> tuple[bool, Set[snet.schematicNet]]:
        sceneShapeRect = inputNet.sceneShapeRect
        sceneItems = self.items(sceneShapeRect)

        splitPointsSet = set()

        for item in sceneItems:
            if isinstance(item, snet.schematicNet) and inputNet.isOrthogonal(item):
                for point in item.sceneEndPoints:
                    if sceneShapeRect.contains(point):
                        splitPointsSet.add(point)
            elif isinstance(item, (shp.symbolPin, shp.schematicPin)):
                splitPointsSet.add(item.mapToScene(item.start).toPoint())

        if not splitPointsSet:
            return False, set()

        splitPointsList = [inputNet.sceneEndPoints[0], *splitPointsSet,
                           inputNet.sceneEndPoints[1]]
        orderedPoints = list(dict.fromkeys(self.orderPoints(splitPointsList)))

        splitNetSet = set()
        is_selected = inputNet.isSelected()

        for i in range(len(orderedPoints) - 1):
            splitNet = snet.schematicNet(orderedPoints[i], orderedPoints[i + 1],
                                         inputNet.width)
            if not splitNet.draftLine.isNull():
                if is_selected:
                    splitNet.setSelected(True)
                splitNetSet.add(splitNet)

        return True, splitNetSet

    def findSnapPoint(self, eventLoc: QPoint,
                      ignoredSet: set[snet.schematicNet]) -> QPoint:
        snapRect = QRect(eventLoc.x() - self.snapTuple[0],
                         eventLoc.y() - self.snapTuple[1], 4 * self.snapTuple[0],
                         4 * self.snapTuple[1])
        snapPoints = self.findConnectPoints(snapRect, ignoredSet)

        if self._newNet:
            snapPoints.update(self.findNetInterSect(self._newNet, snapRect))
        if snapPoints:
            lengths = [(snapPoint - eventLoc).manhattanLength() for snapPoint in
                       snapPoints]
            closestPoint = list(snapPoints)[lengths.index(min(lengths))]
            return closestPoint
        else:
            return eventLoc

    def findConnectPoints(self, sceneRect: QRect,
                          ignoredSet: set[QGraphicsItem]) -> set[QPoint]:
        snapPoints = set()
        rectItems = set(self.items(sceneRect)) - ignoredSet
        for item in rectItems:
            if isinstance(item, snet.schematicNet) and any(
                    list(map(sceneRect.contains, item.sceneEndPoints))):
                snapPoints.add(item.sceneEndPoints[list(
                    map(sceneRect.contains, item.sceneEndPoints)).index(True)])
            elif isinstance(item, shp.symbolPin):
                snapPoints.add(item.mapToScene(item.start).toPoint())
            elif isinstance(item, shp.schematicPin):
                snapPoints.add(item.mapToScene(item.start).toPoint())
        return snapPoints

    def findNetInterSect(self, inputNet: snet.schematicNet, rect: QRect) -> set[QPoint]:
        netsInSnapRectSet = {netItem for netItem in self.items(rect) if
                             isinstance(netItem,
                                        snet.schematicNet) and netItem.isOrthogonal(
                                 inputNet)}
        snapPointsSet = set()
        l1 = QLineF(inputNet.sceneEndPoints[0], inputNet.sceneEndPoints[1])
        unitVector = l1.unitVector()
        dx = unitVector.dx() if unitVector.dx() else 0
        dy = unitVector.dy() if unitVector.dy() else 0
        newEndX = l1.x2() + rect.width() * dx
        newEndY = l1.y2() + rect.height() * dy
        extendedL1 = QLineF(l1.p1(), QPointF(newEndX, newEndY))
        for netItem in netsInSnapRectSet:
            l2 = QLineF(netItem.sceneEndPoints[0], netItem.sceneEndPoints[1])
            (_, intersectPoint) = extendedL1.intersects(l2)
            if intersectPoint:
                snapPointsSet.add(intersectPoint.toPoint())
        return snapPointsSet

    @staticmethod
    def orderPoints(points: list[QPoint]) -> list[QPoint]:
        currentPoint = points.pop(0)
        orderedPoints = [currentPoint]

        while points:
            distances = [(point - currentPoint).manhattanLength() for point in points]
            nearest_point_index = distances.index(min(distances))
            nearestPoint = points[nearest_point_index]
            orderedPoints.append(nearestPoint)
            currentPoint = points.pop(nearest_point_index)

        return orderedPoints

    @staticmethod
    def findFurthestPoints(points: list[QPoint]) -> tuple[QPoint, QPoint]:
        """Find the two points with the maximum distance between them."""
        max_distance = 0
        furthest_points = None

        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                distance = (points[i] - points[j]).manhattanLength()
                if distance > max_distance:
                    max_distance = distance
                    furthest_points = (points[i], points[j])

        return furthest_points[0], furthest_points[1]

    def addStretchWires(self, start: QPoint, end: QPoint) -> List[snet.schematicNet]:
        """Add stretch wires between two points using L-shaped routing."""
        newNets = []
        if start == end:
            return newNets

        if start.x() != end.x() and start.y() != end.y():
            # L-shaped route
            midPoint = QPoint(end.x(), start.y())
            net1 = snet.schematicNet(start, midPoint)
            net2 = snet.schematicNet(midPoint, end)
            if not net1.draftLine.isNull():
                newNets.append(net1)
            if not net2.draftLine.isNull():
                newNets.append(net2)
        else:
            # Straight route
            net = snet.schematicNet(start, end)
            if not net.draftLine.isNull():
                newNets.append(net)

        return newNets
