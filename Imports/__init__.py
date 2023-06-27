import copy
import pyglet
import numpy as np
import os
from .Vector import *
import pyglet.window.key as key
import pyglet.gl as gl
import time
import sys


class Component:
    def __init__(self):
        self.gameObject = None

    def update(self, fpsDelta):
        pass

    def late_update(self, fpsDelta):
        pass

    def on_mouse_click(self, x, y, button, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass

    def on_key_press(self, symbol, modifiers):
        pass

    def on_key_release(self, symbol, modifiers):
        pass

    def destroy(self):
        pass
