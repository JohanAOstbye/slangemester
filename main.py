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

    def __str__(self):
        return f"Up: {self.up.preferrable}, Down: {self.down.preferrable}, Left: {self.left.preferrable}, Right: {self.right.preferrable}"

    def choose_move(self):
        moves = [self.up, self.down, self.left, self.right]
        moves = sorted(moves, key=lambda x: x.preferrable, reverse=True)
        print(f"Moves: {self}")
        for move in moves:
            if move.is_safe:
                return move

        return moves[0]


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

    def add_preferrable(self, preferrable, message=""):
        print(f"Adding {preferrable} to {self.direction} because {message}")
        self.preferrable += preferrable
        return self

    def __str__(self):
        return f"{self.direction}: {self.preferrable}"


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
        my_move_set.combine(
            evaluate_food(my_snake, food_item, game_state["board"]["snakes"])
        )
        
    # my_move_set.combine(evaluate_next_turn(my_snake, game_state["board"]["snakes"]))
    
    #aim towards the center with preferrable 3
    if my_head["x"] < 5:
        my_move_set.right.add_preferrable(3, "center")
    if my_head["x"] > 5:
        my_move_set.left.add_preferrable(3, "center")
    if my_head["y"] < 5:
        my_move_set.up.add_preferrable(3, "center")
    if my_head["y"] > 5:
        my_move_set.down.add_preferrable(3, "center")

    next_move = my_move_set.choose_move()
    print(f"MOVE {game_state['turn']}: {next_move.direction}")
    return {"move": next_move.direction}


# Function for evaluating the next turn where it prefers to have 2 avaliable moves, then 3, then 1
def evaluate_next_turn(my_snake, snakes):
    next_turn_move_set = MoveSet()

    # simulating the next turn

    # all snakes cordinates
    taken_positions = []
    for snake in snakes:
        taken_positions += snake["body"]

    possible_positions = []

    for my_move in ["up", "down", "left", "right"]:
        next_head = {
            "x": my_snake["body"][0]["x"],
            "y": my_snake["body"][0]["y"],
        }
        if my_move == "up":
            next_head["y"] += 1
        if my_move == "down":
            next_head["y"] -= 1
        if my_move == "left":
            next_head["x"] -= 1
        if my_move == "right":
            next_head["x"] += 1

        if (
            next_head["x"] < 0
            or next_head["x"] >= 11
            or next_head["y"] < 0
            or next_head["y"] >= 11
        ):
            continue

        if next_head in taken_positions:
            continue
        taken_positions.append(next_head)

        my_next_snake = my_snake.copy()
        my_next_snake["body"].insert(0, next_head)
        my_next_snake["body"].pop()

        for snake in snakes:
            if snake["id"] == my_snake["id"]:
                continue
            for other_snake_move in ["up", "down", "left", "right"]:
                other_snake_next_head = {
                    "x": snake["body"][0]["x"],
                    "y": snake["body"][0]["y"],
                }
                if other_snake_move == "up":
                    other_snake_next_head["y"] += 1
                if other_snake_move == "down":
                    other_snake_next_head["y"] -= 1
                if other_snake_move == "left":
                    other_snake_next_head["x"] -= 1
                if other_snake_move == "right":
                    other_snake_next_head["x"] += 1

                if other_snake_next_head in taken_positions:
                    continue

                snake_next_snake = snake.copy()
                snake_next_snake["body"].insert(0, other_snake_next_head)
                snake_next_snake["body"].pop()

                possible_positions.append((my_move, my_next_snake, snake_next_snake))

    # calualte the amount of possible moves
    possible_moves = [
        {
            "move": "up",
            "my_moves_amount": [],
            "other_snake_moves_amount": [],
        },
        {
            "move": "down",
            "my_moves_amount": [],
            "other_snake_moves_amount": [],
        },
        {
            "move": "left",
            "my_moves_amount": [],
            "other_snake_moves_amount": [],
        },
        {
            "move": "right",
            "my_moves_amount": [],
            "other_snake_moves_amount": [],
        },
    ]
    for position in possible_positions:
        my_move = position[0]
        my_next_snake = position[1]
        snake_next_snake = position[2]
        possition_takenpositions = taken_positions.copy()
        possition_takenpositions.append(my_next_snake["body"][0])

        # if head is in the same position
        if my_next_snake["body"][0] == snake_next_snake["body"][0]:
            print("Head to head")
            continue

        my_possible_moves = 4
        other_snake_possible_moves = 4
        for new_move in ["up", "down", "left", "right"]:
            my_next_head = {
                "x": my_next_snake["body"][0]["x"],
                "y": my_next_snake["body"][0]["y"],
            }
            other_snake_next_head = {
                "x": snake_next_snake["body"][0]["x"],
                "y": snake_next_snake["body"][0]["y"],
            }
            if new_move == "up":
                my_next_head["y"] += 1
                other_snake_next_head["y"] += 1
            if new_move == "down":
                my_next_head["y"] -= 1
                other_snake_next_head["y"] -= 1
            if new_move == "left":
                my_next_head["x"] -= 1
                other_snake_next_head["x"] -= 1
            if new_move == "right":
                my_next_head["x"] += 1
                other_snake_next_head["x"] += 1

            if my_next_head in possition_takenpositions:
                my_possible_moves -= 1
            if other_snake_next_head in possition_takenpositions:
                other_snake_possible_moves -= 1

        for possible_move in possible_moves:
            if possible_move["move"] == my_move:
                possible_move["my_moves_amount"].append(my_possible_moves)
                possible_move["other_snake_moves_amount"].append(
                    other_snake_possible_moves
                )

    # get the average amount of moves for each move
    for possible_move in possible_moves:
        
        my_average = 0
        if len(possible_move["my_moves_amount"]) != 0:
            my_average = sum(possible_move["my_moves_amount"]) / len(possible_move["my_moves_amount"])
        # other_snake_average = sum(possible_move["other_snake_moves_amount"]) / len(possible_move["other_snake_moves_amount"])
        match possible_move["move"]:
            case "up":
                if my_average == 0:
                    next_turn_move_set.up.add_preferrable(-100, "dead")
                if my_average < 1.7:
                    next_turn_move_set.up.add_preferrable(-7, "blocked")
                elif my_average > 2.5:
                    next_turn_move_set.up.add_preferrable(3, "open")
                else:
                    next_turn_move_set.up.add_preferrable(7, "open -yes")
            case "down":
                if my_average == 0:
                    next_turn_move_set.down.add_preferrable(-100, "dead")
                if my_average < 1.7:
                    next_turn_move_set.down.add_preferrable(-7, "blocked")
                elif my_average > 2.5:
                    next_turn_move_set.down.add_preferrable(3, "open")
                else:
                    next_turn_move_set.down.add_preferrable(7, "open -yes")
            case "left":
                if my_average == 0:
                    next_turn_move_set.left.add_preferrable(-100, "dead")
                if my_average < 1.7:
                    next_turn_move_set.left.add_preferrable(-7, "blocked")
                elif my_average > 2.5:
                    next_turn_move_set.left.add_preferrable(3, "open")
                else:
                    next_turn_move_set.left.add_preferrable(7, "open -yes")
            case "right":
                if my_average == 0:
                    next_turn_move_set.right.add_preferrable(-100, "dead")
                if my_average < 1.7:
                    next_turn_move_set.right.add_preferrable(-7, "blocked")
                elif my_average > 2.5:
                    next_turn_move_set.right.add_preferrable(3, "open")
                else:
                    next_turn_move_set.right.add_preferrable(7, "open -yes")
                    
    return next_turn_move_set


def evaluate_food(my_snake, food, snakes):
    food_move_set = MoveSet()

    path_to_food = move_vector(my_snake["body"][0], food)

    for snake in snakes:
        if snake["id"] == my_snake["id"]:
            continue

        snake_path_to_food = move_vector(snake["body"][0], food)
        if abs(snake_path_to_food["x"]) + abs(snake_path_to_food["y"]) < abs(
            path_to_food["x"]
        ) + abs(path_to_food["y"]):
            return MoveSet()
        else:
            # find preferabel direcetion to the food
            if path_to_food["x"] > 0:
                food_move_set.right.add_preferrable(5, "food")
            if path_to_food["x"] < 0:
                food_move_set.left.add_preferrable(5, "food")
            if path_to_food["y"] > 0:
                food_move_set.up.add_preferrable(5, "food")
            if path_to_food["y"] < 0:
                food_move_set.down.add_preferrable(5, "food")

    return food_move_set


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
    calculated_distance = abs(path_to_other_snake["x"]) + abs(path_to_other_snake["y"])
    if calculated_distance > 2:
        return eat_move_set

    win = -1
    if my_snake["length"] > other_snake["length"]:
        win = 1

    pref = 10*win
    if path_to_other_snake["x"] > 0:
        eat_move_set.right.add_preferrable(pref, "killing")
    if path_to_other_snake["x"] < 0:
        eat_move_set.left.add_preferrable(pref, "killing")
    if path_to_other_snake["y"] > 0:
        eat_move_set.up.add_preferrable(pref, "killing")
    if path_to_other_snake["y"] < 0:
        eat_move_set.down.add_preferrable(pref, "killing")

    return eat_move_set

# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
