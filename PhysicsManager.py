from Globals import *
from ObjectManager import *
from ScreenManager import *
from FileManager import *


def triangleArea(triangleList):
    return abs(((triangleList[0].x * (triangleList[1].y - triangleList[2].y)) +
                (triangleList[1].x * (triangleList[2].y - triangleList[0].y)) +
                (triangleList[2].x * (triangleList[0].y - triangleList[1].y)))/2)


def insideTriangle(triangleList, point):
    a = triangleArea(triangleList)
    a1 = triangleArea([point, triangleList[1], triangleList[2]])
    a2 = triangleArea([triangleList[0], point, triangleList[2]])
    a3 = triangleArea([triangleList[0], triangleList[1], point])
    return a == a1 + a2 + a3


def triangleIsClockwise(triangleList):
    return (triangleList[1] - triangleList[0]).cross((triangleList[2] - triangleList[0])) >= 0


class PolygonCollider:
    def __init__(self, points=None):
        self.gameObject = None
        self.points = points if points is not None else []
        self.triangles = []
        Physics.colliders.append(self)

    def update(self, fpsDelta):
        if len(self.triangles) < len(self.points) - 2:
            self.segment()

    def centerOfMass(self):
        pass

    def segment(self):
        self.triangles = []

        pointList = self.points.copy()
        for t in range(len(self.points) - 2):
            boundingPointIndex = None

            for possibleTriangle in range(len(pointList)):
                triangleWorks = True

                trianglePoints = [pointList[((possibleTriangle - 1) % len(pointList))],
                                   pointList[possibleTriangle],
                                   pointList[((possibleTriangle + 1) % len(pointList))]]

                if triangleIsClockwise(trianglePoints):
                    triangleWorks = False

                slicedList = pointList.copy()
                for point in trianglePoints:
                    slicedList.remove(point)
                for point in slicedList:
                    if insideTriangle(trianglePoints, point):
                        triangleWorks = False
                        break

                if triangleWorks:
                    boundingPointIndex = possibleTriangle
                    break

            if boundingPointIndex is not None:
                self.triangles.append([pointList[((boundingPointIndex - 1) % len(pointList))],
                                       pointList[boundingPointIndex],
                                       pointList[((boundingPointIndex + 1) % len(pointList))]])
                pointList.remove(pointList[boundingPointIndex])

    def getCollision(self):
        pass


class BoxCollider(PolygonCollider):
    def __init__(self, size=None):
        size = size if size is not None else Vector2(1, 1)
        points = list(Vector2((int(0 < i < 3) - 0.5) * size.x, ((int(i / 2) % 2) - 0.5) * size.y) for i in range(4))

        super().__init__(points=points)


class CircleCollider(PolygonCollider):
    def __init__(self, size=None, accuracy=20):
        size = size if size is not None else 1
        points = list(Vector2(math.cos(math.radians((i / accuracy) * 360)) * (size / 2),
                              math.sin(math.radians((i / accuracy) * 360)) * (size / 2)) for i in range(accuracy))

        super().__init__(points=points)


class Rigidbody:
    def __init__(self, velocity=None, torque=0, gravity=None, static=False):
        self.gameObject = None

        self.velocity = velocity if velocity is not None else Vector2(0, 0)
        self.torque = torque
        self.gravity = gravity if gravity is not None else Vector2(0, 0)
        self.static = static

    def update(self, fpsDelta):
        if not self.static:
            colliderFound = False
            colliders = []
            for colliderType in Physics.colliderTypes:
                possibleCollider = self.gameObject.getComponent(colliderType)
                if possibleCollider is not None:
                    colliderFound = True
                    colliders.append(possibleCollider)
            if not colliderFound:
                self.gameObject.transform.position += self.velocity * fpsDelta
                self.velocity += self.gravity * fpsDelta
                self.gameObject.transform.rotation += self.torque * fpsDelta
            else:
                for collider in colliders:
                    pass


class Physics:
    colliders = []
    colliderTypes = [PolygonCollider, BoxCollider, CircleCollider]
