from Globals import *


def cubic_bezier_ease(x):
    m = x % 1
    f = x // 1
    if m < 0.5:
        return f + 4 * (m ** 3)
    else:
        return f + 1 - ((-2 * m + 2) ** 3) / 2


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


class SpriteRenderer(Component):
    def __init__(self, sprite, group=0, batch="default", alpha=255):
        self.gameObject = None

        self.destroyed = False

        self._sprite = None

        self.sprites = [sprite]

        self._alpha = alpha

        self._batch = batch if isinstance(batch, pyglet.graphics.Batch) else Screen.layers[batch]
        if type(group) in [int, str]:
            n, group = Screen.get_render_set("none", str(int(group)))
        self._group = group

        self.sprite = sprite

        self.destroyed = self.sprite is None

        if self.sprite is not None:
            self.batch = batch
            self.group = group

    def __deepcopy__(self, memo):
        return SpriteRenderer(self.sprite, self.group, self.batch)

    def destroy(self):
        for sprite in self.sprites:
            if not sprite.destroyed:
                sprite.destroyed = True
                sprite.delete()

    @property
    def batch(self):
        return self._batch

    @batch.setter
    def batch(self, batch):
        if self.sprite is None:
            return
        if type(batch) == str:
            self._batch = Screen.layers[batch]
        elif type(batch) == pyglet.graphics.Batch:
            self._batch = batch
        self.sprite.batch = self._batch
        if hasattr(self, "_group"):
            self.sprite.group = self._group

    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, group):
        if self.sprite is None:
            return
        if type(group) in [int, str]:
            n, group = Screen.get_render_set("none", group)
            self._group = group
        elif isinstance(group, pyglet.graphics.Group):
            self._group = group
        if hasattr(self, "_batch"):
            self.sprite.batch = self._batch
        self.sprite.group = self._group

    def update(self, fpsDelta):
        if self.useable():
            self.sprite.visible = self.gameObject.active and self.sprite.visible

    def late_update(self, fpsDelta):
        if self.useable():
            self.spritePosition()

    def useable(self):
        if self.sprite is None:
            self.destroyed = True
            return False
        if not hasattr(self.sprite._vertex_list, "vertices"):
            self.destroyed = True
        if not hasattr(self.sprite._texture, "anchor_x"):
            self.destroyed = True
        return not self.destroyed

    @property
    def visible(self):
        return self.sprite.visible

    @visible.setter
    def visible(self, value):
        if self.useable():
            self.sprite.visible = value
        else:
            try:
                self.sprite.visible = value
            except AttributeError:
                pass

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, alpha):
        self._alpha = alpha
        self.sprite.opacity = alpha

    def spritePosition(self):
        if self.gameObject is not None:
            sprite, transform = self.sprite, self.gameObject.transform

            position = transform.worldToScreen(transform.position)
            dx, dy = math.cos(math.radians(360-transform.rotation)), \
                     math.sin(math.radians(360-transform.rotation))
            size = Vector2(sprite.width / 2, sprite.height / 2)
            offset = Vector2(size.x * dx - size.y * dy, size.x * dy + size.y * dx)
            position = position - offset
            position = Vector2(int(position.x), int(position.y))

            sprite.update(position.x, position.y,
                          rotation=transform.rotation,
                          scale_x=transform.scale.x * (Screen.unit / self.sprite.ppu),
                          scale_y=transform.scale.y * (Screen.unit / self.sprite.ppu))

    @property
    def sprite(self):
        return self._sprite

    @sprite.setter
    def sprite(self, sprite):
        if not hasattr(sprite._vertex_list, "vertices"):
            self.destroyed = True
            return
        if not hasattr(sprite._texture, "anchor_x"):
            self.destroyed = True
            return
        if sprite is not None:
            if self.sprite is None:
                self.sprites.append(sprite)
                sprite.visible = True
                sprite.opacity = self.alpha
                self._sprite = sprite
            else:
                if sprite != self.sprite:
                    if sprite not in self.sprites:
                        self.sprites.append(sprite)
                    self.visible = False
                    sprite.visible = True
                    self._sprite = sprite
                    sprite.opacity = self.alpha
                    self.sprite.batch = self.batch
                    self.sprite.group = self.group
        else:
            self.destroyed = True

    def tileSprite(self, size):
        tiled = pyglet.image.ImageGrid(image=self.sprite.image, rows=int(size.x), columns=int(size.y),
                                       item_width=self.sprite.width, item_height=self.sprite.height)
        texture_grid = tiled.get_texture_sequence().\
            get_region(0, 0, self.sprite.width * size.x, self.sprite.height * size.y)
        thing = Sprite(texture_grid)
        self.sprite = thing


class Sprite(pyglet.sprite.Sprite):
    def __init__(self, image, batch="default", group="-10", ppu=Screen.unit, x=-5000, y=-5000):
        b, g = Screen.get_render_set(batch, group)
        if type(image) == str:
            self.path = image
            super().__init__(pyglet.image.load(os.path.join(Resources.resourcePath, self.path)),
                             batch=b, group=g, x=x, y=y)
        elif type(image) in [pyglet.image.Texture, pyglet.image.TextureGrid, pyglet.image.TextureRegion]:
            self.path = image
            super().__init__(image, batch=b, group=g, x=x, y=y)
        self.ppu = ppu
        self.b_name, self.g_name = batch, group
        self.destroyed = False

    def __deepcopy__(self, memo):
        return Sprite(self.image, self.b_name, self.g_name, self.ppu)

    def update(self, x=None, y=None, rotation=None, scale=None, scale_x=None, scale_y=None):
        if not self.destroyed:
            super().update(x, y, rotation, scale, scale_x, scale_y)


def sprites_from_folder(sprite_folder):
    sprites = []
    for name in os.listdir(os.path.join(Resources.resourcePath, sprite_folder)):
        sprites.append(Sprite(os.path.join(sprite_folder, name)))
    return sprites


def animation_from_folder(sprite_folder, renderer: SpriteRenderer, fps):
    sprites = sprites_from_folder(sprite_folder)
    frames = [Frame(sprites[i], (i + 1) * 1 / fps) for i in range(len(sprites))]
    prop = Property(renderer, "sprite", frames, interpolation=None)
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
    def __init__(self, properties: list[Property], loop=True, play_on_awake=True):
        self.properties = properties
        self.loop = loop
        self.playing = play_on_awake

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, properties):
        self._properties = properties
        self._length = max(max(frame.timestamp for frame in prop.frames) for prop in properties)
        self.local_time = 0

    def update(self, fpsDelta):
        if not self.playing:
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
            self.playing = False
            return

        self.local_time = (self.local_time + fpsDelta) % self._length

    def play(self):
        self.local_time = 0
        self.playing = True


class Animator(Component):
    def __init__(self, animations: dict, state):
        self._state = None
        self._anim = None

        self.animations = animations
        self.state = state

    def update(self, fpsDelta):
        self._anim.update(fpsDelta)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state
        self._anim = self.animations[state]
