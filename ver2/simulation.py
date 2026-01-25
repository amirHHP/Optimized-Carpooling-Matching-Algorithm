import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for headless environments
import matplotlib.pyplot as plt
import random
import math
from datetime import datetime

# --- 1. CONFIGURATION & CONSTANTS ---
CITY_CENTER = (35.6892, 51.3890)  # Example: Tehran coordinates
AREA_SIZE_KM = 5.0                # Simulation area size
SEARCH_RADIUS_KM = 1.0            # The constraint: 1km radius
MAX_CAPACITY = 4                  # The constraint: Max 4 people per car
PRICE_BASE = 100                  # Base fare
MARKUP_PERCENT = 0.20             # x% markup for detour

# Random pool size ranges
MIN_DRIVERS = 10
MAX_DRIVERS = 30
MIN_PASSENGERS = 50
MAX_PASSENGERS = 150

# Neighborhood/cluster settings for realistic simulation
NUM_NEIGHBORHOODS = 5             # Number of residential clusters
NUM_WORK_AREAS = 3                # Number of work destination clusters
CLUSTER_RADIUS_KM = 1.5           # Size of each cluster

class User:
    def __init__(self, uid, role, origin, dest, name=None):
        self.id = uid
        self.name = name or f"{role.capitalize()}_{uid}"
        self.role = role  # 'driver' or 'passenger'
        self.origin = origin  # (lat, lon)
        self.dest = dest      # (lat, lon)
        # Simplified time/day for visualization purposes
        self.schedule = random.randint(7, 11)  # Morning commute hour (7-11 AM)
        self.days = {0, 1, 2, 3, 4}  # Mon-Fri

class Driver(User):
    def __init__(self, uid, origin, dest, name=None):
        super().__init__(uid, 'driver', origin, dest, name)
        self.capacity = MAX_CAPACITY
        self.passengers = []
        self.route_score = 0
        self.vehicle_type = random.choice(['Sedan', 'SUV', 'Hatchback', 'Van'])
        
    def get_route_distance(self):
        """Calculate driver's original route distance"""
        return haversine(self.origin, self.dest)

class Passenger(User):
    def __init__(self, uid, origin, dest, name=None):
        super().__init__(uid, 'passenger', origin, dest, name)
        self.matched_driver = None
        self.pickup_distance = None
        self.dropoff_distance = None
        self.fare = 0
        
    def get_trip_distance(self):
        """Calculate passenger's trip distance"""
        return haversine(self.origin, self.dest)

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
    r = radius_km / 111.32  # approx conversion to degrees
    u, v = np.random.uniform(0, 1), np.random.uniform(0, 1)
    w = r * math.sqrt(u)
    t = 2 * math.pi * v
    x = w * math.cos(t)
    y = w * math.sin(t)
    return (y0 + y, x0 + x)

def generate_random_name(role, uid):
    """Generate a random name for users"""
    first_names = ['Ali', 'Sara', 'Reza', 'Mina', 'Hassan', 'Fatima', 'Mohammad', 'Zahra', 
                   'Amir', 'Leila', 'Mehdi', 'Narges', 'Hossein', 'Parisa', 'Ahmad', 'Negar']
    return f"{random.choice(first_names)}_{uid}"

# --- 3. POOL GENERATION ---

def generate_clusters():
    """Generate neighborhood and work area cluster centers"""
    neighborhoods = []
    work_areas = []
    
    # Generate residential neighborhoods (spread around the city)
    for i in range(NUM_NEIGHBORHOODS):
        center = generate_random_point(CITY_CENTER, AREA_SIZE_KM * 0.7)
        neighborhoods.append({
            'name': f"Neighborhood_{i+1}",
            'center': center
        })
    
    # Generate work areas (typically more central)
    for i in range(NUM_WORK_AREAS):
        center = generate_random_point(CITY_CENTER, AREA_SIZE_KM * 0.5)
        work_areas.append({
            'name': f"WorkArea_{i+1}",
            'center': center
        })
    
    return neighborhoods, work_areas

def generate_random_pool():
    """Generate a random pool of drivers and passengers with realistic clustering"""
    num_drivers = random.randint(MIN_DRIVERS, MAX_DRIVERS)
    num_passengers = random.randint(MIN_PASSENGERS, MAX_PASSENGERS)
    
    # Generate cluster centers
    neighborhoods, work_areas = generate_clusters()
    
    drivers = []
    passengers = []
    
    print("=" * 60)
    print(f"{'GENERATING RANDOM POOL':^60}")
    print("=" * 60)
    print(f"\nSimulation Seed: {datetime.now().strftime('%Y%m%d_%H%M%S')}")
    print(f"City Center: {CITY_CENTER} (Tehran)")
    print(f"Area Size: {AREA_SIZE_KM} km radius")
    print(f"Search Radius: {SEARCH_RADIUS_KM} km")
    print(f"Max Capacity per Car: {MAX_CAPACITY}")
    print(f"\nUsing CLUSTERED mode (realistic neighborhoods)")
    print(f"  - {NUM_NEIGHBORHOODS} residential neighborhoods")
    print(f"  - {NUM_WORK_AREAS} work destination areas")
    print()
    
    # Generate Drivers (from neighborhoods to work areas)
    print(f"Generating {num_drivers} drivers...")
    for i in range(num_drivers):
        # Pick a random neighborhood for origin
        home_cluster = random.choice(neighborhoods)
        d_org = generate_random_point(home_cluster['center'], CLUSTER_RADIUS_KM)
        
        # Pick a random work area for destination
        work_cluster = random.choice(work_areas)
        d_dst = generate_random_point(work_cluster['center'], CLUSTER_RADIUS_KM)
        
        name = generate_random_name('driver', i)
        driver = Driver(i, d_org, d_dst, name)
        driver.home_neighborhood = home_cluster['name']
        driver.work_area = work_cluster['name']
        drivers.append(driver)
    
    # Generate Passengers (similar pattern - neighborhoods to work areas)
    print(f"Generating {num_passengers} passengers...")
    for i in range(num_passengers):
        # Pick a random neighborhood for origin
        home_cluster = random.choice(neighborhoods)
        p_org = generate_random_point(home_cluster['center'], CLUSTER_RADIUS_KM)
        
        # Pick a random work area for destination
        work_cluster = random.choice(work_areas)
        p_dst = generate_random_point(work_cluster['center'], CLUSTER_RADIUS_KM)
        
        name = generate_random_name('passenger', i)
        passenger = Passenger(i, p_org, p_dst, name)
        passenger.home_neighborhood = home_cluster['name']
        passenger.work_area = work_cluster['name']
        passengers.append(passenger)
    
    return drivers, passengers, neighborhoods, work_areas

# --- 4. THE ALGORITHM ---

def match_algorithm(drivers, passengers):
    """
    Executes the Greedy Heuristic Matching.
    Returns detailed match information.
    """
    match_details = []
    
    # Shuffle drivers to randomize "First come first serve" order
    random.shuffle(drivers)
    
    for driver in drivers:
        if driver.capacity == 0:
            continue
            
        # Step A: Find all FEASIBLE candidates
        candidates = []
        for p in passengers:
            if p.matched_driver is not None:
                continue  # Already taken
            
            # Constraint 1: Origin Radius <= 1km
            dist_origin = haversine(driver.origin, p.origin)
            if dist_origin > SEARCH_RADIUS_KM:
                continue
                
            # Constraint 2: Destination Radius <= 1km
            dist_dest = haversine(driver.dest, p.dest)
            if dist_dest > SEARCH_RADIUS_KM:
                continue
                
            # Constraint 3: Time Overlap (within 1 hour window)
            if abs(driver.schedule - p.schedule) > 1:
                continue

            candidates.append((p, dist_origin, dist_dest))
        
        # Step B: OPTIMIZATION (Scoring)
        candidates.sort(key=lambda x: x[1] + x[2])
        
        # Step C: Assignment
        slots = driver.capacity
        selected = candidates[:slots]
        
        for p_tuple in selected:
            p, dist_origin, dist_dest = p_tuple
            p.matched_driver = driver
            p.pickup_distance = dist_origin
            p.dropoff_distance = dist_dest
            driver.passengers.append(p)
            driver.capacity -= 1
            
            # Pricing Calculation
            ride_cost = (PRICE_BASE / 4) + (PRICE_BASE * MARKUP_PERCENT)
            p.fare = ride_cost
            
            match_details.append({
                'driver': driver,
                'passenger': p,
                'pickup_dist': dist_origin,
                'dropoff_dist': dist_dest,
                'fare': ride_cost
            })
    
    return match_details

# --- 5. DETAILED REPORTING ---

def print_pool_details(drivers, passengers, neighborhoods, work_areas):
    """Print details about the generated pool"""
    print("\n" + "=" * 60)
    print(f"{'POOL DETAILS':^60}")
    print("=" * 60)
    
    # Cluster info
    print(f"\n{'--- CLUSTER CENTERS ---':^60}")
    print("Residential Neighborhoods:")
    for n in neighborhoods:
        print(f"  {n['name']}: ({n['center'][0]:.4f}, {n['center'][1]:.4f})")
    print("\nWork Areas:")
    for w in work_areas:
        print(f"  {w['name']}: ({w['center'][0]:.4f}, {w['center'][1]:.4f})")
    
    # Driver details
    print(f"\n{'--- DRIVERS ---':^60}")
    print(f"{'ID':<4} {'Name':<12} {'Vehicle':<10} {'Sched':<6} {'Route':<8} {'From->To':<25}")
    print("-" * 70)
    for d in drivers[:10]:  # Show first 10
        route_dist = d.get_route_distance()
        route_info = f"{d.home_neighborhood[:8]}->{d.work_area[:8]}"
        print(f"{d.id:<4} {d.name:<12} {d.vehicle_type:<10} {d.schedule}:00  {route_dist:>5.2f}km  {route_info}")
    if len(drivers) > 10:
        print(f"... and {len(drivers) - 10} more drivers")
    
    # Passenger details
    print(f"\n{'--- PASSENGERS ---':^60}")
    print(f"{'ID':<4} {'Name':<12} {'Sched':<6} {'Trip':<8} {'From->To':<25}")
    print("-" * 60)
    for p in passengers[:10]:  # Show first 10
        trip_dist = p.get_trip_distance()
        route_info = f"{p.home_neighborhood[:8]}->{p.work_area[:8]}"
        print(f"{p.id:<4} {p.name:<12} {p.schedule}:00  {trip_dist:>5.2f}km  {route_info}")
    if len(passengers) > 10:
        print(f"... and {len(passengers) - 10} more passengers")
    
    # Schedule distribution
    print(f"\n{'--- SCHEDULE DISTRIBUTION ---':^60}")
    driver_schedules = {}
    passenger_schedules = {}
    for d in drivers:
        driver_schedules[d.schedule] = driver_schedules.get(d.schedule, 0) + 1
    for p in passengers:
        passenger_schedules[p.schedule] = passenger_schedules.get(p.schedule, 0) + 1
    
    print(f"{'Hour':<10} {'Drivers':<15} {'Passengers':<15}")
    print("-" * 40)
    for hour in sorted(set(list(driver_schedules.keys()) + list(passenger_schedules.keys()))):
        d_count = driver_schedules.get(hour, 0)
        p_count = passenger_schedules.get(hour, 0)
        print(f"{hour}:00      {d_count:<15} {p_count:<15}")
    
    # Neighborhood distribution
    print(f"\n{'--- NEIGHBORHOOD DISTRIBUTION ---':^60}")
    driver_neighborhoods = {}
    passenger_neighborhoods = {}
    for d in drivers:
        driver_neighborhoods[d.home_neighborhood] = driver_neighborhoods.get(d.home_neighborhood, 0) + 1
    for p in passengers:
        passenger_neighborhoods[p.home_neighborhood] = passenger_neighborhoods.get(p.home_neighborhood, 0) + 1
    
    print(f"{'Neighborhood':<20} {'Drivers':<15} {'Passengers':<15}")
    print("-" * 50)
    all_neighborhoods = set(list(driver_neighborhoods.keys()) + list(passenger_neighborhoods.keys()))
    for n in sorted(all_neighborhoods):
        d_count = driver_neighborhoods.get(n, 0)
        p_count = passenger_neighborhoods.get(n, 0)
        print(f"{n:<20} {d_count:<15} {p_count:<15}")

def print_matching_results(drivers, passengers, match_details):
    """Print detailed matching results"""
    print("\n" + "=" * 60)
    print(f"{'MATCHING RESULTS':^60}")
    print("=" * 60)
    
    matched_passengers = [p for p in passengers if p.matched_driver is not None]
    unmatched_passengers = [p for p in passengers if p.matched_driver is None]
    
    # Car occupancy breakdown
    full_cars = sum(1 for d in drivers if len(d.passengers) == MAX_CAPACITY)
    cars_with_3 = sum(1 for d in drivers if len(d.passengers) == 3)
    cars_with_2 = sum(1 for d in drivers if len(d.passengers) == 2)
    cars_with_1 = sum(1 for d in drivers if len(d.passengers) == 1)
    empty_cars = sum(1 for d in drivers if len(d.passengers) == 0)
    active_cars = sum(1 for d in drivers if len(d.passengers) > 0)
    
    print(f"\n{'--- OVERALL STATISTICS ---':^60}")
    print(f"Total Drivers:            {len(drivers)}")
    print(f"Total Passengers:         {len(passengers)}")
    print(f"Matched Passengers:       {len(matched_passengers)} ({len(matched_passengers)/len(passengers)*100:.1f}%)")
    print(f"Unmatched Passengers:     {len(unmatched_passengers)} ({len(unmatched_passengers)/len(passengers)*100:.1f}%)")
    
    print(f"\n{'--- CAR OCCUPANCY BREAKDOWN ---':^60}")
    print(f"Full Cars (4 passengers): {full_cars} ({full_cars/len(drivers)*100:.1f}%)")
    print(f"Cars with 3 passengers:   {cars_with_3} ({cars_with_3/len(drivers)*100:.1f}%)")
    print(f"Cars with 2 passengers:   {cars_with_2} ({cars_with_2/len(drivers)*100:.1f}%)")
    print(f"Cars with 1 passenger:    {cars_with_1} ({cars_with_1/len(drivers)*100:.1f}%)")
    print(f"Empty Cars (0 passengers):{empty_cars} ({empty_cars/len(drivers)*100:.1f}%)")
    print(f"Active Cars:              {active_cars} ({active_cars/len(drivers)*100:.1f}%)")
    
    # Calculate fleet occupancy
    total_capacity = len(drivers) * MAX_CAPACITY
    used_capacity = len(matched_passengers)
    fleet_occupancy = used_capacity / total_capacity * 100 if total_capacity > 0 else 0
    
    print(f"\n{'--- CAPACITY UTILIZATION ---':^60}")
    print(f"Total Fleet Capacity:     {total_capacity} seats")
    print(f"Used Capacity:            {used_capacity} seats")
    print(f"Fleet Occupancy:          {fleet_occupancy:.1f}%")
    
    # Distance statistics
    if match_details:
        pickup_distances = [m['pickup_dist'] for m in match_details]
        dropoff_distances = [m['dropoff_dist'] for m in match_details]
        total_distances = [m['pickup_dist'] + m['dropoff_dist'] for m in match_details]
        
        print(f"\n{'--- DISTANCE STATISTICS (km) ---':^60}")
        print(f"{'Metric':<25} {'Min':<10} {'Max':<10} {'Avg':<10}")
        print("-" * 55)
        print(f"{'Pickup Distance':<25} {min(pickup_distances):.3f}    {max(pickup_distances):.3f}    {sum(pickup_distances)/len(pickup_distances):.3f}")
        print(f"{'Dropoff Distance':<25} {min(dropoff_distances):.3f}    {max(dropoff_distances):.3f}    {sum(dropoff_distances)/len(dropoff_distances):.3f}")
        print(f"{'Total Detour':<25} {min(total_distances):.3f}    {max(total_distances):.3f}    {sum(total_distances)/len(total_distances):.3f}")
    
    # Revenue statistics
    if match_details:
        total_revenue = sum(m['fare'] for m in match_details)
        print(f"\n{'--- REVENUE STATISTICS ---':^60}")
        print(f"Base Fare:                ${PRICE_BASE:.2f}")
        print(f"Markup:                   {MARKUP_PERCENT*100:.0f}%")
        print(f"Fare per Passenger:       ${match_details[0]['fare']:.2f}")
        print(f"Total Revenue:            ${total_revenue:.2f}")
        print(f"Avg Revenue per Driver:   ${total_revenue/len(drivers):.2f}")
    
    # Detailed match list
    if match_details:
        print(f"\n{'--- MATCH DETAILS ---':^60}")
        print(f"{'Driver':<18} {'Passenger':<18} {'Pickup':<10} {'Dropoff':<10}")
        print("-" * 60)
        
        # Group matches by driver
        driver_matches = {}
        for m in match_details:
            d_id = m['driver'].id
            if d_id not in driver_matches:
                driver_matches[d_id] = []
            driver_matches[d_id].append(m)
        
        for d_id in sorted(driver_matches.keys()):
            matches = driver_matches[d_id]
            driver = matches[0]['driver']
            print(f"\n{driver.name} ({driver.vehicle_type}) - {driver.schedule}:00")
            print(f"  Route: {driver.home_neighborhood} -> {driver.work_area}")
            for m in matches:
                p = m['passenger']
                print(f"  + {p.name:<16} {m['pickup_dist']:.3f} km   {m['dropoff_dist']:.3f} km")
    
    # Show some unmatched passengers and why
    if unmatched_passengers:
        print(f"\n{'--- SAMPLE UNMATCHED PASSENGERS ---':^60}")
        print("(First 5 unmatched passengers with reasons)")
        for p in unmatched_passengers[:5]:
            print(f"\n{p.name} (Schedule: {p.schedule}:00, {p.home_neighborhood})")
            # Find closest driver
            closest_driver = None
            closest_dist = float('inf')
            rejection_reason = "Unknown"
            
            for d in drivers:
                dist_origin = haversine(d.origin, p.origin)
                dist_dest = haversine(d.dest, p.dest)
                
                if dist_origin < closest_dist:
                    closest_dist = dist_origin
                    closest_driver = d
                    
                    if dist_origin > SEARCH_RADIUS_KM:
                        rejection_reason = f"Origin too far ({dist_origin:.2f}km > {SEARCH_RADIUS_KM}km)"
                    elif dist_dest > SEARCH_RADIUS_KM:
                        rejection_reason = f"Destination too far ({dist_dest:.2f}km > {SEARCH_RADIUS_KM}km)"
                    elif abs(d.schedule - p.schedule) > 1:
                        rejection_reason = f"Schedule mismatch (Driver: {d.schedule}:00, Passenger: {p.schedule}:00)"
                    elif len(d.passengers) >= MAX_CAPACITY:
                        rejection_reason = "Driver at full capacity"
                    else:
                        rejection_reason = "No compatible driver found"
            
            if closest_driver:
                print(f"  Closest driver: {closest_driver.name} ({closest_dist:.2f}km away)")
            print(f"  Reason: {rejection_reason}")

# --- 6. VISUALIZATION ---

def plot_simulation(drivers, passengers, match_details, neighborhoods, work_areas):
    """Create a detailed visualization of the simulation"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    # Left plot: Geographic visualization
    ax1 = axes[0]
    
    # Plot neighborhood and work area centers
    for n in neighborhoods:
        ax1.scatter(n['center'][1], n['center'][0], c='blue', marker='^', s=200, 
                   alpha=0.3, edgecolors='blue', linewidths=2)
        circle = plt.Circle((n['center'][1], n['center'][0]), CLUSTER_RADIUS_KM/111.32, 
                            fill=False, color='blue', linestyle='--', alpha=0.3)
        ax1.add_patch(circle)
    
    for w in work_areas:
        ax1.scatter(w['center'][1], w['center'][0], c='purple', marker='*', s=300, 
                   alpha=0.5, edgecolors='purple', linewidths=2)
    
    # Plot Unmatched Passengers
    unmatched_x = [p.origin[1] for p in passengers if p.matched_driver is None]
    unmatched_y = [p.origin[0] for p in passengers if p.matched_driver is None]
    ax1.scatter(unmatched_x, unmatched_y, c='grey', alpha=0.4, s=20, label='Unmatched Passenger')

    # Plot Drivers and their Routes
    for d in drivers:
        color = 'red' if len(d.passengers) == 0 else 'darkgreen'
        ax1.scatter(d.origin[1], d.origin[0], c=color, marker='s', s=80, edgecolors='black', zorder=10)
        ax1.arrow(d.origin[1], d.origin[0], 
                  d.dest[1] - d.origin[1], d.dest[0] - d.origin[0], 
                  head_width=0.003, color=color, alpha=0.3, length_includes_head=True)
        
        for p in d.passengers:
            ax1.plot([d.origin[1], p.origin[1]], [d.origin[0], p.origin[0]], 'g-', linewidth=1.5, alpha=0.7)
            ax1.scatter(p.origin[1], p.origin[0], c='limegreen', s=40, zorder=5, edgecolors='darkgreen')

    # Legend
    ax1.scatter([], [], c='blue', marker='^', s=100, alpha=0.5, label='Neighborhood Center')
    ax1.scatter([], [], c='purple', marker='*', s=150, label='Work Area Center')
    ax1.scatter([], [], c='darkgreen', marker='s', s=60, label='Active Driver')
    ax1.scatter([], [], c='red', marker='s', s=60, label='Inactive Driver')
    ax1.scatter([], [], c='limegreen', s=30, edgecolors='darkgreen', label='Matched Passenger')
    ax1.plot([], [], 'g-', linewidth=1.5, label='Match Connection')

    matched_count = sum(1 for p in passengers if p.matched_driver)
    ax1.set_title(f"Carpooling Matching - {matched_count}/{len(passengers)} matched ({matched_count/len(passengers)*100:.1f}%)\n"
                  f"Radius: {SEARCH_RADIUS_KM}km | Capacity: {MAX_CAPACITY}")
    ax1.set_xlabel("Longitude")
    ax1.set_ylabel("Latitude")
    ax1.legend(loc='upper right', fontsize=8)
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.set_aspect('equal')
    
    # Right plot: Statistics bar chart
    ax2 = axes[1]
    
    # Car occupancy data
    occupancy_counts = [
        sum(1 for d in drivers if len(d.passengers) == 0),
        sum(1 for d in drivers if len(d.passengers) == 1),
        sum(1 for d in drivers if len(d.passengers) == 2),
        sum(1 for d in drivers if len(d.passengers) == 3),
        sum(1 for d in drivers if len(d.passengers) == 4),
    ]
    
    colors = ['#ff6b6b', '#ffa94d', '#ffd43b', '#69db7c', '#20c997']
    bars = ax2.bar(['Empty', '1 Pass', '2 Pass', '3 Pass', 'Full (4)'], occupancy_counts, color=colors)
    
    ax2.set_xlabel('Car Occupancy')
    ax2.set_ylabel('Number of Cars')
    ax2.set_title('Car Occupancy Distribution')
    
    # Add value labels on bars
    for bar, count in zip(bars, occupancy_counts):
        if count > 0:
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, 
                    str(count), ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    # Add summary text
    total_matched = sum(1 for p in passengers if p.matched_driver)
    fleet_occ = total_matched / (len(drivers) * MAX_CAPACITY) * 100
    summary_text = (f"Summary:\n"
                   f"Drivers: {len(drivers)}\n"
                   f"Passengers: {len(passengers)}\n"
                   f"Matched: {total_matched} ({total_matched/len(passengers)*100:.1f}%)\n"
                   f"Fleet Occupancy: {fleet_occ:.1f}%")
    ax2.text(0.98, 0.98, summary_text, transform=ax2.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig("simulation_result.png", dpi=150)
    plt.close()
    print(f"\nVisualization saved to: simulation_result.png")

# --- 7. MAIN EXECUTION ---

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print(f"{'CARPOOLING SIMULATION':^60}")
    print(f"{'Optimized Matching Algorithm':^60}")
    print("=" * 60)
    print(f"Run Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # A. Generate Random Pool with Clusters
    drivers, passengers, neighborhoods, work_areas = generate_random_pool()
    
    # B. Print Pool Details
    print_pool_details(drivers, passengers, neighborhoods, work_areas)
    
    # C. Run Algorithm
    print("\n" + "=" * 60)
    print(f"{'RUNNING MATCHING ALGORITHM':^60}")
    print("=" * 60)
    match_details = match_algorithm(drivers, passengers)
    
    # D. Print Detailed Results
    print_matching_results(drivers, passengers, match_details)
    
    # E. Visualize
    plot_simulation(drivers, passengers, match_details, neighborhoods, work_areas)
    
    # F. Final Summary
    print("\n" + "=" * 60)
    print(f"{'SIMULATION COMPLETE':^60}")
    print("=" * 60)
    matched = sum(1 for p in passengers if p.matched_driver)
    full_cars = sum(1 for d in drivers if len(d.passengers) == MAX_CAPACITY)
    active_cars = sum(1 for d in drivers if len(d.passengers) > 0)
    
    print(f"\n{'='*20} FINAL SUMMARY {'='*20}")
    print(f"  Drivers:           {len(drivers)}")
    print(f"  Passengers:        {len(passengers)}")
    print(f"  Matched:           {matched}/{len(passengers)} ({matched/len(passengers)*100:.1f}%)")
    print(f"  Active Cars:       {active_cars}/{len(drivers)} ({active_cars/len(drivers)*100:.1f}%)")
    print(f"  Full Cars:         {full_cars}/{len(drivers)} ({full_cars/len(drivers)*100:.1f}%)")
    print(f"  Fleet Occupancy:   {matched/(len(drivers)*MAX_CAPACITY)*100:.1f}%")
    print(f"\n  Results saved to: simulation_result.png")
    print("\n  Run again for a new random simulation!")
    print("=" * 60 + "\n")
