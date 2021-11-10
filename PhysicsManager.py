from Globals import *
from ObjectManager import *
from ScreenManager import *

class Physics:
    colliders = []

class BoxCollider:
    quickAngles = [225, 135, 45, 315]

    def __init__(self):
        Physics.colliders.append(self)

    def update(self, fpsDelta):
        pass


class CircleCollider:
    def __init__(self):
        Physics.colliders.append(self)

    def update(self, fpsDelta):
        pass


class Rigidbody:
    def __init__(self):
        pass

    def update(self, fpsDelta):
        pass