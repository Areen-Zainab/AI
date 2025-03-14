def read_grid(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        grid = [list(line.strip()) for line in lines]
    return grid

def read_robots(file_path):
    robots = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            robot_id = int(parts[1].replace(':', ''))
            start_str = parts[3].strip('()')
            start = tuple(map(int, start_str.split(',')))
            goal_str = parts[5].strip('()')
            goal = tuple(map(int, goal_str.split(',')))
            robots[robot_id] = {'start': start, 'goal': goal}
    return robots

def read_agents(file_path):
    agents = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(':')
            agent_id = int(parts[0].split()[1])
            path = eval(parts[1].split('at')[0].strip())
            times = eval(parts[1].split('at')[1].strip())
            agents[agent_id] = {'path': path, 'times': times}
    return agents

def a_star(grid, start, goal, dynamic_agents, time_step):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < len(grid) and 0 <= neighbor[1] < len(grid[0]):
                if grid[neighbor[0]][neighbor[1]] == 'X':
                    continue
                if neighbor in dynamic_agents and dynamic_agents[neighbor] == time_step:
                    continue
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        time_step += 1

    return None

def simulate_robots(grid, robots, goals, dynamic_agents):
    paths = {}
    for robot_id, data in robots.items():
        start = data['start']
        goal = data['goal']
        path = a_star(grid, start, goal, dynamic_agents, 0)
        if path:
            paths[robot_id] = {'start': start, 'goal': goal, 'path': path, 'time': len(path) - 1}
    return paths

def main():
    grid = read_grid('data0.txt')
    robots = read_robots('RobotS0.txt')
    agents = read_agents('Agent0.txt')

    dynamic_agents = {}
    for agent_id, data in agents.items():
        path = data['path']
        times = data['times']
        for i in range(len(path)):
            dynamic_agents[path[i]] = times[i]

    results = simulate_robots(grid, robots, dynamic_agents)

    for robot_id, data in results.items():
        print(f"Robot {robot_id}:")
        print(f"  Start: {data['start']}")
        print(f"  Goal: {data['goal']}")
        print(f"  Time: {data['time']}")
        print(f"  Path: {data['path']}")
        print()

if __name__ == "__main__":
    main()