import math


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
    ap = point - line[0]
    ab = line[1] - line[0]
    t = Vector.dot(ap, ab) / Vector.dot(ab, ab)
    t = max(0, min(1, t))
    result = line[0] + ab * t
    return result


def lerp(a, b, t):
    return a + ((b - a) * t)


class Vector:
    def __init__(self, *args):
        self.data = []
        for arg in args:
            try:
                if type(arg) == Vector:
                    raise TypeError
                for item in arg:
                    self.data.append(item)
            except TypeError:
                self.data.append(arg)

    @property
    def x(self):
        return self.data[0] if len(self.data) >= 0 else None

    @x.setter
    def x(self, x):
        while len(self.data) < 1:
            self.data.append(None)
        self.data[0] = x

    @property
    def y(self):
        return self.data[1] if len(self.data) >= 1 else None

    @y.setter
    def y(self, y):
        while len(self.data) < 2:
            self.data.append(None)
        self.data[1] = y

    @property
    def z(self):
        return self.data[2] if len(self.data) >= 2 else None

    @z.setter
    def z(self, z):
        while len(self.data) < 3:
            self.data.append(None)
        self.data[2] = z

    @property
    def w(self):
        return self.data[3] if len(self.data) >= 3 else None

    @w.setter
    def w(self, w):
        while len(self.data) < 4:
            self.data.append(None)
        self.data[3] = w

    @staticmethod
    def type_assert(item):
        assert isinstance(item, Vector) or type(item) in [int, float], \
            "Operation attempted with invalid operand: " + str(type(item))

    def __getitem__(self, item):
        return self.data[item]

    def __add__(self, other):
        Vector.type_assert(other)
        if isinstance(other, Vector):
            return Vector(self[i] + other[i] for i in range(max(len(self), len(other))))
        elif type(other) in [int, float]:
            return Vector(item + other for item in self)

    def __sub__(self, other):
        Vector.type_assert(other)
        if isinstance(other, Vector):
            return Vector(self[i] - other[i] for i in range(max(len(self), len(other))))
        elif type(other) in [int, float]:
            return Vector(item - other for item in self)

    def __mul__(self, other):
        Vector.type_assert(other)
        if isinstance(other, Vector):
            return Vector(self[i] * other[i] for i in range(max(len(self), len(other))))
        elif type(other) in [int, float]:
            return Vector(item * other for item in self)

    def __floordiv__(self, other):
        Vector.type_assert(other)
        return Vector(math.floor(item) for item in (self / other))

    def __truediv__(self, other):
        Vector.type_assert(other)
        if isinstance(other, Vector):
            return Vector(self[i] / other[i] for i in range(max(len(self), len(other))))
        elif type(other) in [int, float]:
            return Vector(item / other for item in self)

    def __floor__(self):
        return Vector(math.floor(item) for item in self)

    def __abs__(self):
        return Vector(abs(item) for item in self)

    def __len__(self):
        return len(self.data)

    def list(self):
        return self.data

    def normalize(self):
        self.data = (self / (self.magnitude() + 1e-6)).data
        return self

    @property
    def magnitude(self):
        return sum(item ** 2 for item in self.data) ** 0.5

    def dot(self, other):
        if len(self) == len(other):
            return sum(self[i] * other[i] for i in range(len(self)))

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self + other

    def string(self):
        return "".join(str(item) for item in self)

    def interpolate(self, other, t):
        return self + ((other - self) * t)

    def __str__(self):
        return str("[" + ", ".join(str(item) for item in self) + "]")


class Vector2(Vector):
    def __init__(self, x, y):
        super().__init__(x, y)
