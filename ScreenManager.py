from Globals import *
from pyglet.gl import *
from ctypes import *
from array import *


def ease_in_out_cubic(x):
    m = x % 1
    f = x // 1
    if m < 0.5:
        return f + 4 * (m ** 3)
    else:
        return f + 1 - ((-2 * m + 2) ** 3) / 2


def ease_out_cubic(x):
    return 1 - (1 - x) ** 3


def ease_in_cubic(x):
    return x ** 3


def sine_ease(x):
    m = x % 1
    f = x // 1
    return f - (math.cos(math.pi * m) - 1) / 2


class Camera(Component):
    def __init__(self, mainCamera=False):
        self.gameObject = None
        self.mainCamera = mainCamera
        if Screen.camera is None:
            Screen.camera = self
        Resources.cameras.append(self)

    def update(self, fpsDelta):
        pass

    def setMain(self):
        for camera in Resources.cameras:
            camera.mainCamera = False
        self.mainCamera = True
        Screen.camera = self


shader_types = {"vert": "vertex",
                "frag": "fragment",
                "comp": "compute",
                "geom": "geometry",
                "tesc": "tesscontrol",
                "tese": "tessevaluation"}


class Shader(pyglet.graphics.shader.ShaderProgram):
    def __init__(self, path, sprite_vert=False):
        shaders = []

        self.handle = {}

        if sprite_vert:
            default_vert = pyglet.graphics.shader.Shader(pyglet.sprite.vertex_source, "vertex")
            shaders.append(default_vert)

        p = os.path.join(Resources.resourcePath, path)
        for f in os.listdir(p):
            file = open(os.path.join(Resources.resourcePath, path, f))
            extension = f.split(".")[-1]
            shader = pyglet.graphics.shader.Shader(file.read(), shader_types[extension])
            shaders.append(shader)

        super().__init__(*shaders)

    # def set_uniforms(self):
    #     for key, value in self.handle.items():
    #         location = glGetUniformLocation(self.id, create_string_buffer(key.encode('utf-8')))
    #         if location == -1:
    #             print("NOT FOUND:", key)
    #         c_array = (c_int * len(value))()
    #         c_array[:] = value
    #         ptr = cast(c_array, POINTER(c_int))
    #         glProgramUniform2iv(self.id, location, len(value), ptr)
    #     self.handle = {}
    #
    # def __setitem__(self, key, value):
    #     if type(value) == list:
    #         self.handle[key] = value
    #     else:
    #         super().__setitem__(key, value)


# class SpriteGroup(pyglet.graphics.Group):
#     def __init__(self, texture, blend_src, blend_dest, program, parent=None):
#         super().__init__(parent)
#
#         self.texture = texture
#         self.blend_src = blend_src
#         self.blend_dest = blend_dest
#         self.program = program
#
#     def set_state(self):
#         self.program.use()
#
#         glActiveTexture(GL_TEXTURE0)
#         glBindTexture(self.texture.target, self.texture.id)
#
#         glEnable(GL_BLEND)
#         glBlendFunc(self.blend_src, self.blend_dest)
#
#         if hasattr(self.program, "set_uniforms"):
#             self.program.set_uniforms()
#
#     def unset_state(self):
#         glDisable(GL_BLEND)
#         self.program.stop()
#
#     def __repr__(self):
#         return "{0}({1})".format(self.__class__.__name__, self.texture)
#
#     def __eq__(self, other):
#         return (other.__class__ is self.__class__ and
#                 self.program is other.program and
#                 self.parent == other.parent and
#                 self.texture.target == other.texture.target and
#                 self.texture.id == other.texture.id and
#                 self.blend_src == other.blend_src and
#                 self.blend_dest == other.blend_dest)
#
#     def __hash__(self):
#         return hash((self.program, self.parent,
#                      self.texture.id, self.texture.target,
#                      self.blend_src, self.blend_dest))
#
#
# pyglet.sprite.Sprite.group_class = SpriteGroup


class Sprite(pyglet.sprite.Sprite, Component):
    def __init__(self, img, group=0, batch="default", x=0, y=0, program=None, ppu=Screen.unit):
        if type(img) == str:
            img = load_image(img)

        self.gameObject = None

        self._program = program
        if not program:
            self._program = pyglet.sprite.get_default_shader()

        if isinstance(batch, pyglet.graphics.Batch) and isinstance(group, pyglet.graphics.Group):
            b, g = batch, group
        else:
            b, g = Screen.get_render_set(batch, group)

        self.ppu = ppu

        super().__init__(img, x=x, y=y, batch=b, group=g)

    def __deepcopy__(self, memo):
        img = self.image.get_region(0, 0, self.image.width, self.image.height)
        return Sprite(img, self._group, self._batch, self.x, self.y, self._program, self.ppu)

    def destroy(self):
        self.delete()

    def update(self, fpsDelta):
        self.visible = self.visible and self.gameObject.active

    def on_draw(self):
        self.position()

    def position(self):
        transform = self.gameObject.transform

        position = transform.worldToScreen(transform.position)
        dx, dy = math.cos(math.radians(360-transform.rotation)), \
                 math.sin(math.radians(360-transform.rotation))
        size = Vector2(self.width / 2, self.height / 2)
        offset = Vector2(size.x * dx - size.y * dy, size.x * dy + size.y * dx)
        position = position - offset
        position = Vector2(int(position.x), int(position.y))

        super().update(position.x, position.y,
                        rotation=transform.rotation,
                        scale_x=transform.scale.x * (Screen.unit / self.ppu),
                        scale_y=transform.scale.y * (Screen.unit / self.ppu))

    def tile(self, size):
        tiled = pyglet.image.ImageGrid(image=self.image, rows=int(size.x), columns=int(size.y),
                                       item_width=self.width, item_height=self.height)
        texture_grid = tiled.get_texture_sequence().\
            get_region(0, 0, self.width * size.x, self.height * size.y)
        self.image = texture_grid

    @property
    def program(self):
        return self._program


def load_image(name):
    return pyglet.image.load(os.path.join(Resources.resourcePath, name))


def images_from_folder(sprite_folder):
    sprites = []
    for name in os.listdir(os.path.join(Resources.resourcePath, sprite_folder)):
        sprites.append(pyglet.image.load(os.path.join(Resources.resourcePath, sprite_folder, name)))
    return sprites


def sprites_from_folder(sprite_folder):
    sprites = []
    for name in os.listdir(os.path.join(Resources.resourcePath, sprite_folder)):
        sprites.append(Sprite(os.path.join(Resources.resourcePath, sprite_folder, name)))
    return sprites


def animation_from_folder(sprite_folder, renderer: Sprite, fps):
    sprites = images_from_folder(sprite_folder)
    frames = [Frame(sprites[i], (i + 1) * 1 / fps) for i in range(len(sprites))]
    prop = Property(renderer, "image", frames, interpolation=None)
    return Animation([prop])


class Frame:
    def __init__(self, value, timestamp):
        self.value = value
        self.timestamp = timestamp


class Property:
    def __init__(self, component, name, frames, interpolation=None):
        self._component = component
        self._name = name
        self.frames = frames
        self.interpolation = interpolation

    @property
    def value(self):
        return getattr(self._component, self._name)

    @value.setter
    def value(self, value):
        setattr(self._component, self._name, value)


class Animation:
    def __init__(self, properties: list[Property], loop=True):
        self.properties = properties
        self.loop = loop

        self.finished = False

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, properties):
        self._properties = properties
        self._length = max(max(frame.timestamp for frame in prop.frames) for prop in properties)
        self.local_time = 0

    def update(self, fpsDelta):
        if self.finished:
            return

        for prop in self.properties:
            for f in range(len(prop.frames)):
                frame = prop.frames[f]
                if not self.local_time < frame.timestamp:
                    continue

                prev_frame = prop.frames[f - 1]
                if f != 0:
                    if self.local_time < prev_frame.timestamp:
                        continue

                if prop.interpolation is not None:
                    t = (self.local_time - prev_frame.timestamp) / abs(prev_frame.timestamp - frame.timestamp)
                    prop.value = prop.interpolation(prev_frame.value, frame.value, t)

                if not self.local_time + fpsDelta >= frame.timestamp:
                    continue

                if prop.interpolation is None:
                    prop.value = frame.value

        if self.local_time + fpsDelta > self._length and not self.loop:
            self.finished = True
            return

        self.local_time = (self.local_time + fpsDelta) % self._length

    def play(self):
        self.local_time = 0
        self.finished = False


class Animator(Component):
    def __init__(self, animations: dict, state, play_on_awake=True):
        self._state = None
        self._anim = None

        self.animations = animations
        self.state = state

        self._playing = play_on_awake

    @property
    def playing(self):
        return self._playing

    def play(self):
        self._playing = True

    def pause(self):
        self._playing = False

    def update(self, fpsDelta):
        if not self._playing:
            return

        self._anim.update(fpsDelta)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state
        self._anim = self.animations[state]
        self._anim.play()
