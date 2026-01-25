import numpy as np
import matplotlib.pyplot as plt
import random
import math

# --- 1. CONFIGURATION & CONSTANTS ---
CITY_CENTER = (35.6892, 51.3890)  # Example: Tehran coordinates
AREA_SIZE_KM = 5.0                # Simulation area size
NUM_DRIVERS = 15
NUM_PASSENGERS = 80
SEARCH_RADIUS_KM = 1.0            # The constraint: 1km radius
MAX_CAPACITY = 4                  # The constraint: Max 4 people per car
PRICE_BASE = 100                  # Base fare
MARKUP_PERCENT = 0.20             # x% markup for detour

class User:
    def __init__(self, uid, role, origin, dest):
        self.id = uid
        self.role = role  # 'driver' or 'passenger'
        self.origin = origin # (lat, lon)
        self.dest = dest     # (lat, lon)
        # Simplified time/day for visualization purposes
        self.schedule = random.randint(8, 10) # Morning commute hour
        self.days = {0, 1, 2, 3, 4} # Mon-Fri

class Driver(User):
    def __init__(self, uid, origin, dest):
        super().__init__(uid, 'driver', origin, dest)
        self.capacity = MAX_CAPACITY
        self.passengers = []
        self.route_score = 0

class Passenger(User):
    def __init__(self, uid, origin, dest):
        super().__init__(uid, 'passenger', origin, dest)
        self.matched_driver = None

# --- 2. HELPER FUNCTIONS (MATH) ---

def haversine(coord1, coord2):
    """Calculates distance in km between two lat/lon points."""
    R = 6371  # Earth radius in km
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def generate_random_point(center, radius_km):
    """Generates a random lat/lon within radius_km of center."""
    y0, x0 = center
    r = radius_km / 111.32 # approx conversion to degrees
    u, v = np.random.uniform(0, 1), np.random.uniform(0, 1)
    w = r * math.sqrt(u)
    t = 2 * math.pi * v
    x = w * math.cos(t)
    y = w * math.sin(t)
    return (y0 + y, x0 + x)

# --- 3. THE ALGORITHM ---

def match_algorithm(drivers, passengers):
    """
    Executes the Greedy Heuristic Matching.
    Complexity: O(D * P) - Simplified for this demo without Spatial Index
    """
    print(f"Running optimization for {len(drivers)} drivers and {len(passengers)} passengers...")
    
    # Shuffle drivers to randomize "First come first serve" order
    random.shuffle(drivers)
    
    for driver in drivers:
        if driver.capacity == 0:
            continue
            
        # Step A: Find all FEASIBLE candidates
        candidates = []
        for p in passengers:
            if p.matched_driver is not None:
                continue # Already taken
            
            # Constraint 1: Origin Radius <= 1km
            dist_origin = haversine(driver.origin, p.origin)
            if dist_origin > SEARCH_RADIUS_KM:
                continue
                
            # Constraint 2: Destination Radius <= 1km (Simulated constraint)
            dist_dest = haversine(driver.dest, p.dest)
            if dist_dest > SEARCH_RADIUS_KM:
                continue
                
            # Constraint 3: Time Overlap (Exact match for this demo)
            if driver.schedule != p.schedule:
                continue

            candidates.append((p, dist_origin, dist_dest))
        
        # Step B: OPTIMIZATION (Scoring)
        # We want to minimize total deviation. 
        # Score = matches closest to origin and closest to dest.
        # Lower score is better (score = sum of distances)
        candidates.sort(key=lambda x: x[1] + x[2])
        
        # Step C: Assignment
        slots = driver.capacity
        selected = candidates[:slots]
        
        for p_tuple in selected:
            p = p_tuple[0]
            p.matched_driver = driver
            driver.passengers.append(p)
            driver.capacity -= 1
            
            # Pricing Calculation (Constraint 4)
            # 1/4 full ride + Markup
            ride_cost = (PRICE_BASE / 4) + (PRICE_BASE * MARKUP_PERCENT)
            # print(f"   -> Match: D{driver.id} picks P{p.id}. Cost: ${ride_cost:.2f}")

# --- 4. VISUALIZATION ---

def plot_simulation(drivers, passengers):
    plt.figure(figsize=(12, 8))
    
    # 1. Plot Unmatched Passengers
    unmatched_x = [p.origin[1] for p in passengers if p.matched_driver is None]
    unmatched_y = [p.origin[0] for p in passengers if p.matched_driver is None]
    plt.scatter(unmatched_x, unmatched_y, c='grey', alpha=0.5, s=20, label='Unmatched Passenger')

    # 2. Plot Drivers and their Routes
    for d in drivers:
        # Plot Driver Origin
        plt.scatter(d.origin[1], d.origin[0], c='red', marker='s', s=80, edgecolors='black', zorder=10)
        # Plot Driver Dest (Arrow)
        plt.arrow(d.origin[1], d.origin[0], 
                  d.dest[1] - d.origin[1], d.dest[0] - d.origin[0], 
                  head_width=0.002, color='red', alpha=0.3, length_includes_head=True)
        
        # Draw "Rubber bands" to assigned passengers
        for p in d.passengers:
            # Green line from Driver Origin to Passenger Origin
            plt.plot([d.origin[1], p.origin[1]], [d.origin[0], p.origin[0]], 'g--', linewidth=0.8, alpha=0.7)
            # Plot Matched Passenger
            plt.scatter(p.origin[1], p.origin[0], c='green', s=30, zorder=5)

    # Fake legend entry for Driver
    plt.scatter([], [], c='red', marker='s', label='Driver Origin')
    plt.scatter([], [], c='green', label='Matched Passenger')
    plt.plot([], [], 'g--', label='Match Connection')

    plt.title(f"Carpooling Algorithm Optimization\nRadius: {SEARCH_RADIUS_KM}km | Capacity: {MAX_CAPACITY}")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend(loc='upper right')
    plt.grid(True, linestyle=':', alpha=0.6)
    
    # Save the plot
    plt.savefig("simulation_result.png")
    plt.show()

# --- 5. MAIN EXECUTION ---

if __name__ == "__main__":
    # A. Generate Data
    drivers = []
    passengers = []
    
    print("Generating synthetic data...")
    for i in range(NUM_DRIVERS):
        d_org = generate_random_point(CITY_CENTER, AREA_SIZE_KM)
        d_dst = generate_random_point(CITY_CENTER, AREA_SIZE_KM) # Random dest for demo
        drivers.append(Driver(i, d_org, d_dst))
        
    for i in range(NUM_PASSENGERS):
        p_org = generate_random_point(CITY_CENTER, AREA_SIZE_KM)
        p_dst = generate_random_point(CITY_CENTER, AREA_SIZE_KM)
        passengers.append(Passenger(i, p_org, p_dst))

    # B. Run Algorithm
    match_algorithm(drivers, passengers)
    
    # C. Calculate Metrics
    matched_count = sum(1 for p in passengers if p.matched_driver)
    occupancy = sum(len(d.passengers) for d in drivers) / (len(drivers) * MAX_CAPACITY)
    
    print("-" * 30)
    print(f"SIMULATION RESULTS:")
    print(f"Total Passengers: {len(passengers)}")
    print(f"Matched:          {matched_count} ({matched_count/len(passengers):.1%})")
    print(f"Fleet Occupancy:  {occupancy:.1%}")
    print("-" * 30)

    # D. Visualize
    plot_simulation(drivers, passengers)