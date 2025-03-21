import random
import pandas as pd
from collections import defaultdict

class Shelf:
    def __init__(self, name, capacity, is_refrigerated=False, is_hazardous=False, is_eye_level=False):
        self.name = name
        self.capacity = capacity
        self.is_refrigerated = is_refrigerated
        self.is_hazardous = is_hazardous
        self.is_eye_level = is_eye_level

    def __repr__(self):
        return f"{self.name}(cap={self.capacity}, refrig={self.is_refrigerated}, haz={self.is_hazardous}, eye={self.is_eye_level})"

class Product:
    def __init__(self, name, weight, category, is_perishable=False, is_hazardous=False, is_high_demand=False):
        self.name = name
        self.weight = weight
        self.category = category
        self.is_perishable = is_perishable
        self.is_hazardous = is_hazardous
        self.is_high_demand = is_high_demand

    def __repr__(self):
        return f"{self.name}(w={self.weight}, cat={self.category}, per={self.is_perishable}, haz={self.is_hazardous}, hd={self.is_high_demand})"

def setup_shelves_and_products():
    shelves = [
        Shelf("S1_Checkout", 8, is_eye_level=True),
        Shelf("S2_Lower", 25),
        Shelf("S3_EyeLevel", 15, is_eye_level=True),
        Shelf("S4_General", 20),
        Shelf("R1_Refrigerator", 20, is_refrigerated=True),
        Shelf("H1_Hazardous", 10, is_hazardous=True),
    ]

    products = [
        Product("Milk", 5, "Dairy", is_perishable=True, is_high_demand=True),
        Product("Rice_Bag", 10, "Grain", is_perishable=False, is_high_demand=False),
        Product("Frozen_Nuggets", 5, "Frozen", is_perishable=True, is_high_demand=False),
        Product("Cereal", 3, "Breakfast", is_perishable=False, is_high_demand=True),
        Product("Pasta", 2, "Grain", is_perishable=False, is_high_demand=False),
        Product("Pasta_Sauce", 3, "Condiment", is_perishable=False, is_high_demand=False),
        Product("Detergent", 4, "Cleaning", is_perishable=False, is_hazardous=True),
        Product("Glass_Cleaner", 5, "Cleaning", is_perishable=False, is_hazardous=True),
        Product("Bread", 2, "Bakery", is_perishable=False, is_high_demand=True),
        Product("Apples", 3, "Produce", is_perishable=True, is_high_demand=False),
        Product("Perfume", 1, "Cosmetics", is_perishable=False, is_hazardous=False, is_high_demand=False),
        Product("Candy", 1, "Snacks", is_perishable=False, is_hazardous=False, is_high_demand=False),
    ]
    return shelves, products

def compute_fitness(chromosome, shelves, products):
    penalty = 0.0

    shelf_loads = [0]*len(shelves)
    shelf_contents = [[] for _ in range(len(shelves))]

    # Assign products to shelves
    for prod_idx, shelf_idx in enumerate(chromosome):
        p = products[prod_idx]
        s = shelves[shelf_idx]
        shelf_loads[shelf_idx] += p.weight
        shelf_contents[shelf_idx].append(p)

    # Capacity check
    for i, load in enumerate(shelf_loads):
        if load > shelves[i].capacity:
            penalty += (load - shelves[i].capacity)*10

    # Perishable in fridge
    for prod_idx, shelf_idx in enumerate(chromosome):
        p = products[prod_idx]
        s = shelves[shelf_idx]
        if p.is_perishable and not s.is_refrigerated:
            penalty += 30

    # Hazardous zone
    for prod_idx, shelf_idx in enumerate(chromosome):
        p = products[prod_idx]
        s = shelves[shelf_idx]
        if p.is_hazardous and not s.is_hazardous:
            penalty += 5


    # High-demand -> prefer eye-level
    for prod_idx, shelf_idx in enumerate(chromosome):
        p = products[prod_idx]
        s = shelves[shelf_idx]
        if p.is_high_demand and not s.is_eye_level:
            penalty += 5

    # Cross-selling 
    name_to_idx = {prod.name: i for i, prod in enumerate(products)}
    if "Pasta" in name_to_idx and "Pasta_Sauce" in name_to_idx:
        pasta_idx = name_to_idx["Pasta"]
        sauce_idx = name_to_idx["Pasta_Sauce"]
        if chromosome[pasta_idx] != chromosome[sauce_idx]:
            penalty += 2

    # Theft prevention (Perfume -> prefer shelf index 0)
    if "Perfume" in name_to_idx:
        perfume_shelf = chromosome[name_to_idx["Perfume"]]
        if perfume_shelf != 0:
            penalty += 10

    return penalty

def init_population(pop_size, shelves, products):
    population = []
    for _ in range(pop_size):
        chromosome = [random.randint(0, len(shelves)-1) for _ in products]
        population.append(chromosome)
    return population

def tournament_selection(pop, fitnesses, k=3):
    selected = []
    size = len(pop)
    for _ in range(len(pop)):
        best = None
        best_fit = float('inf')
        for _ in range(k):
            idx = random.randint(0, size-1)
            if fitnesses[idx] < best_fit:
                best_fit = fitnesses[idx]
                best = pop[idx]
        selected.append(best)
    return selected

def crossover(p1, p2):
    if random.random() < 0.9:  # single-point with 90% chance
        point = random.randint(1, len(p1)-2)
        c1 = p1[:point] + p2[point:]
        c2 = p2[:point] + p1[point:]
        return c1, c2
    else:
        return p1[:], p2[:]

def mutate(chromosome, mutation_rate, num_shelves):
    for i in range(len(chromosome)):
        if random.random() < mutation_rate:
            chromosome[i] = random.randint(0, num_shelves-1)
    return chromosome

def genetic_algorithm(shelves, products, pop_size=30, generations=50, mutation_rate=0.02):
    population = init_population(pop_size, shelves, products)
    best_chromosome = None
    best_fitness = float('inf')

    for gen in range(generations):
        fitnesses = [compute_fitness(ch, shelves, products) for ch in population]

        for i, f in enumerate(fitnesses):
            if f < best_fitness:
                best_fitness = f
                best_chromosome = population[i]

        print(f"Generation {gen}, Best Fitness: {best_fitness}")

        selected = tournament_selection(population, fitnesses, k=3)
        next_pop = []
        for i in range(0, len(selected), 2):
            p1 = selected[i]
            p2 = selected[(i+1) % len(selected)]
            c1, c2 = crossover(p1, p2)
            c1 = mutate(c1, mutation_rate, len(shelves))
            c2 = mutate(c2, mutation_rate, len(shelves))
            next_pop.append(c1)
            next_pop.append(c2)

        population = next_pop

    return best_chromosome, best_fitness

def export_solution_to_excel(chromosome, shelves, products, filename="shelf_allocation.xlsx"):
    rows = []
    for prod_idx, shelf_idx in enumerate(chromosome):
        p = products[prod_idx]
        s = shelves[shelf_idx]
        row = {
            "Product": p.name,
            "Weight": p.weight,
            "Category": p.category,
            "Is_Perishable": p.is_perishable,
            "Is_Hazardous": p.is_hazardous,
            "Is_HighDemand": p.is_high_demand,
            "Assigned_Shelf": s.name,
            "Shelf_Capacity": s.capacity,
            "Shelf_Refrigerated": s.is_refrigerated,
            "Shelf_Hazardous": s.is_hazardous,
            "Shelf_EyeLevel": s.is_eye_level,
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_excel(filename, index=False)
    print(f"Solution exported to {filename}")

def main():
    shelves, products = setup_shelves_and_products()

    best_chromosome, best_fitness = genetic_algorithm(
        shelves=shelves, 
        products=products,
        pop_size=30,
        generations=50,
        mutation_rate=0.02
    )

    print("\nGA Finished: ")
    print(f"Best Fitness: {best_fitness}")
    print(f"Best Chromosome: {best_chromosome}\n")

    shelf_assignments = defaultdict(list)
    shelf_weights = defaultdict(int)
    for prod_idx, shelf_idx in enumerate(best_chromosome):
        p = products[prod_idx]
        s = shelves[shelf_idx]
        shelf_assignments[s.name].append(p.name)
        shelf_weights[s.name] += p.weight

    for shelf_name, prod_names in shelf_assignments.items():
        total_weight = shelf_weights[shelf_name]
        prod_list_str = ", ".join(prod_names)
        print(f"{shelf_name}: {prod_list_str} ({total_weight}kg)")

    # Optionally, also print line-by-line assignment if you like:
    #for prod_idx, shelf_idx in enumerate(best_chromosome):
    #     print(f"\n{products[prod_idx].name} -> {shelves[shelf_idx].name}")

    export_solution_to_excel(best_chromosome, shelves, products, filename="shelf_allocation.xlsx")

if __name__ == "__main__":
    main()
