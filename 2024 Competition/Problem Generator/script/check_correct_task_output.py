import argparse
import sys

def load_map(filepath):
    """Load a Moving AI .map file."""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    width = None
    height = None
    map_start_idx = None

    for i, line in enumerate(lines):
        if line.lower().startswith("width"):
            width = int(line.split()[1])
        elif line.lower().startswith("height"):
            height = int(line.split()[1])
        elif line.lower() == "map":
            map_start_idx = i + 1
            break

    if width is None or height is None or map_start_idx is None:
        raise ValueError("Invalid .map file: missing width/height/map header.")

    grid_lines = lines[map_start_idx:]
    if len(grid_lines) != height:
        raise ValueError(f"Map height mismatch: expected {height}, got {len(grid_lines)}.")
    if not all(len(line) == width for line in grid_lines):
        raise ValueError("Some map lines do not match the specified width.")

    grid = [list(line) for line in grid_lines]
    return grid, width, height


def load_tasks(filepath):
    """
    Load tasks from a file.
    Returns a list of lists of flattened indices (one list per line).
    """
    tasks = []
    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    for line in lines[2:]:  # skip first line (version) and second line (number of tasks)
        if line.startswith("#") or not line:
            continue
        try:
            loc_part, _ = line.split(";")  # ignore deadline
            indices = [int(idx) for idx in loc_part.split(",")]
            tasks.append(indices)
        except Exception as e:
            print(f"Skipping invalid line: {line} ({e})")
    return tasks


def flattened_to_coords(index, width, height):
    """Convert a flattened index to (row, col)."""
    if index < 0 or index >= width * height:
        raise ValueError(f"Index {index} out of range for grid size {width}x{height}.")
    row = index // width
    col = index % width
    return row, col


def check_tasks(grid, width, height, tasks):
    """
    Check if all indices in each task are valid (not walls).
    Returns list of tuples: (line_number, indices_list, all_ok)
    """
    results = []
    for line_num, indices in enumerate(tasks, start=1):
        all_ok = True
        for idx in indices:
            try:
                row, col = flattened_to_coords(idx, width, height)
                if grid[row][col] == "@":
                    all_ok = False
                    break
            except ValueError:
                all_ok = False
                break
        results.append((line_num, indices, all_ok))
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Check if all task locations (flattened indices) are on valid cells in a map and save results."
    )
    parser.add_argument("map_file", help="Path to the .map file.")
    parser.add_argument("task_file", help="Path to the task file.")
    parser.add_argument("output_file", help="Path to save the results.")

    args = parser.parse_args()

    try:
        grid, width, height = load_map(args.map_file)
        tasks = load_tasks(args.task_file)
        results = check_tasks(grid, width, height, tasks)

        # Save results to output file
        with open(args.output_file, "w", encoding="utf-8") as f:
            for line_num, indices, all_ok in results:
                status = "OK" if all_ok else "WALL"
                indices_str = ",".join(str(i) for i in indices)
                f.write(f"Line {line_num}: {indices_str} -> {status}\n")

        print(f"Results saved to {args.output_file}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()