import sys
import time
from maze import Maze

def read_algorithm_choice():
    """
    Reads the algorithm choice from the user.
    Returns the chosen algorithm as a string.
    """
    while True:
        algo = input("Choose algorithm (BFS, DFS, A*, Greedy, Uniform, Bidirectional): ").lower()
        if algo in ["bfs", "dfs", "a*", "greedy", "uniform", "bidirectional"]:
            return algo
        print("Invalid algorithm. Please choose again.")

def read_heuristic_choice():
    """
    Reads the heuristic choice from the user.
    Returns the chosen heuristic as a string.
    """
    while True:
        heuristic = input("Choose heuristic (Manhattan, Euclidean, Chebyshev): ").lower()
        if heuristic in ["manhattan", "euclidean", "chebyshev"]:
            return heuristic
        print("Invalid heuristic. Please choose again.")

def read_save_gif_choice():
    """
    Reads the user's choice on whether to save an animated GIF of the solving process.
    """
    while True:
        save_gif_input = input("Do you want to save an animated GIF of the solving process? (yes/no): ").lower()
        if save_gif_input in ["yes", "y"]:
            gif_filename = input("Enter GIF filename (e.g., solution.gif): ")
            if not gif_filename.endswith(".gif"):
                gif_filename += ".gif"

            return  True, gif_filename
        elif save_gif_input in ["no", "n"]:
            return False, ""
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

def main():
    # Ensure at least one maze file is provided as a command-line argument
    if len(sys.argv) < 2:
        width = int(input("Enter maze width: "))
        height = int(input("Enter maze height: "))
        
        m = Maze(width=width, height=height)  # Create a new maze with specified dimensions
        algo = read_algorithm_choice()  # Read algorithm choice from user
        if algo in ["a*", "greedy"]:
            heuristic = read_heuristic_choice()
        save_gif, gif_filename = read_save_gif_choice()  # Read GIF saving choice

        print("Algorithm selected:", algo)
        print("Generated Maze:")
        m.print()  # Print the generated maze
        print("Solving...")
        start_time = time.perf_counter()
        if algo in ["a*", "greedy"]:
            m.solve(algo, method=heuristic, save_gif=save_gif)
        else:
            m.solve(algo, save_gif=save_gif)
        end_time = time.perf_counter()
        if save_gif:
            m.save_solution_gif(gif_path=gif_filename)
        print(f"Time taken: {end_time - start_time:.8f} seconds")
        print("States Explored:", m.num_explored)
        print("Cost of Path:", m.co_path)
        print("Solution:")
        m.print()
        m.output_image("maze_solution.png", show_explored=True)  # Save the solution as an image
        save_maze = input("Do you want to save the maze to a file? (yes/no): ").lower()
        if save_maze in ["yes", "y"]:
            filename = input("Enter filename to save the maze (e.g., maze.txt): ")
            if not filename.endswith(".txt"):
                filename += ".txt"
            m.save_to_file(filename)

        

    else:
        algo = read_algorithm_choice()

        # If algorithm requires a heuristic, prompt user to select one
        if algo in ["a*", "greedy"]:
            heuristic = read_heuristic_choice()

        # Ask user if they want to save an animated GIF of the solving process
        save_gif, gif_filename = read_save_gif_choice()
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