"""
This module implements AI logic for the 2048 game using the Expectimax algorithm.
It interacts with the game mechanics defined in logic.py.

You can import this into 2048.py and call:
    move = ai.expectimax_decision(mat)
to let the AI choose the best move automatically.
"""

import logic
import copy
import math
import random


def expectimax_decision(mat, depth=3):
    """
    Returns the best move ('w', 'a', 's', 'd') for the given board state.
    This is the main entry point for the AI.
    The Expectimax search and evaluation logic will be implemented inside.
    """
    # TODO: implement your Expectimax logic here
    # You can start by trying each possible move and evaluating the resulting state

    # Example structure:
    possible_moves = {
        'w': logic.move_up,
        'a': logic.move_left,
        's': logic.move_down,
        'd': logic.move_right
    }

    best_move = None
    best_score = -math.inf

    for move_key, move_func in possible_moves.items():
        temp = copy.deepcopy(mat)
        new_board, moved = move_func(temp)

        if not moved:
            continue  # skip invalid moves

        # Simulate adding a new tile (the "chance" layer)
        # You may call a helper function like "expectimax_value(new_board, depth - 1)"
        score = evaluate_board(new_board)  # <-- replace with expectimax_value() later

        if score > best_score:
            best_score = score
            best_move = move_key

    # If no move is possible, just return None
    return best_move


def evaluate_board(mat):
    """
    A simple heuristic evaluation function for the board.
    You can make this more complex later (smoothness, monotonicity, empty tiles, etc.)
    For now, returns a basic score.
    """
    # Create a weighted graph of the game board. Exponentially decrease the weight of tiles from one corner. This will force the algorithm
    # to keep tiles in one corner


    empty_cells = sum(row.count(0) for row in mat)
    max_tile = max(max(row) for row in mat)
    return empty_cells + math.log(max_tile, 2)  # placeholder heuristic


# Example placeholder for a recursive function
def expectimax_value(mat, depth, is_chance_node):
    """
    Recursive Expectimax function (to be implemented).
    - mat: current board
    - depth: current search depth
    - is_chance_node: True if this node represents a random tile being added
    """
    # TODO: implement the full expectimax recursion logic here
    pass
