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


def projectOntoLine(line, point):
    ap = point - line[0]
    ab = line[1] - line[0]
    t = Vector2.dot(ap, ab) / Vector2.dot(ab, ab)
    t = max(0, min(1, t))
    result = line[0] + ab * t
    return result


class PolygonCollider:
    def __init__(self, points=None):
        self.gameObject = None
        self.points = points if points is not None else []
        self.triangles = []
        self.area = 0
        self.center = Vector2(0, 0)
        self.rigidbody = None
        self.previousPosition = Vector2(0, 0)
        self.boundingBox = []
        Physics.colliders.append(self)

    def update(self, fpsDelta):
        self.startCheck()

        if len(self.triangles) < len(self.points) - 2:
            self.segment()

        if self.previousPosition != self.gameObject.transform.position:
            self.move()

    def startCheck(self):
        if self.rigidbody is None:
            if self.gameObject.getComponent(Rigidbody) is None:
                self.gameObject.addComponent(Rigidbody())
            self.rigidbody = self.gameObject.getComponent(Rigidbody)

        if self.previousPosition == Vector2(0, 0) and self.previousPosition != self.gameObject.transform.position:
            self.previousPosition = self.gameObject.transform.position
            for p in range(len(self.points)):
                self.points[p] += self.gameObject.transform.position

    def centerOfMass(self):
        area = 0
        x = 0
        y = 0
        for p, point in enumerate(self.points):
            nextP = (p + 1) % len(self.points)
            thing = (point.x * self.points[nextP].y) - (self.points[nextP].x * point.y)
            area += thing
            x += thing * (point.x + self.points[nextP].x)
            y += thing * (point.y + self.points[nextP].y)

        area *= 0.5
        x *= 1 / (6 * area)
        y *= 1 / (6 * area)

        self.area = area
        self.rigidbody.mass = self.area * self.rigidbody.density
        self.center = Vector2(x, y)
        self.gameObject.transform.position = self.center
        self.previousPosition = self.center
        self.boundingBox = [
            Vector2(min(point.x for point in self.points), min(point.y for point in self.points)),
            Vector2(max(point.x for point in self.points), max(point.y for point in self.points))
        ]

    def move(self):
        self.startCheck()

        for p in range(len(self.points)):
            self.points[p] += (self.gameObject.transform.position - self.previousPosition)

        for t in range(len(self.triangles)):
            for p in range(len(self.triangles[t])):
                self.triangles[t][p] += (self.gameObject.transform.position - self.previousPosition)

        self.centerOfMass()

    def segment(self):
        self.startCheck()

        self.triangles = []

        for p in range(len(self.points)):
            self.points[p] += (self.gameObject.transform.position - self.previousPosition)

        self.centerOfMass()

        pointList = self.points.copy()
        for t in range(len(pointList) - 2):
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

    def getCollisions(self, fpsDelta, positionAdd):
        collisions = []
        for collider in set(Physics.colliders) - {self}:
            if len(collider.boundingBox) == 0:
                collider.move()
            colliderSpeed = collider.rigidbody.velocity * fpsDelta
            boundingSize = self.boundingBox[1] - self.boundingBox[0]
            boundingPoints = [self.boundingBox[0] + positionAdd,
                              self.boundingBox[0] + positionAdd + Vector2(boundingSize.x, 0),
                              self.boundingBox[0] + positionAdd + Vector2(0, boundingSize.y),
                              self.boundingBox[1] + positionAdd]
            inBoundingBox = False
            for boundingPoint in boundingPoints:
                inBoundingBox = inBoundingBox or boundingPoint.isInside(collider.boundingBox[0] + colliderSpeed,
                                                                        collider.boundingBox[1] + colliderSpeed)
            if inBoundingBox:
                for point in self.points:
                    for other in collider.triangles:
                        newOther = other.copy()
                        for n in range(len(newOther)):
                            newOther[n] += colliderSpeed
                        if insideTriangle(newOther, point + positionAdd):
                            collisions.append([collider, point + positionAdd])
                            break
        return collisions

    def applyMomentum(self, fpsDelta, positionAdd):
        collisions = self.getCollisions(fpsDelta, positionAdd)
        for collision in collisions:
            collider, point = collision

            collisionData = collider.collisionNormal(point)
            collisionNormal = collisionData[0].normalize()

            normalPoint = (collisionNormal/10) + collisionData[1]
            flip = False
            for triangle in self.triangles:
                if not insideTriangle(triangle, normalPoint):
                    flip = True
            if not flip:
                collisionNormal *= -1

            selfVelocity = self.getVelocity(point)

            if not collider.rigidbody.static:
                colliderVelocity = collider.getVelocity(point)
                totalMass = self.rigidbody.mass + collider.rigidbody.mass
                thing = collisionNormal * (selfVelocity - colliderVelocity).magnitude()

                systemVelocity = abs(self.rigidbody.velocity) + abs(collider.rigidbody.velocity)

                self.rigidbody.velocity = (selfVelocity - (thing * collider.rigidbody.mass)) / totalMass
                collider.rigidbody.velocity = (colliderVelocity + (thing * self.rigidbody.mass)) / totalMass

                newVelocity = abs(self.rigidbody.velocity) + abs(collider.rigidbody.velocity)

                self.rigidbody.velocity *= systemVelocity / newVelocity
                collider.rigidbody.velocity *= systemVelocity / newVelocity

            else:
                oldSpeed = abs(self.rigidbody.velocity)
                self.rigidbody.velocity += (collisionNormal * Vector2(-1, -1) * selfVelocity.magnitude())
                try:
                    self.rigidbody.velocity *= abs(oldSpeed) / abs(self.rigidbody.velocity)
                except ZeroDivisionError:
                    self.rigidbody.velocity *= abs(oldSpeed) / (abs(self.rigidbody.velocity) + Vector2(0.001, 0.001))

        return len(collisions) > 0

    def addTorque(self, origin, vector):
        if vector.magnitude() > 0.01:
            pass

    def collisionNormal(self, closestPoint):
        closestLine = [Vector2(0, 0), Vector2(0, 0)]
        smallestDistance = 1000000

        for p in range(len(self.points)):
            line = [self.points[p], self.points[(p + 1) % len(self.points)]]
            projectedPoint = projectOntoLine(line, closestPoint)
            distance = Vector2.distance(closestPoint, projectedPoint)
            if distance < smallestDistance:
                smallestDistance = distance
                closestLine = line

        points = closestLine

        normal = Vector2(-1, 1) * (points[0] - points[1])
        normal.y, normal.x = normal.x, normal.y

        return normal, (points[0] + points[1]) / 2


    def getVelocity(self, origin):
        rotationVelocity = Vector2(0, 0) * self.rigidbody.torque
        totalVelocity = (self.rigidbody.velocity + rotationVelocity)
        return totalVelocity


class BoxCollider(PolygonCollider):
    def __init__(self, size=None):
        size = size if size is not None else Vector2(1, 1)
        points = list(Vector2((int(0 < i < 3) - 0.5) * size.x, ((int(i / 2) % 2) - 0.5) * size.y) for i in range(4))

        super().__init__(points=points)


class CircleCollider(PolygonCollider):
    def __init__(self, size=None, accuracy=20):
        size = size if size is not None else Vector2(1, 1)
        points = list(Vector2(math.cos(math.radians((i / accuracy) * 360)) * (size.x / 2),
                              math.sin(math.radians((i / accuracy) * 360)) * (size.y / 2)) for i in range(accuracy))

        super().__init__(points=points)


class Rigidbody:
    def __init__(self, velocity=None, torque=0, gravity=None, static=False):
        self.gameObject = None

        self.velocity = velocity if velocity is not None else Vector2(0, 0)
        self.torque = torque
        self.gravity = gravity if gravity is not None else Vector2(0, 0)
        self.mass = 0
        self.density = 1
        self.static = static

    def update(self, fpsDelta):
        colliders = self.gameObject.getAllOfComponentTypes(Physics.colliderTypes)
        collided = False
        for collider in colliders:
            collider.move()
            if not self.static:
                collided = collider.applyMomentum(fpsDelta, self.velocity * fpsDelta) or collided

        if not self.static:
            if not collided:
                self.gameObject.transform.position += self.velocity * fpsDelta
                self.gameObject.transform.rotation += self.torque * fpsDelta
                self.velocity += self.gravity * fpsDelta
            else:
                pass


class Physics:
    colliders = []
    colliderTypes = [PolygonCollider, BoxCollider, CircleCollider]
