import math


def angle2Vector(angle):
    return Vector2(math.cos(angle * (math.pi / 180)), math.sin(angle * (math.pi / 180)))

def vector2Angle(vector):
    return math.atan2(vector.y, vector.x) * (180 / math.pi)

def toVector(thing):
    return Vector2(thing[0], thing[1])


class Vector2(dict):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        dict.__init__(self, x=x, y=y, type="Vector2")

    def round(self):
        return Vector2(round(self.x), round(self.y))

    def __add__(self, other):
        if type(other) == Vector2:
            return Vector2(self.x + other.x, self.y + other.y)
        elif type(other) == Vector3:
            return Vector3(self.x + other.x, self.y + other.y, other.z)

    def __sub__(self, other):
        if type(other) == Vector2:
            return Vector2(self.x-other.x, self.y-other.y)
        elif type(other) == Vector3:
            return Vector3(self.x-other.x, self.y-other.y, -other.z)

    def __mul__(self, other):
        if type(other) == Vector2:
            return Vector2(self.x * other.x, self.y * other.y)
        elif type(other) == int or type(other) == float:
            return Vector2(self.x * other, self.y * other)

    def __truediv__(self, other):
        try:
            if type(other) == Vector2:
                return Vector2(self.x/other.x, self.y/other.y)
            if type(other) == int or type(other) == float:
                return Vector2(self.x/other, self.y/other)
        except ZeroDivisionError:
            if type(other) == Vector2:
                return Vector2(self.x/(other.x + 0.0001), self.y/(other.y + 0.0001))
            if type(other) == int or type(other) == float:
                return Vector2(self.x/(other + 0.0001), self.y/(other + 0.0001))

    def __abs__(self):
        return Vector2(abs(self.x), abs(self.y))

    def __round__(self, n=None):
        return Vector2(round(self.x, n), round(self.y, n))

    def __str__(self):
        return "("+str(self.x)+", "+str(self.y)+")"

    def __getitem__(self, item):
        if item == 0:
            return self.x
        if item == 1:
            return self.y

    def __lt__(self, other):
        return self.magnitude() < other.magnitude()

    def __le__(self, other):
        return self.magnitude() <= other.magnitude()

    def __gt__(self, other):
        return self.magnitude() > other.magnitude()

    def __ge__(self, other):
        return self.magnitude() >= other.magnitude()

    def __eq__(self, other):
        return self.magnitude() == other.magnitude()

    def magnitude(self):
        return math.sqrt((self.x ** 2) + (self.y ** 2))

    def normalize(self):
        return self / self.magnitude()

    def sum(self):
        return self.x + self.y

    def isInside(self, point1, point2):
        insideX = min(point1.x, point2.x) <= self.x <= max(point1.x, point2.x)
        insideY = min(point1.y, point2.y) <= self.y <= max(point1.y, point2.y)
        return insideX and insideY

    def toList(self):
        return [self.x, self.y]

    def cross(self, other):
        return self.y * other.x - self.x * other.y

    def rotate(self, angle):
        startAngle = math.atan2(self.y, self.x)
        endPosition = Vector2(math.cos(startAngle + angle), math.sin(startAngle + angle)) * self.magnitude()
        self.x = endPosition.x
        self.y = endPosition.y
        return endPosition

    def rotateAroundPoint(self, point, angle):
        thing = self - point
        thing.rotate(angle)
        thing = thing + point
        self.x = thing.x
        self.y = thing.y
        return self


    @staticmethod
    def distance(point1, point2):
        return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

    @staticmethod
    def dot(point1, point2):
        return (point1.x * point2.x) + (point1.y * point2.y)


class Vector3(dict):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        dict.__init__(self, x=x, y=y, z=z, type="Vector3")

    def __add__(self, other):
        if type(other) == Vector3:
            return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
        elif type(other) == Vector2:
            return Vector3(self.x + other.x, self.y + other.y, self.z)

    def __sub__(self, other):
        if type(other) == Vector3:
            return Vector3(self.x-other.x, self.y-other.y, self.z-other.z)
        elif type(other) == Vector2:
            return Vector3(self.x-other.x, self.y-other.y, self.z)

    def __mul__(self, other):
        if type(other) == Vector3:
            return Vector3(self.x * other.x, self.y * other.y, self.z * other.z)
        elif type(other) == int or type(other) == float:
            return Vector3(self.x * other, self.y * other, self.z * other)

    def __truediv__(self, other):
        if type(other) == Vector3:
            return Vector3(self.x/other.x, self.y/other.y, self.z/other.z)
        if type(other) == int or type(other) == float:
            return Vector3(self.x/other, self.y/other, self.z/other)

    def __abs__(self):
        return Vector3(abs(self.x), abs(self.y), abs(self.z))

    def __str__(self):
        return "("+str(self.x)+", "+str(self.y)+", "+str(self.z)+")"

    def __getitem__(self, item):
        if item == 0:
            return self.x
        if item == 1:
            return self.y
        if item == 2:
            return self.z

    def toList(self):
        return [self.x, self.y, self.z]
