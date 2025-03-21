import random
import math
from collections import defaultdict

def read_graph_edges(filename):
    vertices = set()
    edges = []
    precolored = {}
    distance_constraints = []
    with open(filename, 'r') as f:
        header = next(f)
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            src, dest = int(parts[0]), int(parts[1])
            edges.append((src, dest))
            vertices.add(src)
            vertices.add(dest)
    vertices = sorted(vertices)
    return vertices, edges, precolored, distance_constraints

def build_adjacency(vertices, edges):
    adjacency = {v: set() for v in vertices}
    for (u, v) in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    degrees = {v: len(adjacency[v]) for v in vertices}
    return adjacency, degrees

def build_two_hop_constraints(vertices, adjacency, distance_constraints):
    extended_constraints = set()
    for u in adjacency:
        for v in adjacency[u]:
            extended_constraints.add((min(u,v), max(u,v)))
    for (u, v) in distance_constraints:
        extended_constraints.add((min(u,v), max(u,v)))
    return extended_constraints

def generate_random_valid_coloring(vertices, precolored, max_colors):
    state = {}
    for v in vertices:
        if v in precolored:
            state[v] = precolored[v]
        else:
            state[v] = random.randint(0, max_colors - 1)
    return state

def color_balancing_score(state, max_colors):
    color_count = defaultdict(int)
    for c in state.values():
        color_count[c] += 1
    counts = list(color_count.values())
    if len(counts) < 2:
        return 0
    mean_val = sum(counts) / len(counts)
    var = sum((x - mean_val) ** 2 for x in counts) / len(counts)
    return math.sqrt(var)

def count_conflicts(state, extended_constraints):
    c = 0
    for (u, v) in extended_constraints:
        if state[u] == state[v]:
            c += 1
    return c

def heuristic(state, extended_constraints, max_colors):
    return count_conflicts(state, extended_constraints) * 1000 + color_balancing_score(state, max_colors)

def get_successors(current_state, adjacency, degrees, extended_constraints, max_colors, precolored):
    successors = []
    vertices_sorted = sorted(current_state.keys(), key=lambda v: degrees[v], reverse=True)
    for v in vertices_sorted[:3]:
        if v in precolored:
            continue
        orig_col = current_state[v]
        for new_col in range(max_colors):
            if new_col == orig_col:
                continue
            new_state = dict(current_state)
            new_state[v] = new_col
            successors.append(new_state)
    return successors

def local_beam_search(
    initial_states, adjacency, degrees, extended_constraints,
    max_colors, precolored, beam_width=5, max_iter=500
):
    beam = []
    for st in initial_states:
        cost = heuristic(st, extended_constraints, max_colors)
        beam.append((cost, st))
    beam.sort(key=lambda x: x[0])
    beam = beam[:beam_width]

    for iteration in range(1, max_iter + 1):
        beam.sort(key=lambda x: x[0])
        best_cost, best_state = beam[0]
        if count_conflicts(best_state, extended_constraints) == 0:

            print(f"Total iterations: {iteration}")
            used_colors = set(best_state.values())
            print("Number of colors used:", len(used_colors))
            for v in sorted(best_state.keys()):
                print(f"Vertex {v} -> Color {best_state[v]}")
            return best_state

        successor_list = []
        for cost, st in beam:
            succs = get_successors(st, adjacency, degrees, extended_constraints, max_colors, precolored)
            for s in succs:
                successor_list.append((heuristic(s, extended_constraints, max_colors), s))

        if not successor_list:
            print(f"Total iterations: {iteration}")
            used_colors = set(best_state.values())
            print("Number of colors used:", len(used_colors))
            for v in sorted(best_state.keys()):
                if v in precolored:
                    print(f"Vertex {v} -> Color {best_state[v]} (Pre-assigned, could not change)")
                else:
                    print(f"Vertex {v} -> Color {best_state[v]}")

            return best_state

        successor_list.sort(key=lambda x: x[0])
        beam = successor_list[:beam_width]

    beam.sort(key=lambda x: x[0])
    final_cost, final_state = beam[0]
    used_colors = set(final_state.values())
    
    for v in sorted(final_state.keys()):
        if v in precolored:
            print(f"Vertex {v} -> Color {final_state[v]} (Pre-assigned, could not change)")
        else:
            print(f"Vertex {v} -> Color {final_state[v]}")

    print(f"Total iterations: {max_iter}")
    print("Number of colors used:", len(used_colors))
    return final_state

def get_two_hop_neighbors(adjacency, v):
    direct_neighbors = adjacency[v]
    
    two_hop_set = set()

    for neighbor in direct_neighbors:
        two_hop_set.update(adjacency[neighbor])
        
    two_hop_set.difference_update(direct_neighbors)
    two_hop_set.discard(v)
    return two_hop_set

def add_two_hop_constraints_for_all(adjacency, extended_constraints):

    for v in adjacency:
        two_hop_neighbors = get_two_hop_neighbors(adjacency, v)
        for w in two_hop_neighbors:
            pair = (min(v, w), max(v, w))
            extended_constraints.add(pair)

def main():
    vertices, edges, precolored, distance_constraints = read_graph_edges("hypercube_dataset.txt")
    adjacency, degrees = build_adjacency(vertices, edges)

    extended_constraints = build_two_hop_constraints(vertices, adjacency, distance_constraints)

    old_count = len(extended_constraints)
    #print("Number of constraints:", old_count)

    add_two_hop_constraints_for_all(adjacency, extended_constraints)

    new_count = len(extended_constraints)
    #print(f"Added {new_count - old_count} two-hop constraints; \ntotal constraints = {new_count}")
    
    precolored = {
        1: 3,
        7: 0,
        50: 2
    }

    max_colors = 5
    beam_width = 5
    initial_states = [generate_random_valid_coloring(vertices, precolored, max_colors) for _ in range(beam_width)]
    solution = local_beam_search(
        initial_states,
        adjacency,
        degrees,
        extended_constraints,
        max_colors,
        precolored,
        beam_width,
        max_iter=100
    )



if __name__ == "__main__":
    main()
