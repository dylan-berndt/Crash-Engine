from Globals import *


class Rigidbody:
    def __init__(self, velocity=None, static=False, mass=1, restitution=1, angularVelocity=0, gravity=None,
                 colliderMass=False, density=1):
        self.gameObject = None

        self.velocity = velocity if velocity is not None else Vector2(0, 0)
        self.static = static
        self.mass = mass
        self.density = density
        self.colliderMass = colliderMass
        self.restitution = restitution
        self.angularVelocity = angularVelocity

        self.gravity = gravity if gravity is not None else Vector2(0, 0)

    def update(self, fpsDelta):
        if self.colliderMass:
            self.mass = 0
        collided = False
        for collider in self.gameObject.getComponentsOfTypes(Physics.colliderTypes):
            collider.rigidbodyCheck()
            if self.colliderMass:
                self.mass += collider.area * self.density

        for collider in self.gameObject.getComponentsOfTypes(Physics.colliderTypes):
            if not self.static and collider.rigidbody is not None:
                collided = collider.collisions(fpsDelta) or collided
            collider.findCOM()
            collider.findBBOX()

        if not collided and not self.static:
            self.gameObject.transform.rotation += self.angularVelocity * fpsDelta
            self.gameObject.transform.position += self.velocity * fpsDelta
            self.velocity += self.gravity * fpsDelta

        for collider in self.gameObject.getComponentsOfTypes(Physics.colliderTypes):
            rotation = self.gameObject.transform.rotation - collider.previousRotation
            if rotation != 0:
                collider.previousRotation = self.gameObject.transform.rotation
                for point in collider.points:
                    point.rotateAroundPoint(collider.com, math.radians(rotation))


class Collider:
    def __init__(self, points, isTrigger=False):
        self.gameObject = None
        self.rigidbody = None

        self.isTrigger = isTrigger

        self.points = points
        self.com = None
        self.area = None
        self.findCOM()

        self.bbox = []
        self.findBBOX()

        self.normals = []
        self.findNormals()

        self.previousRotation = 0

        Physics.colliders.append(self)

    def destroy(self):
        Physics.colliders.remove(self)

    def rigidbodyCheck(self):
        if self.rigidbody is None and self.gameObject is not None:
            if self.gameObject.getComponent(Rigidbody) is None:
                self.gameObject.addComponent(Rigidbody())
            self.rigidbody = self.gameObject.getComponent(Rigidbody)

    def update(self, fpsDelta):
        pass

    def getVelocityAtPoint(self, point):
        pass

    def addForceAtPoint(self, force, point):
        if not self.rigidbody.static:
            self.rigidbody.velocity += force * 1 / self.rigidbody.mass
            direction = point - self.gameObject.transform.localToWorld(self.com)
            normal = Vector2(-direction.y, direction.x).normalize()
            dot = Vector2.dot(normal, force)
            self.rigidbody.angularVelocity += dot * direction.magnitude()

    def collisions(self, fpsDelta):
        collided = False
        for other in set(Physics.colliders) - set(self.gameObject.getComponentsOfTypes(Physics.colliderTypes)):
            if other.rigidbody is not None:
                momentum = abs(self.rigidbody.velocity * self.rigidbody.mass) + \
                                abs(other.rigidbody.velocity * other.rigidbody.mass)

                velocity = (self.rigidbody.velocity - other.rigidbody.velocity) * fpsDelta
                r1, r2 = self.gameObject.transform.rotation - self.previousRotation, \
                    other.gameObject.transform.rotation - other.previousRotation
                p1 = [(self.gameObject.transform.localToWorld(Vector2.rotateAroundPoint(point, self.com, math.radians(r1))) + velocity)
                      for point in self.points]
                p2 = [other.gameObject.transform.localToWorld(Vector2.rotateAroundPoint(point, other.com, math.radians(r2)))
                      for point in other.points]

                collisions = self.getCollisionPoints(other, p1, p2)
                for collision in collisions:
                    collided = True

                    normal = self.getNormalAtPoint(other, collision, p1, p2)

                    if not other.rigidbody.static:
                        velocityMag = (self.rigidbody.velocity - other.rigidbody.velocity).magnitude()
                        force = normal * velocityMag

                        # self.addForceAtPoint(force, p1[collision])
                        # other.addForceAtPoint(force * -1, p1[collision])

                        selfRatio, otherRatio = self.rigidbody.mass / other.rigidbody.mass, \
                                                other.rigidbody.mass / self.rigidbody.mass

                        self.rigidbody.velocity = (self.rigidbody.velocity + (force * selfRatio))
                        other.rigidbody.velocity = (other.rigidbody.velocity - (force * otherRatio))
                    else:
                        oldSpeed = self.rigidbody.velocity
                        self.rigidbody.velocity += normal * self.rigidbody.velocity.magnitude()
                        self.rigidbody.velocity *= abs(oldSpeed / self.rigidbody.velocity) * self.rigidbody.restitution

                    if self.rigidbody.velocity.magnitude() < 0.05:
                        self.rigidbody.velocity = Vector2(0, 0)

                newMoment = abs(self.rigidbody.velocity * self.rigidbody.mass) + \
                              abs(other.rigidbody.velocity * other.rigidbody.mass)

                if collisions:
                    self.rigidbody.velocity *= momentum * self.rigidbody.restitution / newMoment
                    other.rigidbody.velocity *= momentum * other.rigidbody.restitution / newMoment

        return collided

    def findCOM(self):
        # X = SUM[(Xi + Xi + 1) * (Xi * Yi + 1 - Xi + 1 * Yi)] / 6 / A
        # Y = SUM[(Yi + Yi + 1) * (Xi * Yi + 1 - Xi + 1 * Yi)] / 6 / A
        x, y, a = 0, 0, 0

        for p in range(len(self.points)):
            p1, p2 = self.points[p], self.points[(p + 1) % len(self.points)]
            t = (p1.x * p2.y - p2.x * p1.y)
            x += (p1.x + p2.x) * t
            y += (p1.y + p2.y) * t
            a += t

        x /= a * 6
        y /= a * 6
        a /= 2

        self.area = a

        self.com = Vector2(x, y)

    def findBBOX(self):
        if self.gameObject is not None:
            nPoints = [point + self.gameObject.transform.position for point in self.points]
            self.bbox = [Vector2(min([point.x for point in nPoints]), min([point.y for point in nPoints])),
                         Vector2(max([point.x for point in nPoints]), max([point.y for point in nPoints]))]

    def findNormals(self):
        for p in range(len(self.points)):
            p1, p2 = self.points[p], self.points[(p + 1) % len(self.points)]
            direction = p2 - p1
            normal = Vector2(direction.y, -direction.x).normalize()
            self.normals.append(normal)

    @staticmethod
    def getCollisionPoints(other, sPoints, oPoints):
        collisions = []

        for p, point in enumerate(sPoints):
            if point.inBBOX(other.bbox):
                intersections = 0
                for i in range(len(oPoints)):
                    l1, l2 = oPoints[i], oPoints[(i + 1) % len(oPoints)]
                    if min(l1.y, l2.y) < point.y < max(l1.y, l2.y):
                        if l1.x == l2.x:
                            if l1.x > point.x:
                                intersections += 1
                        elif (l1.x < l2.x and l1.y < l2.y) or (l1.x > l2.x and l1.y > l2.y):
                            if point.y < (((l1.y - l2.y) / (l1.x - l2.x)) * (point.x - l1.x)) + l1.y:
                                intersections += 1
                        else:
                            if point.y > (((l1.y - l2.y) / (l1.x - l2.x)) * (point.x - l1.x)) + l1.y:
                                intersections += 1

                if intersections % 2 == 1:
                    collisions.append(p)

        return collisions

    @staticmethod
    def getNormalAtPoint(other, p, sPoints, oPoints):
        smallestDistance = 9e+10
        current = None

        for o in range(len(oPoints)):
            l1, l2 = oPoints[o-1], oPoints[o]
            point = projectOntoLine([l1, l2], sPoints[p])
            diff = point - sPoints[p]
            distanceToPoint = diff.x ** 2 + diff.y ** 2
            if distanceToPoint < smallestDistance:
                smallestDistance = distanceToPoint
                current = o - 1

        normal = other.normals[current]

        return normal


class BoxCollider(Collider):
    def __init__(self, size=None, offset=None, isTrigger=False):
        size = size if size is not None else Vector2(1, 1)
        offset = offset if offset is not None else Vector2(0, 0)
        points = list(Vector2((int(0 < i < 3) - 0.5), ((int(i / 2) % 2) - 0.5)) * size + offset
                      for i in range(4))
        super().__init__(points=points, isTrigger=isTrigger)


class CircleCollider(Collider):
    def __init__(self, size=None, offset=None, sections=10, isTrigger=False):
        size = size if size is not None else Vector2(1, 1)
        offset = offset if offset is not None else Vector2(0, 0)
        points = list(Vector2(math.cos(i / sections * 2 * math.pi),
                              math.sin(i / sections * 2 * math.pi)) * size / 2 + offset
                      for i in range(sections))
        super().__init__(points=points, isTrigger=isTrigger)


class StarCollider(Collider):
    def __init__(self, size=None, offset=None, sections=10, isTrigger=False):
        size = size if size is not None else Vector2(1, 1)
        offset = offset if offset is not None else Vector2(0, 0)
        points = list(Vector2(math.cos(i / sections * 2 * math.pi + math.pi / 2) * (1 / (i % 2 + 1)),
                              math.sin(i / sections * 2 * math.pi + math.pi / 2) * (1 / (i % 2 + 1))) * size / 2 + offset
                      for i in range(sections))
        super().__init__(points=points, isTrigger=isTrigger)


Physics.colliderTypes = [Collider, BoxCollider, CircleCollider, StarCollider]


