import os
import csv
import time
from maze import Maze  # Import Maze class directly

def main():
    maze_files = [
        "maze_examples/maze21.txt",
        "maze_examples/maze31.txt",
        "maze_examples/maze51.txt",
        "maze_examples/maze71.txt",
        "maze_examples/maze91.txt"
    ] # Add all maze files you want to test here
        # Ensure these files are located in the 'maze_examples' directory

    # Ensure the 'maze_examples' directory exists
    if not os.path.exists("maze_examples"):
        print("Error: 'maze_examples' directory not found. Please create it and add your maze files inside.")
        return

    algorithms_to_test = {
        "bfs": [None], # No heuristics required
        "dfs": [None], # No heuristics required
        "uniform": [None], # No heuristics required
        "bidirectional": [None], # No heuristics required
        "a*": ["manhattan", "euclidean", "chebyshev"], # Heuristics for A*
        "greedy": ["manhattan", "euclidean", "chebyshev"], # Heuristics for Greedy
    }

    results = []
    # CSV header
    header = ["Maze File", "Algorithm", "Heuristic", "Time Taken (s)", "States Explored", "Path Cost"]
    results.append(header)

    num_runs_per_test = 1 # Number of runs for each test to get a more accurate average

    for maze_file_path in maze_files:
        if not os.path.exists(maze_file_path):
            print(f"Warning: Maze file '{maze_file_path}' not found. Skipping.")
            # Optionally, add "File Not Found" rows to CSV if you want to track missing files
            for algo, heuristics in algorithms_to_test.items():
                for heuristic in heuristics:
                    results.append([os.path.basename(maze_file_path), algo, heuristic if heuristic else "N/A", "File Not Found", "File Not Found", "File Not Found"])
            continue

        print(f"\n--- Testing on {os.path.basename(maze_file_path)} ---")

        for algorithm, heuristics in algorithms_to_test.items():
            for heuristic in heuristics:
                test_case_name = f"{algorithm}"
                if heuristic:
                    test_case_name += f" ({heuristic})"

                print(f"Running {test_case_name} for {os.path.basename(maze_file_path)}...")

                total_time = 0
                total_states_explored = 0
                total_path_cost = 0
                successful_runs = 0

                for run_count in range(num_runs_per_test):
                    try:
                        # Create and load the Maze object
                        m = Maze(maze_file_path)

                        # Start timing the solving process
                        start_time = time.perf_counter()
                        
                        # Call the solve method directly
                        if algorithm in ["a*", "greedy"]:
                            # Pass heuristic if required
                            m.solve(algorithm, method=heuristic, save_gif=False) # Always 'False' for GIF in quantitative comparisons
                        else:
                            m.solve(algorithm, save_gif=False) # Always 'False' for GIF in quantitative comparisons
                        
                        end_time = time.perf_counter()

                        # Collect metrics directly from the Maze object
                        time_taken = end_time - start_time
                        states_explored = m.num_explored
                        path_cost = m.co_path

                        # Check if a solution was found and metrics are valid
                        if m.solution and time_taken is not None and states_explored is not None and path_cost is not None:
                            total_time += time_taken
                            total_states_explored += states_explored
                            total_path_cost += path_cost
                            successful_runs += 1
                        else:
                            print(f"  --> Solution failed or metrics not valid for {test_case_name} in run {run_count+1}. Maze might be unsolvable or an internal error occurred.")

                    except Exception as e:
                        print(f"  --> An error occurred during {test_case_name} for {os.path.basename(maze_file_path)} in run {run_count+1}: {e}")
                        # Do not increment successful_runs in case of an error

                if successful_runs > 0:
                    avg_time = total_time / successful_runs
                    avg_states_explored = total_states_explored / successful_runs
                    avg_path_cost = total_path_cost / successful_runs

                    row = [
                        os.path.basename(maze_file_path),
                        algorithm,
                        heuristic if heuristic else "N/A",
                        f"{avg_time:.6f}",
                        int(avg_states_explored),
                        int(avg_path_cost)
                    ]
                    results.append(row)
                else:
                    # If all runs failed or no solution was found
                    row = [os.path.basename(maze_file_path), algorithm, heuristic if heuristic else "N/A", "Error", "Error", "Error"]
                    results.append(row)

    csv_filename = "algorithm_comparison_results_direct.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(results)

    print(f"\nComparison data saved to: {csv_filename}")

if __name__ == "__main__":
    main()