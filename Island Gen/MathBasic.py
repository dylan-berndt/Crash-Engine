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
        if type(other) == Vector2:
            return Vector2(self.x/other.x, self.y/other.y)
        if type(other) == int or type(other) == float:
            return Vector2(self.x/other, self.y/other)

    def __str__(self):
        return "("+str(self.x)+", "+str(self.y)+")"

    def __getitem__(self, item):
        if item == 0:
            return self.x
        if item == 1:
            return self.y

    def isInside(self, point1, point2):
        insideX = min(point1.x, point2.x) < self.x < max(point1.x, point2.x)
        insideY = min(point1.y, point2.y) < self.y < max(point1.y, point2.y)
        return insideX and insideY

    def toList(self):
        return [self.x, self.y]

    @staticmethod
    def distance(point1, point2):
        return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)


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
