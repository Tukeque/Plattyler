VERSION = "1.0.0" # Modified for Plattyler

from traceback import format_exc
from typing import final
from math import floor
from copy import copy
import pygame

class Sprite:
    DO_ROTATION = False

    def __init__(self, texture_index: int, x: float, y: float, z: float, tyler, r: float = 0, rx: float = 0, ry: float = 0, rotate: bool = False):
        self.x, self.y = x, y
        self.z, self.r = z, r
        self.rx, self.ry = rx, ry

        self.tyler = tyler
        self.texture_index = texture_index

        self.DO_ROTATION = rotate

    @final
    def blit_rotate(self, screen: pygame.Surface, image: pygame.Surface, pos: tuple[float, float], origin_pos: tuple[float, float], angle: float): # Made by Rabbid76 on StackOverflow
        # offset from pivot to center
        image_rect = image.get_rect(topleft = (pos[0] - origin_pos[0], pos[1] - origin_pos[1]))
        offset_center_to_pivot: pygame.Vector2 = pygame.math.Vector2(pos) - image_rect.center

        # roatated offset from pivot to center
        rotated_offset = offset_center_to_pivot.rotate(-angle)

        # roatetd image center
        rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

        # get a rotated image
        rotated_image = pygame.transform.rotozoom(image, angle, 1)
        rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

        # rotate and blit the image
        screen.blit(rotated_image, rotated_image_rect)

    def draw(self, screen: pygame.Surface, ox: float = 0, oy: float = 0) -> None:
        """
        If overwrite, remember to multiply by texture_width and texture_height, to add ox and oy and to convert from python coordinates
        """

        if not self.DO_ROTATION:
            screen.blit(self.tyler.textures[self.texture_index], (
                (self.x + ox) * self.tyler.texture_width,
                self.tyler.height - (self.y + 1 + oy) * self.tyler.texture_height
            ))

        else: # do rotation
            self.blit_rotate(screen, self.tyler.textures[self.texture_index], (
                (self.x + ox + 0.5) * self.tyler.texture_width,
                self.tyler.height - (self.y + 1 + oy - 0.5) * self.tyler.texture_height
            ), (
                (self.rx + 0.5) * self.tyler.texture_width,
                (self.ry + 0.5) * self.tyler.texture_height
            ), self.r)

class Scene:
    def loop(self, delta) -> None:
        pass

    def start(self) -> None:
        pass

    def quit(self) -> None:
        pass

    def event(self, event) -> None:
        pass

    def draw(self) -> None:
        pass

class Tyler:
    FPS = 30
    NAME = "Tyler Application"
    RUN = True

    TRANSPARENT_TEXTURE_NAME = "transparent.png"
    HIJACKER_TEXTURE_NAME = "transparent.png"
    DEFAULT_TEXTURE_NAME = "default.png"
    DEFAULT_SCENE_NAME = "main"
    CLEAR_COLOR = (0, 0, 0)
    FULLSCREEN = False

    # Warning!: Messing with these values incorrectly may lead to a broken engine
    DO_BACKGROUNDS = True
    DO_FOREGROUND = True
    DO_HIJACKER = False
    DO_TEXTURES = True
    DO_SPRITES = True
    DO_RESIZE = True
    DO_CLEAR = True
    DO_FPS = True

    TEXTURE_DATA = [
        ("default.png", 1, 1),
        ("transparent.png", 1, 1)
    ]

    @final
    def int_to_xy(self, i: int) -> tuple[int, int]:
        return (i % self.tile_w, i // self.tile_w)

    @final
    def xy_to_int(self, x: int, y: int) -> int:
        return y * self.tile_w + x

    @final
    def get_tile(self, tiles: list[Sprite], x: int, y: int) -> Sprite:
        if x < 0 or x >= self.tile_w or y < 0 or y >= self.tile_h:
            raise IndexError

        return tiles[self.xy_to_int(x, y)]

    @final
    def set_tile(self, tiles: list[Sprite], x: int, y: int, sprite: Sprite) -> None:
        tiles[self.xy_to_int(x, y)] = sprite

    @final
    def fill(self, tiles: list[Sprite], texture_index: int) -> None:
        for i in range(self.length):
            tiles[i] = Sprite(texture_index, self.int_to_xy(i)[0], self.int_to_xy(i)[1], -1, self)

    @final
    def draw(self, x: float, y: float, tiles: list[Sprite], w: int = 0, h: int = 0) -> None:
        if w == h == 0:
            for sprite in tiles:
                sprite.draw(self.screen, x, y)
        else: # custom size
            for i in range(w):
                for j in range(h):
                    tiles[self.xy_to_int(i, j)].draw(self.screen, x, y)

    @final
    def draw_z(self, x: float, y: float, tiles: list[Sprite], old_tiles: list[Sprite], draw_tiles: list[Sprite]) -> None:
        self.regenerate(draw_tiles, tiles, old_tiles)

        for sprite in draw_tiles:
            sprite.draw(self.screen, x, y)

        for i in range(len(tiles)):
            old_tiles[i] = copy(tiles[i])

    @final
    def get_sort_value(self, sprite: Sprite) -> int:
        return sprite.z

    @final
    def regenerate(self, draw_tiles: list[Sprite], tiles: list[Sprite], old_tiles: list[Sprite]) -> None:
        if tiles != old_tiles: # regenerate
            for i in range(len(tiles)):
                draw_tiles[i] = copy(tiles[i])

            draw_tiles.sort(key=self.get_sort_value)

    @final
    def texture(self, texture_name: str) -> int:
        for i, texture in enumerate(self.TEXTURE_DATA):
            if texture[0] == texture_name:
                return i
        raise Exception(f"Cannot find texture {texture_name}")

    @final
    def load_scene(self, name: str) -> None:
        if self.scene != None:
            self.scene.quit()

        self.scene = self.scenes[name]
        self.scene.start()

    @final
    def pygame_screen(self, width: int, height: int, flags: int = 0) -> None:
        self.py_screen = pygame.display.set_mode((width, height), flags | pygame.SCALED, vsync=1)
        self.py_screen.fill(self.CLEAR_COLOR)

        self.width = width
        self.height = height
        self.length = self.tile_w * self.tile_h

        if height > width:
            self.scale = 1 / ((self.base_w / width) * self.tile_w)
        else: # width >= height
            self.scale = 1 / ((self.base_h / height) * self.tile_h)

        self.texture_width = floor(self.base_w * self.scale)
        self.texture_height = floor(self.base_h * self.scale)

        self.ox = (width - self.tile_w * self.texture_width) / 2
        self.oy = (height - self.tile_h * self.texture_height) / 2

        self.screen = pygame.Surface((self.texture_width * self.tile_w, self.texture_height * self.tile_h))

    @final
    def toggle_fullscreen(self) -> None:
        self.set_fullscreen(not self.FULLSCREEN)
    
    @final
    def set_fullscreen(self, x: bool) -> None:
        self.FULLSCREEN = x

        if self.DO_RESIZE:
            if self.FULLSCREEN:
                self.pygame_screen(self.monitor_size[0], self.monitor_size[1], pygame.FULLSCREEN)
                self.generate_textures()
            else:
                self.pygame_screen(self.base_w * self.tile_w, self.base_h * self.tile_h, pygame.RESIZABLE)
                self.generate_textures()

    @final
    def resize(self, width: int, height: int) -> None:
        if self.DO_RESIZE:
            self.pygame_screen(width, height, pygame.RESIZABLE)
        else:
            self.pygame_screen(width, height)

        self.generate_textures()

    @final
    def generate_textures(self) -> None:
        if self.DO_TEXTURES:
            self.textures = [
                pygame.transform.scale(pygame.image.load(texture[0]), (self.texture_width * texture[1], self.texture_height * texture[2])) for texture in self.TEXTURE_DATA
            ]

    @final
    def __init__(self, width: int, height: int, tile_w: int, tile_h: int, scenes: dict[str, Scene]):
        pygame.init()
        pygame.display.set_caption(self.NAME)
        self.clock = pygame.time.Clock() # For syncing the FPS
        info = pygame.display.Info()
        self.monitor_size = (info.current_w, info.current_h)

        self.tile_w = tile_w
        self.tile_h = tile_h
        self.base_w = width // tile_w
        self.base_h = height // tile_h
        self.ox = 0
        self.oy = 0
        self.scale = 1
        self.fps_check = 5

        if self.DO_SPRITES:
            self.sprites: dict[str, Sprite] = {}
        self.resize(width, height)   
        if self.DO_BACKGROUNDS:
            self.backgrounds: list[list[Sprite]] = [
                [None for _ in range(self.length)] for _ in range(4)
            ]
        if self.DO_HIJACKER:
            self.hijacker = Sprite(self.texture(self.HIJACKER_TEXTURE_NAME), -9999, -9999, -9999, self)
        if self.DO_FOREGROUND:
            self.foreground: list[Sprite] = [None for _ in range(self.length)]
            self.draw_foreground: list[Sprite] = [None for _ in range(self.length)]
            self.old_foreground: list[Sprite] = [None for _ in range(self.length)] # don't touch
        
            self.fill(self.foreground, self.texture(self.TRANSPARENT_TEXTURE_NAME))

        self.scenes = scenes
        self.scene = None
        for scene_name in self.scenes:
            self.scenes[scene_name].tyler = self
        self.load_scene(self.DEFAULT_SCENE_NAME)

    @final
    def update(self) -> None:
        if self.DO_FPS:
            if self.FPS != 0:
                delta = self.clock.tick(self.FPS) / 1000 # will make the loop run at the same speed all the time
            else:
                delta = self.clock.tick() / 1000 # no FPS limit

            self.fps_check += 1 * delta
            if self.fps_check >= 2:
                print(f"FPS: {round(1/delta, 1)}")
                self.fps_check = 0
        else:
            delta = self.clock.tick() / 1000

        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.RUN = False
                case pygame.VIDEORESIZE: # can only happen if self.DO_RESIZE is True
                    if not self.FULLSCREEN:
                        self.pygame_screen(event.w, event.h, pygame.RESIZABLE)
                        self.generate_textures()
            self.scene.event(event)

        if self.DO_CLEAR:
            self.screen.fill(self.CLEAR_COLOR)
        self.scene.loop(delta)

        # sprite order
        if self.DO_SPRITES:
            sorted_sprites: list[Sprite] = []
            for key in self.sprites: sorted_sprites.append(copy(self.sprites[key]))
            sorted_sprites.sort(key=self.get_sort_value)

        # draw
        self.scene.draw() # background
        if self.DO_SPRITES:
            for sprite in sorted_sprites: sprite.draw(self.screen) # sprites
        if self.DO_FOREGROUND:
            self.draw_z(0, 0, self.foreground, self.old_foreground, self.draw_foreground) # foreground
        if self.DO_HIJACKER:
            self.hijacker.draw(self.screen)

        self.py_screen.blit(self.screen, (self.ox, self.oy))

        pygame.display.flip()

    @final
    def run(self) -> None:
        try:
            while self.RUN:
                self.update()
        except Exception:
            print(format_exc())
        
        self.scene.quit()
        pygame.quit()
        print("Goodbye!")