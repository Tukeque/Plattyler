import pygame
from app import Sprite, Tyler
from worlds import worlds, solids
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT
from math import floor, ceil

world = None

def load_world(name: str) -> None:
    global world

    world = worlds[name]

class Player:
    x = 0
    y = 0

    dx = 0
    dy = 0

    accel = 0.55
    max_speedx = 0.3
    max_speedy = 0.5
    jump = 0.438
    drag = 0.7
    gravity = 1.5

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

class Platformer(Tyler):
    NAME = "Platformer"
    DEFAULT_TEXTURE_NAME = "air.png"
    OUTSIDE_TEXTURE_NAME = "stone.png"
    FPS = 30

    TEXTURE_NAMES = [
        "player.jpg",
        "air.png",
        "grass.png",
        "dirt.png",
        "stone.png",
        "bush.png"
    ]

    BLOCKS = [
        "air.png",
        "grass.png",
        "dirt.png",
        "stone.png",
        "bush.png"
    ]

    def load_map(self) -> None:
        for x in range(self.tile_w):
            for y in range(self.tile_h):
                self.get_tile(x, y).texture_index = self.texture(self.BLOCKS[world[-y-1][x]])

    def check_tile(self, offx: int, offy: int) -> bool:
        x = floor(self.player.x + offx)
        y = floor(self.player.y + offy)

        tile = self.get_tile(x, y)

        if self.BLOCKS.index(self.TEXTURE_NAMES[tile.texture_index]) in solids:
            return True
        return False

    def check_player_collision(self, offsets) -> bool:
        for offset in offsets:
            if self.check_tile(offset[0], offset[1]):
                return True

        return False

    def start(self) -> None:
        load_world("test1")

        self.player = Player("pepe", 4, 3)
        self.sprites["player"] = Sprite(self.texture("player.jpg"), self.player.x, self.player.y, 10, self)

        self.load_map() # todo scrolling maps (requires Tyler update)

    def event(self, event) -> None:
        match event.type:
            case pygame.KEYDOWN:
                if event.key == K_UP and self.check_player_collision(self.player.flooroffests):
                    self.player.dy += self.player.jump

    def do_player_movement(self, delta) -> None:
        keys = pygame.key.get_pressed()
        pressingx = False

        if keys[K_DOWN]: self.player.dy -= self.player.jump * delta #?
        if keys[K_LEFT]: self.player.dx -= self.player.accel * delta; pressingx = True
        if keys[K_RIGHT]: self.player.dx += self.player.accel * delta; pressingx = True

        # x acceleration & collision
        if self.player.dx != 0:
            iters = ceil(abs(self.player.dx))
            step = self.player.dx / iters

            for _ in range(iters):
                self.player.x += step
                if self.check_player_collision(self.player.coloffsets): # round and break
                    self.player.x = floor(self.player.x) if self.player.dx > 0 else ceil(self.player.x)
                    self.player.dx = 0
                    break

        # y acceleration & collision
        if self.player.dy != 0:
            iters = ceil(abs(self.player.dy))
            step = self.player.dy / iters

            for _ in range(iters):
                self.player.y += step
                if self.check_player_collision(self.player.coloffsets): # round and break
                    self.player.y = floor(self.player.y) if self.player.dy > 0 else ceil(self.player.y)
                    self.player.dy = 0
                    break

        # speed capping & drag (only when not moving)
        if pressingx: # cap x speed
            if abs(self.player.dx) > self.player.max_speedx:
                self.player.dx = self.player.max_speedx * (self.player.dx / abs(self.player.dx))
        else: # drag
            self.player.dx *= self.player.drag

        # cap y speed
        if abs(self.player.dy) > self.player.max_speedy:
            self.player.dy = self.player.max_speedy * self.player.dy / abs(self.player.dy)

        # gravity
        if self.player.dy > 0:
            self.player.dy -= self.player.gravity / 2 * delta
        elif self.player.dy <= 0:
            self.player.dy -= self.player.gravity * delta


    def loop(self, delta) -> None:
        self.sprites["player"].x = self.player.x
        self.sprites["player"].y = self.player.y

        self.do_player_movement(delta)

main: Platformer = Platformer(800, 800, 20, 20)
main.run()