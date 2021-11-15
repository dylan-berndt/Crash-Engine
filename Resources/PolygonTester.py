import Globals
from Globals import *

class PolygonTester:
    def __init__(self):
        self.gameObject = None

    def update(self, fpsDelta):
        if Input.leftClick or Input.rightClick:
            clickPos = toWorldPos(Input.mousePosition)
            colliders = self.gameObject.getAllOfComponentTypes(Physics.colliderTypes)
            polygonCollider = colliders[0]
            pointList = polygonCollider.points
            distanceList = list(Vector2.distance(clickPos, point) for point in pointList)
            pointIndex = distanceList.index(min(distanceList))

            if Input.leftClick:
                leftDistance = Vector2.distance(pointList[(pointIndex - 1) % len(pointList)], clickPos)
                rightDistance = Vector2.distance(pointList[(pointIndex + 1) % len(pointList)], clickPos)
                left = leftDistance < rightDistance
                if left:
                    polygonCollider.points.insert(pointIndex, clickPos)
                else:
                    polygonCollider.points.insert((pointIndex + 1) % len(pointList), clickPos)

            if Input.rightClick:
                polygonCollider.points.remove(pointList[pointIndex])

            polygonCollider.segment()
