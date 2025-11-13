import subprocess
import re
import csv
import time
import os

GAME_SCRIPT = "2048.py"
NUM_RUNS = 25
BASE_NAME = "ai_test_results"

# Find next available file name
def get_next_filename(base_name, ext=".csv"):
    i = 1
    while True:
        filename = f"{base_name}_{i}{ext}"
        if not os.path.exists(filename):
            return filename
        i += 1

OUTPUT_CSV = get_next_filename(BASE_NAME)

results = []
total_start_time = time.time()

for i in range(NUM_RUNS):
    print(f"\n--- Running Game {i+1}/{NUM_RUNS} ---")
    game_start = time.time()

    # Run the game in AI mode (simulate typing "ai" when prompted)
    process = subprocess.run(
        ["python3", GAME_SCRIPT],
        input="ai\n",
        text=True,
        capture_output=True
    )

    output = process.stdout

    # Extract the final board
    board_lines = re.findall(r'^\d+.*$', output, re.MULTILINE)
    highest_tile = 0
    for line in board_lines:
        nums = [int(x) for x in re.findall(r'\d+', line)]
        if nums:
            highest_tile = max(highest_tile, max(nums))

    # Determine result based on highest tile
    result = "Win" if highest_tile >= 2048 else "Loss"

    # Track time per game
    game_end = time.time()
    game_duration = game_end - game_start

    print(f"Result: {result}, Highest Tile: {highest_tile}, Time: {game_duration:.2f}s")
    results.append((i + 1, result, highest_tile, round(game_duration, 2)))

# Calculate totals
total_end_time = time.time()
total_duration = total_end_time - total_start_time
wins = sum(1 for _, r, _, _ in results if r == "Win")
losses = NUM_RUNS - wins
win_rate = (wins / NUM_RUNS) * 100

# Print summary to console
print(f"\nCompleted {NUM_RUNS} runs.")
print(f"Wins: {wins}, Losses: {losses}")
print(f"Win Rate: {win_rate:.2f}%")
print(f"Total Time: {total_duration:.2f}s")
print(f"Results saved to {OUTPUT_CSV}")

# Save all results + summary to CSV
with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Game", "Result", "Highest Tile", "Game Time (s)"])
    writer.writerows(results)
    writer.writerow([])
    writer.writerow(["Summary"])
    writer.writerow(["Completed Runs", NUM_RUNS])
    writer.writerow(["Wins", wins])
    writer.writerow(["Losses", losses])
    writer.writerow(["Win Rate (%)", f"{win_rate:.2f}"])
    writer.writerow(["Total Time (s)", round(total_duration, 2)])
