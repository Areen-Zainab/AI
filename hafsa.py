#Areen Zainab
#22i-1115
#Section H

import heapq
import random

def read_grid(filename):
    grid = []  # Initialize grid as a list of strings
    with open(filename, 'r') as file:
        lines = file.readlines()
        grid_size = int(lines[0].strip())  # Read grid size
        for i in range(1, grid_size + 1):  # Read grid lines and remove newline characters
            line = lines[i].replace('\n', '')
            grid.append(list(line)) 

    return grid

def read_agents(filename):
    dynamic_agents = {}
    with open(filename, 'r') as file:
        i = 0
        for line in file:
            parts = line.split(': ')[1]
            positions, times = parts.split(' at times [')
            positions = eval(positions)[0]
            #positions = [list(map(int, pos)) for pos in positions]
            times = list(map(int, times.strip(']\n').split(', ')))
            agent_movement = [pos for _, pos in sorted(zip(times, positions))]
            dynamic_agents[i] = {'pos': agent_movement, 'curr': -1}
            i+=1
    return dynamic_agents

def read_robots(filename):
    robots = {}

    with open(filename, 'r') as file:
        for line in file:
            parts = line.split(': ')[1].split(' End ')
            start = tuple(map(int, parts[0].replace('Start (', '').replace(')', '').split(', ')))
            goal = tuple(map(int, parts[1].replace('(', '').replace(')', '').split(', ')))
            robots.append(start)
            goals.append(goal)
    return robots, goals

def agent_move(agents, grid):
    i = 0
    for agent in agents.values():

        x, y = agent['pos'][agent['curr']]
        if(grid[x][y] == f'A{i}'):
            grid[x][y] = ' '

        agent['curr'] += 1
        if(agent['curr'] >= len(agent['pos'])):
            agent['curr'] = 0
            agent['pos'].reverse()

        x, y = agent['pos'][agent['curr']]
        grid[x][y] = f"A{i}"
        i+=1


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def is_valid_move(grid, x, y, obstacles, dynamic_agents, time_step):
    if 0 <= x < len(grid) and 0 <= y < len(grid[0]) and grid[x][y] != 'X':
        if (x, y) in obstacles:
            return False
        for agent in dynamic_agents:
            if time_step % (2 * len(agent)) < len(agent) and agent[time_step % len(agent)] == (x, y):
                return False
        return True
    return False

def a_star(grid, start, goal, obstacles, dynamic_agents):
    moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    open_set = []
    heapq.heappush(open_set, (0, start, []))
    visited = set()
    
    while open_set:
        cost, (x, y), path = heapq.heappop(open_set)
        if (x, y) == goal:
            return path + [(x, y)], len(path)
        
        time_step = len(path)
        if (x, y, time_step) in visited:
            continue
        visited.add((x, y, time_step))
        
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if is_valid_move(grid, nx, ny, obstacles, dynamic_agents, time_step + 1):
                heapq.heappush(open_set, (cost + 1 + heuristic((nx, ny), goal), (nx, ny), path + [(x, y)]))
    
    return [], float('inf')

def resolve_collision(robot_paths):
    positions = {}
    for i, path in enumerate(robot_paths):
        for t, pos in enumerate(path):
            if (t, pos) in positions:
                positions[(t, pos)].append(i)
            else:
                positions[(t, pos)] = [i]
    
    for (t, pos), robots in positions.items():
        if len(robots) > 1:
            for r in robots:
                random.shuffle(robot_paths[r])
    
    return robot_paths

def find_paths(grid, robots, goals, dynamic_agents):
    robot_paths = []
    obstacles = set()
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == 'X':
                obstacles.add((i, j))
    
    for i, (start, goal) in enumerate(zip(robots, goals)):
        path, time = a_star(grid, start, goal, obstacles, dynamic_agents)
        robot_paths.append((path, time))
    
    resolved_paths = resolve_collision([p[0] for p in robot_paths])
    return [(path, len(path) - 1) for path in resolved_paths]

# Read input from files
grid = read_grid('data0.txt')
dynamic_agents = read_agents('Agent0.txt')

for i in range(20):
    agent_move(dynamic_agents, grid)
    for row in grid:
        print(" ".join(row))
        robots, goals = read_robots('Robots0.txt')

paths = find_paths(grid, robots, goals, dynamic_agents)

# Print results 

for i, (path, time) in enumerate(paths):
    print(f"Robot {i+1} Path: {path}")
    print(f"Robot {i+1} Total Time: {time}")
    