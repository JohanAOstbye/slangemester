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

    def choose_move(self):
        chosen_move = self.up
        if self.down.is_safe and self.down.preferrable > chosen_move.preferrable:
            chosen_move = self.down

        if self.left.is_safe and self.left.preferrable > chosen_move.preferrable:
            chosen_move = self.left

        if self.right.is_safe and self.right.preferrable > chosen_move.preferrable:
            chosen_move = self.right

        return chosen_move


# Class for storing move information
# direction: The direction of the move
# is_safe: Whether the move is safe
# preferrable: How preferrable the move is between -10 and 10
class Move:
    def __init__(self, direction, is_safe, preferrable):
        self.direction = direction
        self.is_safe = is_safe
        self.preferrable = preferrable

    def combine(self, other):
        self.is_safe = self.is_safe and other.is_safe
        self.preferrable = (self.preferrable + other.preferrable) / 2
        return self

    def add_preferrable(self, preferrable):
        self.preferrable += preferrable
        return self


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "Slangemesterene",  # TODO: Your Battlesnake Username
        "color": "#993300",  # TODO: Choose color
        "head": "sand-worm",  # TODO: Choose head
        "tail": "round-bum",  # TODO: Choose tail
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
    my_snake = game_state["you"]
    my_head = my_snake["body"][0]  # Coordinates of your head

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
    if not my_move_set.has_safe_moves():
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}

    for snake in game_state["board"]["snakes"]:
        if snake["id"] == my_snake["id"]:
            continue
        my_move_set.combine(to_eat_or_not_to_eat(my_snake, snake))

    food = game_state["board"]["food"]

    for food_item in food:
        food_move_set = MoveSet()

        path_to_food = move_vector(my_head, food_item)

        for snake in game_state["board"]["snakes"]:
            snake_path_to_food = move_vector(snake["body"][0], food_item)
            if abs(snake_path_to_food["x"]) + abs(snake_path_to_food["y"]) < abs(
                path_to_food["x"]
            ) + abs(path_to_food["y"]):
                return MoveSet()
            else:
                # find preferabel direcetion to the food
                if path_to_food["x"] > 0:
                    food_move_set.right.add_preferrable(10)
                if path_to_food["x"] < 0:
                    food_move_set.left.add_preferrable(10)
                if path_to_food["y"] > 0:
                    food_move_set.up.add_preferrable(10)
                if path_to_food["y"] < 0:
                    food_move_set.down.add_preferrable(10)

        my_move_set.combine(food_move_set)

    next_move = my_move_set.choose_move()
    print(f"MOVE {game_state['turn']}: {next_move.direction}")
    return {"move": next_move.direction}


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


def move_vector(origin, destination):
    return {
        "x": destination["x"] - origin["x"],
        "y": destination["y"] - origin["y"],
    }


def to_eat_or_not_to_eat(my_snake, other_snake):
    eat_move_set = MoveSet()
    other_snake_head = other_snake["body"][0]
    my_snake_head = my_snake["body"][0]
    path_to_other_snake = move_vector(my_snake_head, other_snake_head)

    if my_snake["length"] > other_snake["length"]:
        if path_to_other_snake["x"] > 0:
            eat_move_set.right.add_preferrable(10)
        return eat_move_set

    calculated_distance = abs(path_to_other_snake["x"]) + abs(path_to_other_snake["y"])

    if calculated_distance > 2:
        return eat_move_set

    if path_to_other_snake["x"] > 0:
        eat_move_set.right.add_preferrable(10)
    if path_to_other_snake["x"] < 0:
        eat_move_set.left.add_preferrable(10)
    if path_to_other_snake["y"] > 0:
        eat_move_set.up.add_preferrable(10)
    if path_to_other_snake["y"] < 0:
        eat_move_set.down.add_preferrable(10)

    return eat_move_set


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
