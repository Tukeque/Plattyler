import json

world = None

solids = [
    1,
    2,
    3
]

def load_world(file_name: str) -> None:
    global world

    f = open(file_name, "r")
    world = json.load(f)

def get_tile(x: int, y: int) -> int:
    return world["map"][-y-1][x]

def set_tile(x: int, y: int, value: int) -> None:
    global world

    world["map"][-y+1][x] = value