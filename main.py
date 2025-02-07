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

    is_move_safe = {"up": True, "down": True, "left": True, "right": True}

    # We've included code to prevent your Battlesnake from moving backwards
    my_head = game_state["you"]["body"][0]  # Coordinates of your head

    # TODO: Step 1 - Prevent your Battlesnake from moving out of bounds
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]

    if my_head["x"] == 0:
        is_move_safe["left"] = False
    if my_head["x"] == board_width - 1:
        is_move_safe["right"] = False
    if my_head["y"] == 0:
        is_move_safe["down"] = False
    if my_head["y"] == board_height - 1:
        is_move_safe["up"] = False

    for snake in game_state["board"]["snakes"]:
        is_snake_move_safe = collides_with_snake(my_head, snake)
        is_move_safe = update_is_safe_move(is_move_safe, is_snake_move_safe)

    # Are there any safe moves left?
    safe_moves = []
    for move, is_safe in is_move_safe.items():
        if is_safe:
            safe_moves.append(move)

    if len(safe_moves) == 0:
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}

    # Choose a random move from the safe ones
    next_move = random.choice(safe_moves)

    # TODO: Step 4 - Move towards food instead of random, to regain health and survive longer
    # food = game_state['board']['food']

    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}


def collides_with_snake(my_head, snake):
    is_move_safe = {"up": True, "down": True, "left": True, "right": True}
    for body_part in snake["body"]:
        if my_head["y"] + 1 == body_part["y"] and my_head["x"] == body_part["x"]:
            is_move_safe["up"] = False
        elif my_head["y"] - 1 == body_part["y"] and my_head["x"] == body_part["x"]:
            is_move_safe["down"] = False
        elif my_head["x"] + 1 == body_part["x"] and my_head["y"] == body_part["y"]:
            is_move_safe["right"] = False
        elif my_head["x"] - 1 == body_part["x"] and my_head["y"] == body_part["y"]:
            is_move_safe["left"] = False
    return is_move_safe


def update_is_safe_move(first_is_safe_move, second_is_safe_move):
    return {
        "up": first_is_safe_move["up"] and second_is_safe_move["up"],
        "down": first_is_safe_move["down"] and second_is_safe_move["down"],
        "left": first_is_safe_move["left"] and second_is_safe_move["left"],
        "right": first_is_safe_move["right"] and second_is_safe_move["right"],
    }


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
