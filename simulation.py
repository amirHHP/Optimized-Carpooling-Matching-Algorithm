import numpy as np
import random
import math
import json
import webbrowser
import os
from datetime import datetime
from scipy.optimize import linear_sum_assignment
import folium

# --- 1. CONFIGURATION & CONSTANTS ---
CITY_CENTER = (35.6892, 51.3890)  # Tehran coordinates
AREA_SIZE_KM = 5.0
SEARCH_RADIUS_KM = 1.0
MAX_CAPACITY = 4
PRICE_BASE = 100
MARKUP_PERCENT = 0.20

NUM_NEIGHBORHOODS = 5
NUM_WORK_AREAS = 3
CLUSTER_RADIUS_KM = 1.5

class User:
    def __init__(self, uid, role, origin, dest, name=None):
        self.id = uid
        self.name = name or f"{role.capitalize()}_{uid}"
        self.role = role
        self.origin = origin
        self.dest = dest
        self.schedule = random.randint(7, 11)
        self.days = {0, 1, 2, 3, 4}

class Driver(User):
    def __init__(self, uid, origin, dest, name=None):
        super().__init__(uid, 'driver', origin, dest, name)
        self.capacity = MAX_CAPACITY
        self.passengers = []
        self.vehicle_type = random.choice(['Sedan', 'SUV', 'Hatchback', 'Van'])
        self.home_neighborhood = None
        self.work_area = None
        
    def get_route_distance(self):
        return haversine(self.origin, self.dest)

class Passenger(User):
    def __init__(self, uid, origin, dest, name=None):
        super().__init__(uid, 'passenger', origin, dest, name)
        self.matched_driver = None
        self.pickup_distance = None
        self.dropoff_distance = None
        self.fare = 0
        self.home_neighborhood = None
        self.work_area = None
        
    def get_trip_distance(self):
        return haversine(self.origin, self.dest)

# --- 2. HELPER FUNCTIONS ---
def haversine(coord1, coord2):
    R = 6371
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def generate_random_point(center, radius_km):
    y0, x0 = center
    r = radius_km / 111.32
    u, v = np.random.uniform(0, 1), np.random.uniform(0, 1)
    w = r * math.sqrt(u)
    t = 2 * math.pi * v
    x = w * math.cos(t)
    y = w * math.sin(t)
    return (y0 + y, x0 + x)

def generate_random_name(role, uid):
    first_names = ['Ali', 'Sara', 'Reza', 'Mina', 'Hassan', 'Fatima', 'Mohammad', 'Zahra', 
                   'Amir', 'Leila', 'Mehdi', 'Narges', 'Hossein', 'Parisa', 'Ahmad', 'Negar']
    return f"{random.choice(first_names)}_{uid}"

# --- 3. POOL GENERATION WITH SCENARIOS ---
def generate_clusters():
    neighborhoods = []
    work_areas = []
    for i in range(NUM_NEIGHBORHOODS):
        center = generate_random_point(CITY_CENTER, AREA_SIZE_KM * 0.7)
        neighborhoods.append({'name': f"Neighborhood_{i+1}", 'center': center})
    for i in range(NUM_WORK_AREAS):
        center = generate_random_point(CITY_CENTER, AREA_SIZE_KM * 0.5)
        work_areas.append({'name': f"WorkArea_{i+1}", 'center': center})
    return neighborhoods, work_areas

def generate_random_pool(scenario='normal'):
    if scenario == 'rush_hour':
        num_drivers = random.randint(10, 20)
        num_passengers = random.randint(120, 150)
    elif scenario == 'driver_shortage':
        num_drivers = random.randint(5, 10)
        num_passengers = random.randint(50, 80)
    else:
        num_drivers = random.randint(20, 30)
        num_passengers = random.randint(50, 80)
        
    neighborhoods, work_areas = generate_clusters()
    
    drivers = []
    for i in range(num_drivers):
        home = random.choice(neighborhoods)
        work = random.choice(work_areas)
        d_org = generate_random_point(home['center'], CLUSTER_RADIUS_KM)
        d_dst = generate_random_point(work['center'], CLUSTER_RADIUS_KM)
        driver = Driver(i, d_org, d_dst, generate_random_name('driver', i))
        driver.home_neighborhood = home['name']
        driver.work_area = work['name']
        drivers.append(driver)
        
    passengers = []
    for i in range(num_passengers):
        home = random.choice(neighborhoods)
        work = random.choice(work_areas)
        p_org = generate_random_point(home['center'], CLUSTER_RADIUS_KM)
        p_dst = generate_random_point(work['center'], CLUSTER_RADIUS_KM)
        passenger = Passenger(i, p_org, p_dst, generate_random_name('passenger', i))
        passenger.home_neighborhood = home['name']
        passenger.work_area = work['name']
        passengers.append(passenger)
        
    return drivers, passengers, neighborhoods, work_areas

# --- 4. GLOBAL MATCHING ALGORITHM ---
def global_match_algorithm(drivers, passengers):
    match_details = []
    driver_seats = []
    
    for d in drivers:
        for _ in range(d.capacity):
            driver_seats.append(d)
            
    num_seats = len(driver_seats)
    num_pass = len(passengers)
    MAX_COST = 999999
    
    if num_seats == 0 or num_pass == 0:
        return []
        
    cost_matrix = np.full((num_seats, num_pass), MAX_COST, dtype=float)
    
    for i, seat in enumerate(driver_seats):
        for j, p in enumerate(passengers):
            dist_origin = haversine(seat.origin, p.origin)
            dist_dest = haversine(seat.dest, p.dest)
            
            if dist_origin <= SEARCH_RADIUS_KM and dist_dest <= SEARCH_RADIUS_KM:
                if abs(seat.schedule - p.schedule) <= 1:
                    cost_matrix[i, j] = dist_origin + dist_dest

    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    
    for i, j in zip(row_ind, col_ind):
        cost = cost_matrix[i, j]
        if cost < MAX_COST:
            driver = driver_seats[i]
            p = passengers[j]
            
            if not p.matched_driver:
                p.matched_driver = driver
                p.pickup_distance = haversine(driver.origin, p.origin)
                p.dropoff_distance = haversine(driver.dest, p.dest)
                
                driver.passengers.append(p)
                driver.capacity -= 1
                
                ride_cost = (PRICE_BASE / 4) + (PRICE_BASE * MARKUP_PERCENT)
                p.fare = ride_cost
                
                match_details.append({
                    'driver': driver,
                    'passenger': p,
                    'pickup_dist': p.pickup_distance,
                    'dropoff_dist': p.dropoff_distance,
                    'fare': ride_cost
                })
                
    return match_details

# --- 5. VISUALIZATION ---
def generate_folium_map(drivers, passengers, neighborhoods, work_areas, filename='interactive_map.html'):
    m = folium.Map(location=CITY_CENTER, zoom_start=12, tiles='CartoDB positron')
    
    for n in neighborhoods:
        folium.Circle(
            location=n['center'], radius=CLUSTER_RADIUS_KM*1000,
            color='#3498db', fill=True, fill_opacity=0.1, tooltip=f"Home: {n['name']}"
        ).add_to(m)
        
    for w in work_areas:
        folium.Circle(
            location=w['center'], radius=CLUSTER_RADIUS_KM*1000,
            color='#9b59b6', fill=True, fill_opacity=0.1, tooltip=f"Work: {w['name']}"
        ).add_to(m)

    for d in drivers:
        color = 'green' if len(d.passengers) > 0 else 'red'
        html_tooltip = f"<b>Driver:</b> {d.name}<br><b>Capacity:</b> {len(d.passengers)}/{MAX_CAPACITY}"
        folium.Marker(
            location=d.origin,
            icon=folium.Icon(color=color, icon='car', prefix='fa'),
            tooltip=html_tooltip
        ).add_to(m)
        
        folium.PolyLine(
            locations=[d.origin, d.dest],
            color=color, weight=3, opacity=0.4
        ).add_to(m)
        
    for p in passengers:
        color = 'blue' if p.matched_driver else 'gray'
        html_tooltip = f"<b>Passenger:</b> {p.name}<br><b>Matched:</b> {p.matched_driver.name if p.matched_driver else 'No'}"
        folium.Marker(
            location=p.origin,
            icon=folium.Icon(color=color, icon='user', prefix='fa'),
            tooltip=html_tooltip
        ).add_to(m)
        
        if p.matched_driver:
            folium.PolyLine(
                locations=[p.origin, p.matched_driver.origin],
                color='black', weight=2, dash_array='5, 5', opacity=0.6
            ).add_to(m)
            
    m.save(filename)
    print(f"Exported folium map to: {filename}")

def print_stats(drivers, passengers, match_details):
    matched = sum(1 for p in passengers if p.matched_driver)
    full_cars = sum(1 for d in drivers if len(d.passengers) == MAX_CAPACITY)
    active_cars = sum(1 for d in drivers if len(d.passengers) > 0)
    
    print(f"\n{'='*20} SUMMARY {'='*20}")
    print(f"  Drivers:           {len(drivers)}")
    print(f"  Passengers:        {len(passengers)}")
    print(f"  Matched Pass.:     {matched}/{len(passengers)} ({matched/len(passengers)*100:.1f}%)")
    print(f"  Active Cars:       {active_cars}/{len(drivers)} ({active_cars/len(drivers)*100:.1f}%)")
    if len(drivers) > 0:
        print(f"  Fleet Occupancy:   {sum(len(d.passengers) for d in drivers)/(len(drivers)*MAX_CAPACITY)*100:.1f}%")
    print("=" * 49 + "\n")

# --- 6. MAIN ---
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario', type=str, default='normal', choices=['normal', 'rush_hour', 'driver_shortage'])
    args = parser.parse_args()
    
    print(f"Starting Simulation... Scenario: {args.scenario}")
    drivers, passengers, neighborhoods, work_areas = generate_random_pool(scenario=args.scenario)
    
    match_details = global_match_algorithm(drivers, passengers)
    
    print_stats(drivers, passengers, match_details)
    generate_folium_map(drivers, passengers, neighborhoods, work_areas)
    
    html_path = os.path.abspath('interactive_map.html')
    print(f"Opening {html_path}")
    try:
        webbrowser.open(f'file://{html_path}')
    except:
        pass
