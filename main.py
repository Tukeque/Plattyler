from tyler import Tyler, Sprite, Scene
from math import ceil, floor
from pygame.locals import *
from worlds import worlds, solids
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

def cool_effect(num: float) -> float:
    points = [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0]
    offsets = []

    for point in points:
        offsets.append(abs(point - (num % 1)))

    closest = min(offsets)
    result = floor(num) + points[offsets.index(closest)]

    return result

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
    max_speedx = 7
    max_speedy = 20
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

    def __init__(self, name: str, x: int, y: int):
        self.name = name
        self.x, self.y = x, y

class Main(Scene):
    tyler: Tyler

    BLOCKS = [
        AIR,
        GRASS,
        DIRT,
        STONE,
        BUSH
    ]

    def load_world(self, world: str) -> None:
        for x in range(self.tyler.tile_w):
            for y in range(self.tyler.tile_h):
                self.tyler.get_tile(self.tyler.backgrounds[0], x, y).texture_index = self.tyler.texture(self.BLOCKS[worlds[world][-y-1][x]])

    def check_tile(self, offx: int, offy: int) -> bool:
        x = floor(self.player.x + offx)
        y = floor(self.player.y + offy)

        if x < 0 or x >= self.tyler.tile_w or y < 0 or y >= self.tyler.tile_h:
            return True

        tile = self.tyler.get_tile(self.tyler.backgrounds[0], x, y)
        if tile.texture_index in solids:
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
        self.tyler.fill(self.tyler.backgrounds[0], self.tyler.texture(DIRT))
        self.load_world("test2")

        self.player = Player("pepe", 3, 3)
        self.tyler.sprites["player"] = Sprite(self.tyler.texture(PLAYER), self.player.x, self.player.y, 1, self.tyler)

    def event(self, event) -> None:
        match event.type:
            case pygame.KEYDOWN:
                if event.key == K_UP and self.check_player_collision(self.player.flooroffests):
                    self.player.dy += self.player.jump

    def draw(self) -> None:
        self.tyler.draw(0, 0, self.tyler.backgrounds[0])

    def loop(self, delta) -> None:
        self.tyler.sprites["player"].x = cool_effect(self.player.x)
        self.tyler.sprites["player"].y = cool_effect(self.player.y)

        self.do_player_movement(delta)

plattyler: Plattyler = Plattyler(768, 768, 16, 16, {
    "main": Main()
})
plattyler.run()