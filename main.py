import sys
import time
from maze import Maze

def main():
    # Ensure at least one maze file is provided as a command-line argument
    if len(sys.argv) < 2:
        sys.exit("Usage: python main.py maze.txt")

    # Prompt user to select a search algorithm
    while True:
        algo = (input("Choose algorithm (BFS, DFS, A*, Greedy, Uniform, Bidirectional): ")).lower()
        if algo in ["bfs", "dfs", "a*", "greedy", "uniform", "bidirectional"]:
            break
        print("Invalid algorithm. Please choose again.")

    # If algorithm requires a heuristic, prompt user to select one
    if algo in ["a*", "greedy"]:
        while True:
            heuristic = input("Choose heuristic (Manhattan, Euclidean, Chebyshev): ").lower()
            if heuristic in ["manhattan", "euclidean", "chebyshev"]:
                break
            print("Invalid heuristic. Please choose again.")

    # Ask user if they want to save an animated GIF of the solving process
    while True:
        save_gif_input = input("Do you want to save an animated GIF of the solving process? (yes/no): ").lower()
        if save_gif_input in ["yes", "y"]:
            save_gif = True
            break
        elif save_gif_input in ["no", "n"]:
            save_gif = False
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

    # If GIF saving is enabled, prompt for filename and ensure it ends with .gif
    gif_filename = ""
    if save_gif:
        gif_filename = input("Enter GIF filename (e.g., solution.gif): ")
        if not gif_filename.endswith(".gif"):
            gif_filename += ".gif"

    print("Algorithm selected:", algo)

    # Iterate over all maze files provided as arguments
    for i in range(1, len(sys.argv)):
        m = Maze(sys.argv[i])  # Create Maze instance from file
        print(f"Maze {i}:")
        m.print()              # Print the maze before solving
        print("Solving...")

        # Start timing the solving process
        start_time = time.perf_counter()
        if algo in ["a*", "greedy"]:
            # Pass heuristic if required
            m.solve(algo, method=heuristic, save_gif=save_gif)
        else:
            m.solve(algo, save_gif=save_gif)
        end_time = time.perf_counter()

        # Save animated GIF if requested
        if save_gif:
            m.save_solution_gif(gif_path=f"maze_{i}_{gif_filename}")

        # Output statistics and results
        print(f"Time taken: {end_time - start_time:.8f} seconds")
        print("States Explored:", m.num_explored)
        print("Cost of Path:", m.co_path)
        print("Solution:")
        m.print()
        
        # Save a PNG image of the maze with the solution and explored nodes
        m.output_image(f"maze{i}.png", show_explored=True)

if __name__ == "__main__":
    main()