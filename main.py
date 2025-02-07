# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com

import random
import typing


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "Slangemesterene",  # TODO: Your Battlesnake Username
        "color": "#888888",  # TODO: Choose color
        "head": "default",  # TODO: Choose head
        "tail": "default",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    my_move_set = MoveSet()

    # We've included code to prevent your Battlesnake from moving backwards
    my_head = game_state["you"]["body"][0]  # Coordinates of your head

    # TODO: Step 1 - Prevent your Battlesnake from moving out of bounds
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]

    if my_head["x"] == 0:
        my_move_set.left.is_safe = False
    if my_head["x"] == board_width - 1:
        my_move_set.right.is_safe = False
    if my_head["y"] == 0:
        my_move_set.down.is_safe = False
    if my_head["y"] == board_height - 1:
        my_move_set.up.is_safe = False

    for snake in game_state["board"]["snakes"]:
        my_move_set.combine(collides_with_snake(my_head, snake))

    # Are there any safe moves left?
    if my_move_set.has_safe_moves():
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}

    food = game_state["board"]["food"]

    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}


def collides_with_snake(my_head, snake):
    sanke_move_set = MoveSet()

    for body_part in snake["body"]:
        if my_head["y"] + 1 == body_part["y"] and my_head["x"] == body_part["x"]:
            sanke_move_set.up.is_safe = False
        elif my_head["y"] - 1 == body_part["y"] and my_head["x"] == body_part["x"]:
            sanke_move_set.down.is_safe = False
        elif my_head["x"] + 1 == body_part["x"] and my_head["y"] == body_part["y"]:
            sanke_move_set.right.is_safe = False
        elif my_head["x"] - 1 == body_part["x"] and my_head["y"] == body_part["y"]:
            sanke_move_set.left.is_safe = False
    return sanke_move_set


def update_move(first_move_set, second_move_set):

    return {
        "up": update_move_direction(first_move_set["up"], second_move_set["up"]),
        "down": update_move_direction(first_move_set["down"], second_move_set["down"]),
        "left": update_move_direction(first_move_set["left"], second_move_set["left"]),
        "right": update_move_direction(
            first_move_set["right"], second_move_set["right"]
        ),
    }


def update_move_direction(first_move_direction, second_move_direction):
    return {
        "safe": first_move_direction["safe"] and second_move_direction["safe"],
        "preferrable": (
            first_move_direction["preferrable"] + second_move_direction["preferrable"]
        )
        / 2,
    }


def eat_or_not_to_eat(my_snake, other_snake):
    if my_snake["length"] > other_snake["length"]:
        return {"up": False, "down": False, "left": False, "right": False}
    other_snake_head = other_snake["body"][0]
    my_snake_head = my_snake["body"][0]

    calculated_distance = abs(my_snake_head["x"] - other_snake_head["x"]) + abs(
        my_snake_head["y"] - other_snake_head["y"]
    )
    if calculated_distance > 2:
        return {"up": False, "down": False, "left": False, "right": False}

    if my_snake_head["x"] == other_snake_head["x"]:
        if my_snake_head["y"] > other_snake_head["y"]:
            return {"up": False, "down": True, "left": False, "right": False}
        else:
            return {"up": True, "down": False, "left": False, "right": False}
    if my_snake_head["y"] == other_snake_head["y"]:
        if my_snake_head["x"] > other_snake_head["x"]:
            return {"up": False, "down": False, "left": False, "right": True}
        else:
            return {"up": False, "down": False, "left": True, "right": False}
    return {"up": False, "down": False, "left": False, "right": False}


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})


class MoveSet:
    def __init__(self):
        self.up = Move("up", True, 0)
        self.down = Move("down", True, 0)
        self.left = Move("left", True, 0)
        self.right = Move("right", True, 0)

    def combine(self, other):
        self.up = self.up.combine(other.up)
        self.down = self.down.combine(other.down)
        self.left = self.left.combine(other.left)
        self.right = self.right.combine(other.right)

    def has_safe_moves(self):
        return (
            self.up.is_safe
            or self.down.is_safe
            or self.left.is_safe
            or self.right.is_safe
        )


class Move:
    def __init__(self, direction, is_safe, preferrable):
        self.direction = direction
        self.is_safe = is_safe
        self.preferrable = preferrable

    def combine(self, other):
        self.is_safe = self.is_safe and other.is_safe
        self.preferrable = (self.preferrable + other.preferrable) / 2
        return self
