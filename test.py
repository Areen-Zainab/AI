#Areen Zainab
#22i-1115
#Section H

import heapq
import random

def read_grid(filename):
    #list ky tour py list ko initialize karo
    grid = [] 
    with open(filename, 'r') as file:
        lines = file.readlines()
        #grid size read karo
        grid_size = int(lines[0].strip()) 
        #grid lines read karo and new line remove kardo
        for i in range(1, grid_size + 1): 
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
            times = list(map(int, times.strip(']\n').split(', ')))
            agent_movement = [pos for _, pos in sorted(zip(times, positions))]
            dynamic_agents[i] = {'pos': agent_movement, 'curr': -1}
            i += 1
    return dynamic_agents

def read_robots(filename):
    robots = {}
    with open(filename, 'r') as file:
        i = 0
        for line in file:
            parts = line.split(': ')[1].split(' End ')
            start = tuple(map(int, parts[0].replace('Start (', '').replace(')', '').split(', ')))
            goal = tuple(map(int, parts[1].replace('(', '').replace(')', '').split(', ')))
            robots[i] = {'start': start, 'goal': goal, 'path': []}
            i += 1
    return robots

def agent_move(agents, grid):
    for i, agent in agents.items():
        x, y = agent['pos'][agent['curr']]
        if grid[x][y] == f'A{i}':
            grid[x][y] = ' '
        agent['curr'] += 1
        if agent['curr'] >= len(agent['pos']):
            agent['curr'] = 0
            agent['pos'].reverse()
        x, y = agent['pos'][agent['curr']]
        grid[x][y] = f"A{i}"

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def is_valid_move(grid, x, y, obstacles, dynamic_agents, time_step):
    if 0 <= x < len(grid) and 0 <= y < len(grid[0]) and grid[x][y] != 'X':
        if (x, y) in obstacles:
            return False
        for agent in dynamic_agents.values():
            if time_step < len(agent['pos']) and agent['pos'][time_step] == (x, y):
                return False
        return True
    return False

def Astar(grid, start, goal, obstacles, dynamic_agents):
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

def collisionHatao(robot_paths):
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

def rasta_Dhondho(grid, robots, dynamic_agents):
    robot_paths = []
    obstacles = {(i, j) for i in range(len(grid)) for j in range(len(grid[0])) if grid[i][j] == 'X'}
    
    for i, robot in robots.items():
        path, time = Astar(grid, robot['start'], robot['goal'], obstacles, dynamic_agents)
        robots[i]['path'] = path
        robot_paths.append(path)
    
    resolved_paths = collisionHatao(robot_paths)
    
    for i, path in enumerate(resolved_paths):
        robots[i]['path'] = path
    
    return robots

def move_robots(robots, grid):
    for i, robot in robots.items():
        for x, y in robot['path']:
            grid[x][y] = f'R{i}'

grid = read_grid('data0.txt')
dynamic_agents = read_agents('Agent0.txt')
robots = read_robots('Robots0.txt')


for _ in range(20):
    agent_move(dynamic_agents, grid)
#    for row in grid:
#        print(" ".join(row))
#    print()


robots = rasta_Dhondho(grid, robots, dynamic_agents)
move_robots(robots, grid)
print("WOW: \n")
for i, robot in robots.items():
    path_count = len(robot['path'])
    print(f"Robot {i} Path: {robot['path']}")
    print(f"Robot {i} total Time: {path_count-1}\n")
