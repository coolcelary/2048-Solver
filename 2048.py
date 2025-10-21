import logic
import sys

# Cross-platform single-key input setup
try:
    import msvcrt  # Windows
    def get_key():
        return msvcrt.getch().decode('utf-8')
except ImportError:
    import termios
    import tty

    def get_key():
        """Read one character without pressing Enter (Linux/macOS)."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


def has_empty_cell(mat):
    """Return True if there is at least one zero in the grid."""
    return any(0 in row for row in mat)


if __name__ == '__main__':

    # Initialize the matrix
    mat = logic.start_game()

    while True:
        print("\nCurrent Board:")
        for row in mat:
            print('\t'.join(str(num) for num in row))
        print()

        print("Press a key (W/A/S/D to move, Q to quit): ", end='', flush=True)
        x = get_key()
        print(x.upper())

        if x.lower() == 'q':
            print("Game exited by user.")
            break

        prev_mat = [row.copy() for row in mat]
        moved = False

        # Movement controls
        if x.lower() == 'w':
            mat, moved = logic.move_up(mat)
        elif x.lower() == 's':
            mat, moved = logic.move_down(mat)
        elif x.lower() == 'a':
            mat, moved = logic.move_left(mat)
        elif x.lower() == 'd':
            mat, moved = logic.move_right(mat)
        else:
            print("Invalid key pressed.")
            continue

        # If the move produced a change, spawn a new tile (usual behavior)
        if moved:
            logic.add_new_2(mat)
        else:
            # Optional: still spawn new tile if there is space and you want continuous spawning
            if has_empty_cell(prev_mat):
                logic.add_new_2(mat)

        # ✅ Always check current state, even if move didn’t change the board
        status = logic.get_current_state(mat)

        if status == 'WON':
            print("\nYou reached 2048! 🎉 You won!")
            break
        elif status == 'LOST':
            print("\nNo more moves left. Game Over!")
            break
