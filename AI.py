import copy
import math
import logic

def expectimax_decision(mat, depth: int = 4):
    moves = {
        'w': logic.move_up,
        'a': logic.move_left,
        's': logic.move_down,
        'd': logic.move_right,
    }

    best_move = None
    best_score = -math.inf

    empty_count = len(_empty_cells(mat))
    if empty_count > 8:
        max_depth = 3
    elif empty_count > 4:
        max_depth = 4
    else:
        max_depth = 5


    for move_key, move_fn in moves.items():
        grid_copy = copy.deepcopy(mat)
        new_grid, moved = move_fn(grid_copy)

        if not moved:
            continue

        # Chance layer after player moves (a random tile will be added)
        score = _expectimax_value(new_grid, max_depth - 1, is_chance_node=True)

        if score > best_score:
            best_score = score
            best_move = move_key

    return best_move

def _expectimax_value(grid, depth: int, is_chance_node: bool):
    if depth == 0:
        return _evaluate(grid)

    if is_chance_node:
        empties = _empty_cells(grid)
        if not empties:
            # No spawn possible; just evaluate
            return _evaluate(grid)

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
        # Max node try all moves and take the best value
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


def _evaluate(grid) -> float:
    empties = len(_empty_cells(grid))
    max_tile = max(max(row) for row in grid)

    log_max = math.log(max_tile, 2) if max_tile > 0 else 0

    mono = _monotonicity(grid)
    smooth = _smoothness(grid)
    corner = _max_in_corner_bonus(grid, max_tile)

    # Weights
    return (
        10.0 * empties +
        3.0  * log_max +
        2.5  * mono +
        0.5  * smooth +
        12.0  * corner
    )


def _empty_cells(grid):
    empties = []
    for i in range(4):
        for j in range(4):
            if grid[i][j] == 0:
                empties.append((i, j))
    return empties


def _monotonicity(grid) -> float:
    def line_score(line):
        # Convert tiles to logs to stabilize magnitudes
        logs = [math.log(v, 2) if v > 0 else 0 for v in line]
        inc = sum(max(0, logs[i] - logs[i+1]) for i in range(3))  # decreasing
        dec = sum(max(0, logs[i+1] - logs[i]) for i in range(3))  # increasing
        return -min(inc, dec)

    rows = sum(line_score(row) for row in grid)
    cols = sum(line_score([grid[r][c] for r in range(4)]) for c in range(4))
    return rows + cols


def _smoothness(grid) -> float:
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

def _max_in_corner_bonus(grid, max_tile) -> float:
    corners = [(0,0), (0,3), (3,0), (3,3)]
    for (r, c) in corners:
        if grid[r][c] == max_tile:
            return 1.0
    return 0.0