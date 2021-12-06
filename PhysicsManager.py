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
    return a1 + a2 + a3 - 0.00001 <= a <= a1 + a2 + a3 + 0.00001


def triangleIsClockwise(triangleList):
    return (triangleList[1] - triangleList[0]).cross((triangleList[2] - triangleList[0])) >= 0


def projectOntoLine(line, point):
    ap = point - line[0]
    ab = line[1] - line[0]
    t = Vector2.dot(ap, ab) / Vector2.dot(ab, ab)
    t = max(0, min(1, t))
    result = line[0] + ab * t
    return result


def y(point):
    return point.y

def minY(pointList):
    return min(pointList, key=y)

def maxY(pointList):
    return max(pointList, key=y)


class PolygonCollider:
    def __init__(self, points=None, offset=None):
        self.gameObject = None
        self.offset = offset if offset is not None else Vector2(0, 0)
        self.points = points if points is not None else []
        self.triangles = []
        self.lines = []
        self.area = 0
        self.center = None
        self.rigidbody = None
        self.previousPosition = Vector2(0, 0)
        self.previousRotation = 0
        self.boundingBox = []
        self.orderedPoints = None
        Physics.colliders.append(self)

    def update(self, fpsDelta):
        self.startCheck()

        if len(self.triangles) < len(self.points) - 2:
            self.segment()

        if self.previousPosition != self.gameObject.transform.position or abs(self.previousRotation - self.gameObject.transform.rotation) > 0.2:
            self.move()

    def startCheck(self):
        if self.orderedPoints is None:
            self.orderedPoints = []
            for p in range(len(self.points)):
                self.orderedPoints.append(self.points[p].toList())

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
            nextPoint = self.points[(p + 1) % len(self.points)]

            nextPoint -= self.offset
            point -= self.offset

            thing = (point.x * nextPoint.y) - (nextPoint.x * point.y)
            area += thing
            x += thing * (point.x + nextPoint.x)
            y += thing * (point.y + nextPoint.y)

        area *= 0.5
        x *= 1 / (6 * area)
        y *= 1 / (6 * area)

        selfColliders = len(self.gameObject.getAllOfComponentTypes(Physics.colliderTypes))

        previousArea = self.area
        self.area = area
        selfMass = self.area * self.rigidbody.density
        if self.rigidbody.mass == 0 or selfColliders == 1:
            self.rigidbody.mass = selfMass
        else:
            self.rigidbody.mass += selfMass - (previousArea * self.rigidbody.density)

        self.center = Vector2(x, y)
        self.rigidbody.findCenter()

        self.previousPosition = self.center
        self.boundingBox = [
            Vector2(min(point.x for point in self.points), min(point.y for point in self.points)),
            Vector2(max(point.x for point in self.points), max(point.y for point in self.points))
        ]

    def move(self):
        self.startCheck()
        self.centerOfMass()

        changePosition = (self.gameObject.transform.position - self.previousPosition)

        for p in range(len(self.points)):
            self.points[p] += changePosition
            self.orderedPoints[p] = self.points[p].toList()

        for t in range(len(self.triangles)):
            for p in range(len(self.triangles[t])):
                self.triangles[t][p] += changePosition

        for l in range(len(self.lines)):
            for p in range(len(self.lines[l]) - 2):
                self.lines[l][p][0] += changePosition
                self.lines[l][p][1] += changePosition
            self.lines[l][-1] += changePosition.y
            self.lines[l][-2] += changePosition.y

        changeRotation = (self.gameObject.transform.rotation - self.previousRotation)

        if abs(changeRotation) > 0.2 and False:
            for t in range(len(self.triangles)):
                for p in range(len(self.triangles[t])):
                    self.triangles[t][p].rotateAroundPoint(self.rigidbody.center, math.radians(changeRotation))

            for p in range(len(self.points)):
                self.points[p].rotateAroundPoint(self.rigidbody.center, math.radians(0))

            self.previousRotation = self.gameObject.transform.rotation

        self.boundingBox = [
            Vector2(min(point.x for point in self.points), min(point.y for point in self.points)),
            Vector2(max(point.x for point in self.points), max(point.y for point in self.points))
        ]
        if self.center is not None:
            self.previousPosition = self.center

    def segment(self):
        self.startCheck()

        for p in range(len(self.points)):
            self.points[p] += (self.gameObject.transform.position - self.previousPosition)

        self.centerOfMass()

        pointList = self.points.copy()

        self.lines = []

        pointsInList = max(10, int(len(pointList) / 4))
        for i in range(math.ceil(len(pointList) / pointsInList)):
            lineList = []
            for p in range(pointsInList):
                if p + (i * pointsInList) < len(pointList):
                    lineList.append([pointList[p + (i * pointsInList)], pointList[(p + (i * pointsInList) + 1) % len(pointList)]])

            thingList = list(line[0] for line in lineList)
            minimum = min(thingList, key=y).y
            maximum = max(thingList, key=y).y
            lineList.append(minimum)
            lineList.append(maximum)
            self.lines.append(lineList)

        self.triangles = []

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
        for collider in set(Physics.colliders) - set(self.gameObject.getAllOfComponentTypes(Physics.colliderTypes)):
            if not (self.rigidbody.static and collider.rigidbody.static):
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
                    Time.startDebugTime()

                    for point in self.points:
                        collisionFound = False

                        truePoint = point + positionAdd
                        colliderPosition = colliderSpeed

                        for o in range(len(collider.lines)):
                            other = collider.lines[0]
                            other1 = other[-1] + colliderPosition.y
                            other2 = other[-2] + colliderPosition.y
                            if max(other1, other2) >= truePoint.y >= min(other1, other2):
                                total = 0
                                for line in other[:-2]:
                                    line0 = line[0] + colliderPosition
                                    line1 = line[1] + colliderPosition
                                    if line0.x >= truePoint.x or line1.x >= truePoint.x:
                                        if max(line0.y, line1.y) >= truePoint.y >= min(line0.y, line1.y):
                                            total += 1
                                if total % 2 == 1:
                                    collisions.append([collider, truePoint])
                                    collisionFound = True
                                    break
                            if collisionFound:
                                break
                        if collisionFound:
                            break

                    # print("\n")
                    # print(len(collisions), "newc")
                    #
                    # newMethodTime = Time.getDebugTime()
                    # print(newMethodTime, "newt")

                    # collisions = []

                    # for point in self.points:
                    #     collisionFound = False
                    #
                    #     truePoint = point + positionAdd
                    #
                    #     for other in collider.triangles:
                    #         newOther = other.copy()
                    #         for n in range(len(newOther)):
                    #             newOther[n] += colliderSpeed
                    #         if insideTriangle(newOther, truePoint):
                    #             collisions.append([collider, truePoint, newOther])
                    #             collisionFound = True
                    #             break
                    #     if collisionFound:
                    #         break
                    #
                    # print(len(collisions), "oldc")
                    #
                    # oldMethodTime = Time.getDebugTime()
                    #
                    # print(oldMethodTime, "oldt")
        return collisions

    def applyMomentum(self, fpsDelta, positionAdd):
        collisions = self.getCollisions(fpsDelta, positionAdd)
        for collision in collisions:
            collider, point = collision

            if not self.rigidbody.static or not collider.rigidbody.static:
                collisionData = collider.harderNormal(point)
                collisionNormal = collisionData[0].normalize()

                normalPoint = (collisionNormal / 100 * -1) + collisionData[1]
                flip = False
                for triangle in collider.triangles:
                    if not insideTriangle(triangle, normalPoint):
                        flip = True
                if flip:
                    collisionNormal *= -1

                frictionDir = Vector2(-collisionNormal.y, collisionNormal.x)
                bounceVector = abs(frictionDir + (collisionNormal * self.rigidbody.bounce))
                colliderBounce = abs(frictionDir + (collisionNormal * collider.rigidbody.bounce))
                bounceVector = Vector2(min(bounceVector.x, 1), min(bounceVector.y, 1))
                colliderBounce = Vector2(min(colliderBounce.x, 1), min(colliderBounce.y, 1))

                selfVelocity = self.getVelocity(point)

                if not collider.rigidbody.static:
                    colliderVelocity = collider.getVelocity(point)
                    totalMass = self.rigidbody.mass + collider.rigidbody.mass
                    thing = collisionNormal * (selfVelocity - colliderVelocity).magnitude()

                    systemVelocity = abs(self.rigidbody.velocity * self.rigidbody.mass) + \
                                     abs(collider.rigidbody.velocity * collider.rigidbody.mass)

                    if not self.rigidbody.static:
                        self.rigidbody.velocity = (selfVelocity + (thing * collider.rigidbody.mass)) / totalMass
                    collider.rigidbody.velocity = (colliderVelocity - (thing * self.rigidbody.mass)) / totalMass

                    newVelocity = abs(self.rigidbody.velocity * self.rigidbody.mass) + \
                                  abs(collider.rigidbody.velocity * collider.rigidbody.mass)

                    if not self.rigidbody.static:
                        self.rigidbody.velocity *= systemVelocity / newVelocity
                        self.rigidbody.velocity *= bounceVector
                    collider.rigidbody.velocity *= systemVelocity / newVelocity
                    collider.rigidbody.velocity *= colliderBounce

                else:
                    oldSpeed = self.rigidbody.velocity
                    self.rigidbody.velocity += collisionNormal * selfVelocity.magnitude() * 2
                    self.rigidbody.velocity *= abs(oldSpeed / self.rigidbody.velocity)
                    self.rigidbody.velocity *= bounceVector

                    if self.rigidbody.velocity.magnitude() < 0.002 * self.rigidbody.bounce:
                        self.rigidbody.velocity = Vector2(0, 0)

                if not self.rigidbody.static:
                    Editor.normals.append([projectOntoLine(collisionData[2], point), collisionNormal])

                self.gameObject.transform.position += collisionNormal * 0.1 * fpsDelta
                self.rigidbody.velocity += collisionNormal * 0.1 * fpsDelta
                if self.rigidbody.velocity.magnitude() > 0.1:
                    thing = self.rigidbody.velocity
                    other = self.rigidbody.velocity * frictionDir * self.rigidbody.friction * 10 * fpsDelta
                    minus = min(self.rigidbody.velocity, other)
                    self.rigidbody.velocity -= minus
                    if thing < self.rigidbody.velocity:
                        self.rigidbody.velocity += minus
                elif self.rigidbody.velocity.magnitude() > 0.05:
                    self.rigidbody.velocity *= (1 - self.rigidbody.friction)
                else:
                    self.rigidbody.velocity = Vector2(0, 0)

        return len(collisions) > 0

    def addTorque(self, origin, vector):
        if vector.magnitude() < 0.01:
            pass

    def harderNormal(self, closestPoint):
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

        return normal, (points[0] + points[1]) / 2, (points[0], points[1])

    def collisionNormal(self, triangle, closestPoint):
        distanceToLine = list(Vector2.distance(closestPoint, projectOntoLine([triangle[p], triangle[(p + 1) % 3]], closestPoint)) for p in range(3))
        point1Index = distanceToLine.index(min(distanceToLine))
        points = [triangle[point1Index], triangle[(point1Index + 1) % 3]]


        # closestLine = [Vector2(0, 0), Vector2(0, 0)]
        # smallestDistance = 1000000
        #
        # for p in range(len(self.points)):
        #     line = [self.points[p], self.points[(p + 1) % len(self.points)]]
        #     projectedPoint = projectOntoLine(line, closestPoint)
        #     distance = Vector2.distance(closestPoint, projectedPoint)
        #     if distance < smallestDistance:
        #         smallestDistance = distance
        #         closestLine = line
        #
        # points = closestLine

        normal = Vector2(-1, 1) * (points[0] - points[1])
        normal.y, normal.x = normal.x, normal.y

        return normal, (points[0] + points[1]) / 2, (points[0], points[1])


    def getVelocity(self, origin):
        rotationVelocity = Vector2(0, 0) * self.rigidbody.torque
        totalVelocity = (self.rigidbody.velocity + rotationVelocity)
        return totalVelocity


class BoxCollider(PolygonCollider):
    def __init__(self, size=None, offset=None):
        size = size if size is not None else Vector2(1, 1)
        offset = offset if offset is not None else Vector2(0, 0)
        points = list(Vector2((int(0 < i < 3) - 0.5) * size.x, ((int(i / 2) % 2) - 0.5) * size.y) for i in range(4))

        super().__init__(points=points, offset=offset)


class CircleCollider(PolygonCollider):
    def __init__(self, size=None, offset=None, sections=10):
        size = size if size is not None else Vector2(1, 1)
        offset = offset if offset is not None else Vector2(0, 0)
        points = list(Vector2(math.cos(math.radians((i / sections) * 360)) * (size.x / 2),
                              math.sin(math.radians((i / sections) * 360)) * (size.y / 2)) for i in range(sections))

        super().__init__(points=points, offset=offset)


class Rigidbody:
    def __init__(self, velocity=None, torque=0, gravity=None, static=False, bounce=1, friction=0):
        self.gameObject = None

        self.velocity = velocity if velocity is not None else Vector2(0, 0)
        self.torque = torque
        self.gravity = gravity if gravity is not None else Vector2(0, 0)
        self.mass = 0
        self.density = 1
        self.static = static
        self.bounce = bounce
        self.friction = friction
        self.layer = "Default"
        self.center = None

    def update(self, fpsDelta):
        colliders = self.gameObject.getAllOfComponentTypes(Physics.colliderTypes)
        collided = False
        for collider in colliders:
            collided = collider.applyMomentum(fpsDelta, self.velocity * fpsDelta) or collided

        if not self.static:
            if not collided:
                self.velocity += self.gravity * fpsDelta
                self.gameObject.transform.position += self.velocity * fpsDelta
                self.center += self.velocity * fpsDelta
                self.gameObject.transform.rotation += self.torque * fpsDelta
            else:
                pass

    def findCenter(self):
        self.center = Vector2(0, 0)
        colliders = self.gameObject.getAllOfComponentTypes(Physics.colliderTypes)
        for collider in colliders:
            try:
                self.center += ((collider.center + collider.offset) * collider.area * self.density) / self.mass
            except TypeError:
                pass


class Physics:
    colliders = []
    colliderTypes = [PolygonCollider, BoxCollider, CircleCollider]
