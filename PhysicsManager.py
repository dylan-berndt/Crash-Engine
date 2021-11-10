from Globals import *
from ObjectManager import *
from ScreenManager import *
from FileManager import *


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
    def __init__(self, velocity=None, torque=0, gravity=None, static=False):
        self.gameObject = None

        self.velocity = velocity if velocity is not None else Vector2(0, 0)
        self.torque = torque
        self.gravity = gravity if gravity is not None else Vector2(0, 0)
        self.static = static

    def update(self, fpsDelta):
        if not self.static:
            self.gameObject.transform.position += self.velocity * fpsDelta
            self.velocity += self.gravity * fpsDelta
            self.gameObject.transform.rotation += self.torque * fpsDelta
