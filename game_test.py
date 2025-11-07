import subprocess
import re
import csv

# Configuration
GAME_SCRIPT = "2048.py"  # Replace with your actual filename
NUM_RUNS = 50             # Number of games to run
OUTPUT_CSV = "ai_test_results.csv"

results = []

for i in range(NUM_RUNS):
    print(f"\n--- Running Game {i+1}/{NUM_RUNS} ---")
    
    # Run the game in AI mode (simulate typing "ai" when prompted)
    process = subprocess.run(
        ["python3", GAME_SCRIPT],
        input="ai\n",          # feeds "ai" to the game's input prompt
        text=True,
        capture_output=True
    )

    output = process.stdout

    # Extract the final board
    # Matches lines with numbers separated by tabs or spaces
    board_lines = re.findall(r'^\d+.*$', output, re.MULTILINE)
    highest_tile = 0
    for line in board_lines:
        nums = [int(x) for x in re.findall(r'\d+', line)]
        if nums:
            highest_tile = max(highest_tile, max(nums))
    
    # Determine result
    if "You won" in output:
        result = "Win"
    elif "Game Over" in output:
        result = "Loss"
    else:
        result = "Unknown"
    
    print(f"Result: {result}, Highest Tile: {highest_tile}")
    results.append((i + 1, result, highest_tile))

# Save all results to CSV
with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Game", "Result", "Highest Tile"])
    writer.writerows(results)

# Print summary
wins = sum(1 for _, r, _ in results if r == "Win")
print(f"\nCompleted {NUM_RUNS} runs.")
print(f"Wins: {wins}, Losses: {NUM_RUNS - wins}")
print(f"Win Rate: {wins / NUM_RUNS * 100:.2f}%")
print(f"Results saved to {OUTPUT_CSV}")
