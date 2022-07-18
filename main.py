from tyler import Tyler, Sprite, Scene
from math import ceil, floor
from pygame.locals import *
import loader
import pygame

GLOBAL_TEXTURE_DATA = [
    (DIRT := "assets/dirt.png", 1, 1),
    (GRASS := "assets/grass.png", 1, 1),
    (STONE := "assets/stone.png", 1, 1),
    (AIR := "assets/air.png", 1, 1),
    (BUSH := "assets/bush.png", 1, 1),
    (PLAYER := "assets/player.jpg", 1, 1),
    (TRANSPARENT := "assets/transparent.png", 1, 1),
]
X = 0
Y = 1

def cool_effect(num: float) -> float:
    return floor(num) + round((num % 1) * 8) / 8

class Plattyler(Tyler):
    NAME = "Plattyler"
    FPS = 0
    TRANSPARENT_TEXTURE_NAME = "assets/transparent.png"
    DEFAULT_SCENE_NAME = "main"

    DO_FOREGROUND = False
    DO_FPS = True

    TEXTURE_DATA = GLOBAL_TEXTURE_DATA

class Player:
    x = 0
    y = 0

    dx = 0
    dy = 0

    accel = 40
    deaccel = 80
    max_speedx = 10
    max_speedy = 18
    jump = 18.5
    gravity = 40

    coloffsets = [
        (.999, .999),
        (.999, 0),
        (0, .999),
        (0, 0)
    ]

    flooroffests = [
        (0, -0.1),
        (0.999, -0.1)
    ]

    def __init__(self, name: str, x: float, y: float) -> None:
        self.name = name
        self.x, self.y = x, y

class Camera:
    def __init__(self, x: float, y: float, tyler: Tyler) -> None:
        self.x, self.y = x, y
        self.tyler = tyler

        self.old_x = self.x + self.tyler.tile_w
        self.old_y = self.y + self.tyler.tile_h
        self.changed = False

    def get_poses(self) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
        stop_x_off = False
        stop_y_off = False

        if self.x < 0:
            self.x = 0
        elif self.x >= (loader.world["size"][X] - 1) * self.tyler.tile_w:
            self.x = (loader.world["size"][X] - 1) * self.tyler.tile_w
            stop_x_off = True

        if self.y < 0:
            self.y = 0
        elif self.y >= (loader.world["size"][Y] - 1) * self.tyler.tile_h:
            self.y = (loader.world["size"][Y] - 1) * self.tyler.tile_h
            stop_y_off = True

        main_x = floor(self.x / self.tyler.tile_w) * self.tyler.tile_w
        sec_x = main_x + self.tyler.tile_w
        off_x = self.x % self.tyler.tile_w

        main_y = floor(self.y / self.tyler.tile_h) * self.tyler.tile_h
        sec_y = main_y + self.tyler.tile_h
        off_y = self.y % self.tyler.tile_h

        if stop_x_off:
            off_x = 0

        if stop_y_off:
            off_y = 0

        if main_x != self.old_x or main_y != self.old_y:
            self.changed = True
        else:
            self.changed = False

        if sec_x >= (loader.world["size"][X] - 1) * self.tyler.tile_w:
            sec_x = (loader.world["size"][X] - 1) * self.tyler.tile_w

        if sec_y >= (loader.world["size"][Y] - 1) * self.tyler.tile_h:
            sec_y = (loader.world["size"][Y] - 1) * self.tyler.tile_h

        self.old_x = main_x
        self.old_y = main_y

        return ((floor(main_x), floor(main_y)), (floor(sec_x), floor(sec_y)), (-off_x, -off_y))

    def pre_draw(self, blocks: list[str]) -> tuple[float, float]:
        main, sec, off = self.get_poses()

        if self.changed:
            for x in range(self.tyler.tile_w):
                for y in range(self.tyler.tile_h):
                    self.tyler.get_tile(self.tyler.backgrounds[0], x, y).texture_index = self.tyler.texture(blocks[loader.get_tile(main[X] + x, main[Y] + y)])
                    if loader.world["size"][X] > 1: 
                        self.tyler.get_tile(self.tyler.backgrounds[1], x, y).texture_index = self.tyler.texture(blocks[loader.get_tile(sec[X] + x, main[Y] + y)])
                    if loader.world["size"][Y] > 1:
                        self.tyler.get_tile(self.tyler.backgrounds[2], x, y).texture_index = self.tyler.texture(blocks[loader.get_tile(main[X] + x, sec[Y] + y)])
                        self.tyler.get_tile(self.tyler.backgrounds[3], x, y).texture_index = self.tyler.texture(blocks[loader.get_tile(sec[X] + x, sec[Y] + y)])

        return off

class Main(Scene):
    tyler: Tyler

    BLOCKS = [
        AIR,
        GRASS,
        DIRT,
        STONE,
        BUSH
    ]

    def check_tile(self, offx: int, offy: int) -> bool:
        x = floor(self.player.x + offx)
        y = floor(self.player.y + offy)

        if x < 0 or x >= loader.world["size"][X] * self.tyler.tile_w or y < 0 or y >= loader.world["size"][Y] * self.tyler.tile_h:
            return True

        tile = loader.get_tile(x, y)
        if tile in loader.solids:
            return True
        return False

    def check_player_collision(self, offsets) -> bool:
        for offset in offsets:
            if self.check_tile(offset[0], offset[1]):
                return True

        return False

    def do_player_movement(self, delta) -> None:
        keys = pygame.key.get_pressed()
        pressingx = False

        # acceleration
        if keys[K_LEFT]: self.player.dx -= self.player.accel * delta; pressingx = True
        if keys[K_RIGHT]: self.player.dx += self.player.accel * delta; pressingx = True

        # speed capping
        if pressingx:
            if abs(self.player.dx * delta) > self.player.max_speedx * delta:
                self.player.dx = self.player.max_speedx * (self.player.dx / abs(self.player.dx))

        # x velocity & collision
        if self.player.dx != 0:
            iters = ceil(abs(self.player.dx))
            step = self.player.dx / iters * delta

            for _ in range(iters):
                self.player.x += step
                if self.check_player_collision(self.player.coloffsets): # round and break
                    self.player.x = floor(self.player.x) if self.player.dx > 0 else ceil(self.player.x)
                    self.player.dx = 0
                    break

        # y velocity & collision
        if self.player.dy != 0:
            iters = ceil(abs(self.player.dy))
            step = self.player.dy / iters * delta

            for _ in range(iters):
                self.player.y += step
                if self.check_player_collision(self.player.coloffsets): # round and break
                    self.player.y = floor(self.player.y) if self.player.dy > 0 else ceil(self.player.y)
                    self.player.dy = 0
                    break

        if not pressingx: # deacceleration
            if self.player.dx > 0: # has right speed
                self.player.dx -= self.player.deaccel * delta

                if self.player.dx < 0: self.player.dx = 0
            elif self.player.dx < 0: # has left speed
                self.player.dx += self.player.deaccel * delta

                if self.player.dx > 0: self.player.dx = 0
                
        # cap y speed
        if abs(self.player.dy) > self.player.max_speedy:
            self.player.dy = self.player.max_speedy * self.player.dy / abs(self.player.dy)

        # gravity
        if self.player.dy > 0:
            self.player.dy -= self.player.gravity * delta
        elif self.player.dy <= 0:
            self.player.dy -= self.player.gravity * delta

    def start(self) -> None:
        loader.load_world("assets/levels/level00.json")

        self.tyler.fill(self.tyler.backgrounds[0], self.tyler.texture(AIR))
        if loader.world["size"][X] > 1:
            self.tyler.fill(self.tyler.backgrounds[1], self.tyler.texture(AIR))
        if loader.world["size"][Y] > 1:
            self.tyler.fill(self.tyler.backgrounds[2], self.tyler.texture(AIR))
            self.tyler.fill(self.tyler.backgrounds[3], self.tyler.texture(AIR))

        self.player = Player("pepe", 1, 3)
        self.camera = Camera(0, 0, self.tyler)
        self.tyler.sprites["player"] = Sprite(self.tyler.texture(PLAYER), self.player.x, self.player.y, 1, self.tyler)
        self.camera.pre_draw(self.BLOCKS) # first update

    def event(self, event) -> None:
        match event.type:
            case pygame.KEYDOWN:
                if event.key == K_UP and self.check_player_collision(self.player.flooroffests):
                    self.player.dy += self.player.jump

    def draw(self) -> None:
        off = self.off

        if loader.world["size"][Y] > 1: 
            self.tyler.draw(
                off[X] + self.tyler.tile_w,
                off[Y] + self.tyler.tile_h,
            self.tyler.backgrounds[3])

            self.tyler.draw(
                off[X],
                off[Y] + self.tyler.tile_h,
            self.tyler.backgrounds[2])

        if loader.world["size"][X] > 1: 
            self.tyler.draw(
                off[X] + self.tyler.tile_w,
                off[Y],
            self.tyler.backgrounds[1])

        self.tyler.draw(
            off[X],
            off[Y],
        self.tyler.backgrounds[0])

    def loop(self, delta) -> None:
        self.do_player_movement(delta)

        self.camera.x = self.player.x - 7.5
        self.camera.y = self.player.y - 7.5

        self.off = self.camera.pre_draw(self.BLOCKS)

        self.tyler.sprites["player"].x = self.player.x - self.camera.x
        self.tyler.sprites["player"].y = self.player.y - self.camera.y

plattyler: Plattyler = Plattyler(768, 768, 16, 16, {
    "main": Main()
})
plattyler.run()