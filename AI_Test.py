"""
This module implements AI logic for the 2048 game using the Expectimax algorithm.
It interacts with the game mechanics defined in logic.py.

You can import this into 2048.py and call:
    move = expectimax_decision(mat)
to let the AI choose the best move automatically.
"""

import copy
import math
import logic

# -----------------------------
# Public entry point
# -----------------------------

def expectimax_decision(mat, depth: int = 4):
    """
    Returns the best move ('w', 'a', 's', 'd') for the given board state using Expectimax.
    If no moves are possible, returns None.
    """
    moves = {
        'w': logic.move_up,
        'a': logic.move_left,
        's': logic.move_down,
        'd': logic.move_right,
    }

    best_move = None
    best_score = -math.inf

    empty_count = len(_empty_cells(mat))
    if empty_count > 6:
        max_depth = 3
    elif empty_count > 3:
        max_depth = 4
    else:
        max_depth = 5


    for move_key, move_fn in moves.items():
        grid_copy = copy.deepcopy(mat)
        new_grid, moved = move_fn(grid_copy)

        if not moved:
            continue  # skip illegal moves that don't change the grid

        # Chance layer after player moves (a random tile will be added)
        score = _expectimax_value(new_grid, max_depth - 1, is_chance_node=True)

        if score > best_score:
            best_score = score
            best_move = move_key

    return best_move


# -----------------------------
# Core Expectimax
# -----------------------------

def _expectimax_value(grid, depth: int, is_chance_node: bool):
    """
    Recursive expectimax evaluation.
    - grid: current board (list[list[int]])
    - depth: remaining depth
    - is_chance_node: if True, we aggregate over random tile spawns; else we choose best move.
    """
    if depth == 0:
        return _evaluate(grid)

    if is_chance_node:
        empties = _empty_cells(grid)
        if not empties:
            # No spawn possible; just evaluate
            return _evaluate(grid)

        # In the user's logic.py, add_new_2 only spawns 2s.
        # We'll model that exactly. If you later
        # add 4s in logic.py, adjust `candidates` accordingly (e.g., [(2, 0.9), (4, 0.1)]).
        candidates = [(2, 0.9), (4, 0.1)]

        expected = 0.0
        p_cell = 1.0 / len(empties)  # equal chance to pick any empty cell
        for (r, c) in empties:
            for tile, p_tile in candidates:
                tmp = copy.deepcopy(grid)
                tmp[r][c] = tile
                val = _expectimax_value(tmp, depth - 1, is_chance_node=False)
                expected += p_cell * p_tile * val
        return expected

    else:
        # Max (player) node: try all moves and take the best value
        best = -math.inf
        for move_fn in (logic.move_up, logic.move_left, logic.move_down, logic.move_right):
            tmp = copy.deepcopy(grid)
            new_grid, moved = move_fn(tmp)
            if not moved:
                continue
            val = _expectimax_value(new_grid, depth - 1, is_chance_node=True)
            if val > best:
                best = val
        # If no moves possible, evaluate current grid
        return best if best != -math.inf else _evaluate(grid)


# -----------------------------
# Heuristic Evaluation
# -----------------------------

def _evaluate(grid) -> float:
    """
    Heuristic score combining several signals known to work well for 2048:
    - number of empty cells (more flexibility)
    - max tile magnitude (encourages growth)
    - monotonicity along rows/cols (encourages sorted, snake-like boards)
    - smoothness (neighboring cells similar -> easier merges)
    - corner bias for max tile (keeps big tile parked)
    """
    empties = len(_empty_cells(grid))
    max_tile = max(max(row) for row in grid)

    # Normalize logs to keep scales reasonable
    log_max = math.log(max_tile, 2) if max_tile > 0 else 0

    mono = _monotonicity(grid)
    smooth = _smoothness(grid)
    corner = _max_in_corner_bonus(grid, max_tile)

    # Weighted sum (tuned with simple trial; feel free to tweak)
    return (
        12.0 * empties +
        2.0  * log_max +
        1.8  * mono +
        0.3  * smooth +
        8.0  * corner
    )


def _empty_cells(grid):
    empties = []
    for i in range(4):
        for j in range(4):
            if grid[i][j] == 0:
                empties.append((i, j))
    return empties


def _monotonicity(grid) -> float:
    """
    Reward boards that are monotonic along rows/cols (values steadily increase or decrease).
    We compute both directions and take the maximum for rows and columns.
    """
    def line_score(line):
        # Convert tiles to logs to stabilize magnitudes
        logs = [math.log(v, 2) if v > 0 else 0 for v in line]
        inc = sum(max(0, logs[i] - logs[i+1]) for i in range(3))  # decreasing
        dec = sum(max(0, logs[i+1] - logs[i]) for i in range(3))  # increasing
        return -min(inc, dec)  # penalize the "less monotone" direction

    rows = sum(line_score(row) for row in grid)
    cols = sum(line_score([grid[r][c] for r in range(4)]) for c in range(4))
    return rows + cols


def _smoothness(grid) -> float:
    """
    Penalize large differences between neighboring tiles.
    """
    penalty = 0.0
    for i in range(4):
        for j in range(4):
            if grid[i][j] == 0: 
                continue
            v = math.log(grid[i][j], 2)
            # Right neighbor
            if j + 1 < 4 and grid[i][j+1] != 0:
                penalty += abs(v - math.log(grid[i][j+1], 2))
            # Down neighbor
            if i + 1 < 4 and grid[i+1][j] != 0:
                penalty += abs(v - math.log(grid[i+1][j], 2))
    return -penalty / 16.0


#def _max_in_corner_bonus(grid, max_tile) -> float:
    # prefer bottom-right corner specifically
   # return 1.0 if grid[0][0] == max_tile else 0.0

def _max_in_corner_bonus(grid, max_tile) -> float:
    corners = [(0,0), (0,3), (3,0), (3,3)]
    for (r, c) in corners:
        if grid[r][c] == max_tile:
            return 1.0
    return 0.0