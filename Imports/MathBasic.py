import math


def angle2Vector(angle):
    return Vector2(math.cos(angle * (math.pi / 180)), math.sin(angle * (math.pi / 180)))


def vector2Angle(vector):
    return math.atan2(vector.y, vector.x) * (180 / math.pi)


def toVector(thing):
    return Vector2(thing[0], thing[1])


def lineIntersection(l1, l2):
    xdiff = (l1[0].x - l1[1].x, l2[0].x - l2[1].x)
    ydiff = (l1[0].y - l1[1].y, l2[0].y - l2[1].y)

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div != 0:
        d = (det(*l1), det(*l2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        if min(l1[0].x, l1[1].x) < x < max(l1[0].x, l1[1].x) and min(l2[0].x, l2[1].x) < x < max(l2[0].x, l2[1].x):
            return x, y


def clockwise(l1, l2):
    p1, p2 = l1[1] - l1[0], l2[1] - l1[0]
    return (p2.x - p1.x) * (p2.y + p1.y) >= 0


def projectOntoLine(line, point):
    ap = line[1] - line[0]
    ab = point - line[0]
    v = (ab.x ** 2 + ab.y ** 2)
    if v != 0:
        t = (ap.x * ab.x + ap.y * ab.y) / (ab.x ** 2 + ab.y ** 2)
        if t < 0:
            return line[1]
        if t > 1:
            return line[0]
        return line[1] + (ab * t)
    return line[0]


def lerp(a, b, t):
    return a + ((b - a) * t)


class Vector2:
    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y

    def copy(self):
        return Vector2(self.x, self.y)

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

    def __floordiv__(self, other):
        return (self / other).__floor__()

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

    def __floor__(self):
        return Vector2(int(self.x), int(self.y))

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

    def inBBOX(self, box):
        return box[0].x <= self.x <= box[1].x and box[0].y <= self.y <= box[1].y

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


class VectorN:
    def __init__(self, data):
        self.data = data
        try:
            self.x = data[0]
            self.y = data[1]
            self.z = data[2]
            self.w = data[3]
        except IndexError:
            pass

    def __add__(self, other):
        if type(other) == VectorN:
            if len(other.data) == len(self.data):
                return VectorN([self.data[i] + other.data[i] for i in range(len(self))])

    def __sub__(self, other):
        if type(other) == VectorN:
            if len(other.data) == len(self.data):
                return VectorN([self.data[i] - other.data[i] for i in range(len(self))])

    def __mul__(self, other):
        if type(other) == VectorN:
            if len(other.data) == len(self.data):
                return VectorN([self.data[i] * other.data[i] for i in range(len(self))])

        elif type(other) in [int, float]:
            return VectorN([self.data[i] * other for i in range(len(self))])

    def __truediv__(self, other):
        if type(other) == VectorN:
            if len(other.data) == len(self.data):
                return VectorN([self.data[i] / other.data[i] for i in range(len(self))])

        elif type(other) in [int, float]:
            return VectorN([self.data[i] / other for i in range(len(self))])

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for i in range(len(self)):
            yield self.data[i]

    def __getitem__(self, item):
        return self.data[item]

    def __str__(self):
        return str(self.data)

    def normalize(self):
        return self / self.magnitude()

    def magnitude(self):
        return math.sqrt(sum(self.data[i] ** 2 for i in range(len(self))))

    def floor(self):
        return VectorN([math.floor(self.data[i]) for i in range(len(self))])

    def ceil(self):
        return VectorN([math.ceil(self.data[i]) for i in range(len(self.data))])

    def dot(self, other):
        if type(other) == VectorN:
            if len(other) == len(self):
                return sum(iter(self * other))

