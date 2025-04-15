def astar_pathfinding(grid, start, end):
    """
    Implements A* pathfinding algorithm

    Args:
        grid: 2D matrix where True represents a wall (unwalkable) and False represents walkable space
        start: Tuple of (x, y) coordinates for the starting point
        end: Tuple of (x, y) coordinates for the end point

    Returns:
        List of (x, y) coordinates representing the path from start to end, or empty list if no path exists
    """
    # Convert float coordinates to integers if needed
    start = (int(start[0]), int(start[1]))
    end = (int(end[0]), int(end[1]))

    # Helper function to get neighboring cells
    def get_neighbors(pos):
        x, y = pos
        # Check all 8 directions (including diagonals)
        directions = [
            (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1),  # 4-directional
            (x + 1, y + 1), (x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1)  # diagonals
        ]

        # Filter valid neighbors
        neighbors = []
        for nx, ny in directions:
            # Check if within grid bounds
            if nx < 0 or ny < 0 or nx >= len(grid[0]) or ny >= len(grid):
                continue
            # Check if walkable
            if grid[ny][nx]:  # True means wall (unwalkable)
                continue
            # For diagonal movement, make sure we're not cutting corners through walls
            if (nx != x and ny != y):
                if grid[y][nx] or grid[ny][x]:  # Can't cut through walls
                    continue

            # Calculate cost: 1.0 for cardinals, 1.4 for diagonals
            cost = 1.4 if (nx != x and ny != y) else 1.0
            neighbors.append(((nx, ny), cost))

        return neighbors

    # Heuristic function (Euclidean distance)
    def heuristic(a, b):
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    # Initialize data structures
    from heapq import heappush, heappop

    open_set = []  # Priority queue
    closed_set = set()  # Visited nodes

    # Dictionary to track the best path
    came_from = {}

    # Costs
    g_score = {start: 0}  # Cost from start to current node
    f_score = {start: heuristic(start, end)}  # Estimated total cost

    # Add start node to open set
    heappush(open_set, (f_score[start], start))

    while open_set:
        # Get node with lowest f_score
        _, current = heappop(open_set)

        # If we reached the end, construct and return the path
        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        # Mark as visited
        closed_set.add(current)

        # Check all neighbors
        for neighbor, move_cost in get_neighbors(current):
            # Skip if already visited
            if neighbor in closed_set:
                continue

            # Calculate tentative g_score
            tentative_g_score = g_score[current] + move_cost

            # If new node or better path found
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                # Update path and scores
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)

                # Add to open set if not already there
                if neighbor not in [node for _, node in open_set]:
                    heappush(open_set, (f_score[neighbor], neighbor))

    # If we get here, no path was found
    return []