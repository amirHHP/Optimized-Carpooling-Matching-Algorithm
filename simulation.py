import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for headless environments
import matplotlib.pyplot as plt
import random
import math
import json
import webbrowser
import os
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
        self.schedule = random.randint(7, 11)  # Morning commute hour (7-11 AM)
        self.days = {0, 1, 2, 3, 4}  # Mon-Fri

class Driver(User):
    def __init__(self, uid, origin, dest, name=None):
        super().__init__(uid, 'driver', origin, dest, name)
        self.capacity = MAX_CAPACITY
        self.passengers = []
        self.route_score = 0
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
        self.rejection_reasons = []  # Store why each driver rejected this passenger
        
    def get_trip_distance(self):
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
    
    for i in range(NUM_NEIGHBORHOODS):
        center = generate_random_point(CITY_CENTER, AREA_SIZE_KM * 0.7)
        neighborhoods.append({
            'name': f"Neighborhood_{i+1}",
            'center': center
        })
    
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
    
    print(f"Generating {num_drivers} drivers...")
    for i in range(num_drivers):
        home_cluster = random.choice(neighborhoods)
        d_org = generate_random_point(home_cluster['center'], CLUSTER_RADIUS_KM)
        work_cluster = random.choice(work_areas)
        d_dst = generate_random_point(work_cluster['center'], CLUSTER_RADIUS_KM)
        
        name = generate_random_name('driver', i)
        driver = Driver(i, d_org, d_dst, name)
        driver.home_neighborhood = home_cluster['name']
        driver.work_area = work_cluster['name']
        drivers.append(driver)
    
    print(f"Generating {num_passengers} passengers...")
    for i in range(num_passengers):
        home_cluster = random.choice(neighborhoods)
        p_org = generate_random_point(home_cluster['center'], CLUSTER_RADIUS_KM)
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
    Also records rejection reasons for each passenger.
    """
    match_details = []
    
    # First, calculate rejection reasons for all passengers against all drivers
    for p in passengers:
        p.rejection_reasons = []
        for d in drivers:
            dist_origin = haversine(d.origin, p.origin)
            dist_dest = haversine(d.dest, p.dest)
            
            reasons = []
            if dist_origin > SEARCH_RADIUS_KM:
                reasons.append(f"Origin too far: {dist_origin:.2f}km (max {SEARCH_RADIUS_KM}km)")
            if dist_dest > SEARCH_RADIUS_KM:
                reasons.append(f"Destination too far: {dist_dest:.2f}km (max {SEARCH_RADIUS_KM}km)")
            if abs(d.schedule - p.schedule) > 1:
                reasons.append(f"Schedule mismatch: Driver {d.schedule}:00, Passenger {p.schedule}:00")
            
            p.rejection_reasons.append({
                'driver_id': d.id,
                'driver_name': d.name,
                'pickup_distance': dist_origin,
                'dropoff_distance': dist_dest,
                'reasons': reasons,
                'is_compatible': len(reasons) == 0
            })
    
    # Shuffle drivers to randomize order
    random.shuffle(drivers)
    
    for driver in drivers:
        if driver.capacity == 0:
            continue
            
        candidates = []
        for p in passengers:
            if p.matched_driver is not None:
                continue
            
            dist_origin = haversine(driver.origin, p.origin)
            if dist_origin > SEARCH_RADIUS_KM:
                continue
                
            dist_dest = haversine(driver.dest, p.dest)
            if dist_dest > SEARCH_RADIUS_KM:
                continue
                
            if abs(driver.schedule - p.schedule) > 1:
                continue

            candidates.append((p, dist_origin, dist_dest))
        
        candidates.sort(key=lambda x: x[1] + x[2])
        
        slots = driver.capacity
        selected = candidates[:slots]
        
        for p_tuple in selected:
            p, dist_origin, dist_dest = p_tuple
            p.matched_driver = driver
            p.pickup_distance = dist_origin
            p.dropoff_distance = dist_dest
            driver.passengers.append(p)
            driver.capacity -= 1
            
            ride_cost = (PRICE_BASE / 4) + (PRICE_BASE * MARKUP_PERCENT)
            p.fare = ride_cost
            
            match_details.append({
                'driver': driver,
                'passenger': p,
                'pickup_dist': dist_origin,
                'dropoff_dist': dist_dest,
                'fare': ride_cost
            })
    
    # Update rejection reasons for matched passengers
    for p in passengers:
        if p.matched_driver:
            for reason in p.rejection_reasons:
                if reason['driver_id'] == p.matched_driver.id:
                    reason['matched'] = True
                else:
                    reason['matched'] = False
    
    return match_details

# --- 5. EXPORT DATA FOR INTERACTIVE VISUALIZATION ---

def export_visualization_data(drivers, passengers, neighborhoods, work_areas, match_details):
    """Export simulation data to JSON for interactive visualization"""
    
    data = {
        'config': {
            'city_center': CITY_CENTER,
            'area_size_km': AREA_SIZE_KM,
            'search_radius_km': SEARCH_RADIUS_KM,
            'cluster_radius_km': CLUSTER_RADIUS_KM,
            'max_capacity': MAX_CAPACITY,
            'price_base': PRICE_BASE,
            'markup_percent': MARKUP_PERCENT
        },
        'neighborhoods': [
            {'name': n['name'], 'lat': n['center'][0], 'lon': n['center'][1]}
            for n in neighborhoods
        ],
        'work_areas': [
            {'name': w['name'], 'lat': w['center'][0], 'lon': w['center'][1]}
            for w in work_areas
        ],
        'drivers': [
            {
                'id': d.id,
                'name': d.name,
                'origin': {'lat': d.origin[0], 'lon': d.origin[1]},
                'dest': {'lat': d.dest[0], 'lon': d.dest[1]},
                'schedule': d.schedule,
                'vehicle_type': d.vehicle_type,
                'home_neighborhood': d.home_neighborhood,
                'work_area': d.work_area,
                'route_distance': d.get_route_distance(),
                'passenger_count': len(d.passengers),
                'passenger_ids': [p.id for p in d.passengers]
            }
            for d in drivers
        ],
        'passengers': [
            {
                'id': p.id,
                'name': p.name,
                'origin': {'lat': p.origin[0], 'lon': p.origin[1]},
                'dest': {'lat': p.dest[0], 'lon': p.dest[1]},
                'schedule': p.schedule,
                'home_neighborhood': p.home_neighborhood,
                'work_area': p.work_area,
                'trip_distance': p.get_trip_distance(),
                'matched': p.matched_driver is not None,
                'matched_driver_id': p.matched_driver.id if p.matched_driver else None,
                'matched_driver_name': p.matched_driver.name if p.matched_driver else None,
                'pickup_distance': p.pickup_distance,
                'dropoff_distance': p.dropoff_distance,
                'fare': p.fare,
                'rejection_analysis': p.rejection_reasons
            }
            for p in passengers
        ],
        'statistics': {
            'total_drivers': len(drivers),
            'total_passengers': len(passengers),
            'matched_passengers': sum(1 for p in passengers if p.matched_driver),
            'full_cars': sum(1 for d in drivers if len(d.passengers) == MAX_CAPACITY),
            'active_cars': sum(1 for d in drivers if len(d.passengers) > 0),
            'fleet_occupancy': sum(len(d.passengers) for d in drivers) / (len(drivers) * MAX_CAPACITY) * 100,
            'total_revenue': sum(p.fare for p in passengers if p.matched_driver)
        }
    }
    
    with open('simulation_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Exported simulation data to: simulation_data.json")
    return data

# --- 6. GENERATE INTERACTIVE HTML ---

def generate_interactive_html(data):
    """Generate an interactive HTML visualization with embedded data"""
    
    # Convert data to JSON string for embedding
    data_json = json.dumps(data)
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Carpooling Simulation - Interactive Visualization</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
        }
        
        .header {
            background: rgba(0,0,0,0.3);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .header h1 {
            font-size: 1.5em;
            color: #4cc9f0;
        }
        
        .stats-bar {
            display: flex;
            gap: 20px;
        }
        
        .stat-item {
            text-align: center;
            padding: 5px 15px;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
        }
        
        .stat-value {
            font-size: 1.4em;
            font-weight: bold;
            color: #4cc9f0;
        }
        
        .stat-label {
            font-size: 0.75em;
            color: #aaa;
        }
        
        .container {
            display: flex;
            height: calc(100vh - 70px);
        }
        
        .canvas-container {
            flex: 1;
            position: relative;
            overflow: hidden;
        }
        
        #mainCanvas {
            background: #0f0f23;
            cursor: crosshair;
        }
        
        .sidebar {
            width: 400px;
            background: rgba(0,0,0,0.4);
            border-left: 1px solid rgba(255,255,255,0.1);
            overflow-y: auto;
            padding: 20px;
        }
        
        .panel {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .panel-title {
            font-size: 1.1em;
            color: #4cc9f0;
            margin-bottom: 10px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            font-size: 0.9em;
        }
        
        .info-label {
            color: #888;
        }
        
        .info-value {
            color: #fff;
            font-weight: 500;
        }
        
        .matched {
            color: #2ecc71 !important;
        }
        
        .unmatched {
            color: #e74c3c !important;
        }
        
        .driver-analysis {
            margin-top: 15px;
        }
        
        .driver-card {
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.2s;
            border-left: 3px solid transparent;
        }
        
        .driver-card:hover {
            background: rgba(255,255,255,0.1);
        }
        
        .driver-card.compatible {
            border-left-color: #2ecc71;
        }
        
        .driver-card.incompatible {
            border-left-color: #e74c3c;
        }
        
        .driver-card.selected-match {
            border-left-color: #f39c12;
            background: rgba(243, 156, 18, 0.2);
        }
        
        .driver-name {
            font-weight: bold;
            color: #4cc9f0;
        }
        
        .rejection-reason {
            font-size: 0.8em;
            color: #e74c3c;
            margin-top: 5px;
            padding-left: 10px;
            border-left: 2px solid #e74c3c;
        }
        
        .distance-bar {
            height: 6px;
            background: rgba(255,255,255,0.1);
            border-radius: 3px;
            margin-top: 5px;
            overflow: hidden;
        }
        
        .distance-fill {
            height: 100%;
            border-radius: 3px;
            transition: width 0.3s;
        }
        
        .legend {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            padding: 10px;
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            margin-bottom: 15px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.85em;
        }
        
        .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.2s;
        }
        
        .btn-primary {
            background: #4cc9f0;
            color: #000;
        }
        
        .btn-primary:hover {
            background: #3ab4db;
        }
        
        .btn-secondary {
            background: rgba(255,255,255,0.1);
            color: #fff;
        }
        
        .btn-secondary:hover {
            background: rgba(255,255,255,0.2);
        }
        
        .filter-section {
            margin-bottom: 15px;
        }
        
        .filter-label {
            font-size: 0.85em;
            color: #888;
            margin-bottom: 5px;
        }
        
        .filter-buttons {
            display: flex;
            gap: 5px;
        }
        
        .filter-btn {
            padding: 5px 12px;
            border: 1px solid rgba(255,255,255,0.2);
            background: transparent;
            color: #fff;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8em;
        }
        
        .filter-btn.active {
            background: #4cc9f0;
            color: #000;
            border-color: #4cc9f0;
        }
        
        .tooltip {
            position: absolute;
            background: rgba(0,0,0,0.9);
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 0.85em;
            pointer-events: none;
            z-index: 1000;
            border: 1px solid rgba(255,255,255,0.2);
            max-width: 250px;
        }
        
        .no-selection {
            text-align: center;
            color: #666;
            padding: 40px 20px;
        }
        
        .no-selection-icon {
            font-size: 3em;
            margin-bottom: 15px;
        }
        
        .route-info {
            background: rgba(76, 201, 240, 0.1);
            border: 1px solid rgba(76, 201, 240, 0.3);
            border-radius: 8px;
            padding: 10px;
            margin-top: 10px;
        }
        
        .compatible-count {
            font-size: 0.85em;
            color: #888;
            margin-top: 10px;
        }
        
        .compatible-count span {
            color: #2ecc71;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚗 Carpooling Simulation - Interactive Map</h1>
        <div class="stats-bar">
            <div class="stat-item">
                <div class="stat-value" id="statDrivers">-</div>
                <div class="stat-label">Drivers</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="statPassengers">-</div>
                <div class="stat-label">Passengers</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="statMatched">-</div>
                <div class="stat-label">Matched</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="statOccupancy">-</div>
                <div class="stat-label">Fleet Occupancy</div>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="canvas-container">
            <canvas id="mainCanvas"></canvas>
            <div class="tooltip" id="tooltip" style="display: none;"></div>
        </div>
        
        <div class="sidebar">
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color" style="background: #e74c3c;"></div>
                    <span>Inactive Driver</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #2ecc71;"></div>
                    <span>Active Driver</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #95a5a6;"></div>
                    <span>Unmatched Passenger</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #27ae60;"></div>
                    <span>Matched Passenger</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #3498db; opacity: 0.3;"></div>
                    <span>Neighborhood</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #9b59b6;"></div>
                    <span>Work Area</span>
                </div>
            </div>
            
            <div class="controls">
                <button class="btn btn-primary" onclick="resetView()">Reset View</button>
                <button class="btn btn-secondary" onclick="clearSelection()">Clear Selection</button>
            </div>
            
            <div class="filter-section">
                <div class="filter-label">Show:</div>
                <div class="filter-buttons">
                    <button class="filter-btn active" data-filter="all" onclick="setFilter('all')">All</button>
                    <button class="filter-btn" data-filter="matched" onclick="setFilter('matched')">Matched</button>
                    <button class="filter-btn" data-filter="unmatched" onclick="setFilter('unmatched')">Unmatched</button>
                </div>
            </div>
            
            <div id="selectionInfo">
                <div class="no-selection">
                    <div class="no-selection-icon">👆</div>
                    <p>Click on a passenger or driver to see details</p>
                    <p style="font-size: 0.85em; margin-top: 10px; color: #555;">
                        Hover over points to see quick info
                    </p>
                </div>
            </div>
        </div>
    </div>

    <script>
        let data = null;
        let canvas, ctx;
        let selectedEntity = null;
        let hoveredEntity = null;
        let currentFilter = 'all';
        
        // View transformation
        let viewOffset = { x: 0, y: 0 };
        let viewScale = 1;
        let isDragging = false;
        let lastMouse = { x: 0, y: 0 };
        
        // Load embedded data
        data = __DATA_JSON_PLACEHOLDER__;
        
        // Initialize when DOM is ready
        document.addEventListener('DOMContentLoaded', function() {
            initCanvas();
            updateStats();
            render();
        });
        
        function initCanvas() {
            canvas = document.getElementById('mainCanvas');
            ctx = canvas.getContext('2d');
            
            resizeCanvas();
            window.addEventListener('resize', () => {
                resizeCanvas();
                render();
            });
            
            canvas.addEventListener('mousemove', handleMouseMove);
            canvas.addEventListener('click', handleClick);
            canvas.addEventListener('mousedown', handleMouseDown);
            canvas.addEventListener('mouseup', handleMouseUp);
            canvas.addEventListener('wheel', handleWheel);
            canvas.addEventListener('mouseleave', () => {
                hoveredEntity = null;
                document.getElementById('tooltip').style.display = 'none';
                render();
            });
        }
        
        function resizeCanvas() {
            const container = canvas.parentElement;
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
            resetView();
        }
        
        function resetView() {
            if (!data) return;
            
            // Calculate bounds
            let minLat = Infinity, maxLat = -Infinity;
            let minLon = Infinity, maxLon = -Infinity;
            
            [...data.drivers, ...data.passengers].forEach(entity => {
                minLat = Math.min(minLat, entity.origin.lat, entity.dest.lat);
                maxLat = Math.max(maxLat, entity.origin.lat, entity.dest.lat);
                minLon = Math.min(minLon, entity.origin.lon, entity.dest.lon);
                maxLon = Math.max(maxLon, entity.origin.lon, entity.dest.lon);
            });
            
            const padding = 50;
            const latRange = maxLat - minLat;
            const lonRange = maxLon - minLon;
            
            const scaleX = (canvas.width - padding * 2) / lonRange;
            const scaleY = (canvas.height - padding * 2) / latRange;
            viewScale = Math.min(scaleX, scaleY) * 0.9;
            
            viewOffset.x = canvas.width / 2 - (minLon + lonRange / 2) * viewScale;
            viewOffset.y = canvas.height / 2 + (minLat + latRange / 2) * viewScale;
            
            render();
        }
        
        function worldToScreen(lon, lat) {
            return {
                x: lon * viewScale + viewOffset.x,
                y: -lat * viewScale + viewOffset.y
            };
        }
        
        function screenToWorld(x, y) {
            return {
                lon: (x - viewOffset.x) / viewScale,
                lat: -(y - viewOffset.y) / viewScale
            };
        }
        
        function handleMouseDown(e) {
            isDragging = true;
            lastMouse = { x: e.clientX, y: e.clientY };
        }
        
        function handleMouseUp() {
            isDragging = false;
        }
        
        function handleWheel(e) {
            e.preventDefault();
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            
            const world = screenToWorld(mouseX, mouseY);
            const scaleFactor = e.deltaY > 0 ? 0.9 : 1.1;
            viewScale *= scaleFactor;
            
            viewOffset.x = mouseX - world.lon * viewScale;
            viewOffset.y = mouseY + world.lat * viewScale;
            
            render();
        }
        
        function handleMouseMove(e) {
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            
            if (isDragging) {
                viewOffset.x += e.clientX - lastMouse.x;
                viewOffset.y += e.clientY - lastMouse.y;
                lastMouse = { x: e.clientX, y: e.clientY };
                render();
                return;
            }
            
            // Check hover
            hoveredEntity = findEntityAt(mouseX, mouseY);
            
            const tooltip = document.getElementById('tooltip');
            if (hoveredEntity) {
                tooltip.style.display = 'block';
                tooltip.style.left = (e.clientX + 15) + 'px';
                tooltip.style.top = (e.clientY + 15) + 'px';
                tooltip.innerHTML = getTooltipContent(hoveredEntity);
            } else {
                tooltip.style.display = 'none';
            }
            
            render();
        }
        
        function handleClick(e) {
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            
            selectedEntity = findEntityAt(mouseX, mouseY);
            updateSelectionInfo();
            render();
        }
        
        function findEntityAt(x, y) {
            const threshold = 15;
            
            // Check passengers first (they're on top)
            for (const p of data.passengers) {
                if (!shouldShowEntity(p)) continue;
                const pos = worldToScreen(p.origin.lon, p.origin.lat);
                const dist = Math.sqrt((pos.x - x) ** 2 + (pos.y - y) ** 2);
                if (dist < threshold) {
                    return { type: 'passenger', data: p };
                }
            }
            
            // Check drivers
            for (const d of data.drivers) {
                const pos = worldToScreen(d.origin.lon, d.origin.lat);
                const dist = Math.sqrt((pos.x - x) ** 2 + (pos.y - y) ** 2);
                if (dist < threshold) {
                    return { type: 'driver', data: d };
                }
            }
            
            return null;
        }
        
        function shouldShowEntity(entity) {
            if (currentFilter === 'all') return true;
            if (currentFilter === 'matched') return entity.matched;
            if (currentFilter === 'unmatched') return !entity.matched;
            return true;
        }
        
        function setFilter(filter) {
            currentFilter = filter;
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.filter === filter);
            });
            render();
        }
        
        function clearSelection() {
            selectedEntity = null;
            updateSelectionInfo();
            render();
        }
        
        function getTooltipContent(entity) {
            if (entity.type === 'passenger') {
                const p = entity.data;
                return `
                    <strong>${p.name}</strong><br>
                    ${p.matched ? '✅ Matched' : '❌ Unmatched'}<br>
                    Schedule: ${p.schedule}:00<br>
                    Trip: ${p.trip_distance.toFixed(2)} km
                `;
            } else {
                const d = entity.data;
                return `
                    <strong>${d.name}</strong> (${d.vehicle_type})<br>
                    Passengers: ${d.passenger_count}/${data.config.max_capacity}<br>
                    Schedule: ${d.schedule}:00<br>
                    Route: ${d.route_distance.toFixed(2)} km
                `;
            }
        }
        
        function updateStats() {
            document.getElementById('statDrivers').textContent = data.statistics.total_drivers;
            document.getElementById('statPassengers').textContent = data.statistics.total_passengers;
            document.getElementById('statMatched').textContent = 
                `${data.statistics.matched_passengers} (${(data.statistics.matched_passengers/data.statistics.total_passengers*100).toFixed(0)}%)`;
            document.getElementById('statOccupancy').textContent = 
                data.statistics.fleet_occupancy.toFixed(1) + '%';
        }
        
        function updateSelectionInfo() {
            const container = document.getElementById('selectionInfo');
            
            if (!selectedEntity) {
                container.innerHTML = `
                    <div class="no-selection">
                        <div class="no-selection-icon">👆</div>
                        <p>Click on a passenger or driver to see details</p>
                    </div>
                `;
                return;
            }
            
            if (selectedEntity.type === 'passenger') {
                renderPassengerInfo(container, selectedEntity.data);
            } else {
                renderDriverInfo(container, selectedEntity.data);
            }
        }
        
        function renderPassengerInfo(container, p) {
            const compatibleDrivers = p.rejection_analysis.filter(r => r.is_compatible).length;
            
            let html = `
                <div class="panel">
                    <div class="panel-title">👤 ${p.name}</div>
                    <div class="info-row">
                        <span class="info-label">Status</span>
                        <span class="info-value ${p.matched ? 'matched' : 'unmatched'}">
                            ${p.matched ? '✅ Matched' : '❌ Unmatched'}
                        </span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Schedule</span>
                        <span class="info-value">${p.schedule}:00</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Trip Distance</span>
                        <span class="info-value">${p.trip_distance.toFixed(2)} km</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Home Area</span>
                        <span class="info-value">${p.home_neighborhood}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Work Area</span>
                        <span class="info-value">${p.work_area}</span>
                    </div>
                    ${p.matched ? `
                        <div class="route-info">
                            <div class="info-row">
                                <span class="info-label">Matched Driver</span>
                                <span class="info-value">${p.matched_driver_name}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">Pickup Distance</span>
                                <span class="info-value">${p.pickup_distance.toFixed(3)} km</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">Dropoff Distance</span>
                                <span class="info-value">${p.dropoff_distance.toFixed(3)} km</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">Fare</span>
                                <span class="info-value">$${p.fare.toFixed(2)}</span>
                            </div>
                        </div>
                    ` : ''}
                </div>
                
                <div class="panel">
                    <div class="panel-title">🔍 Driver Compatibility Analysis</div>
                    <div class="compatible-count">
                        <span>${compatibleDrivers}</span> of ${data.drivers.length} drivers compatible
                    </div>
                    <div class="driver-analysis">
            `;
            
            // Sort: matched first, then compatible, then by distance
            const sortedAnalysis = [...p.rejection_analysis].sort((a, b) => {
                if (a.driver_id === p.matched_driver_id) return -1;
                if (b.driver_id === p.matched_driver_id) return 1;
                if (a.is_compatible && !b.is_compatible) return -1;
                if (!a.is_compatible && b.is_compatible) return 1;
                return a.pickup_distance - b.pickup_distance;
            });
            
            for (const analysis of sortedAnalysis) {
                const isMatched = analysis.driver_id === p.matched_driver_id;
                const driver = data.drivers.find(d => d.id === analysis.driver_id);
                
                let cardClass = 'driver-card';
                if (isMatched) cardClass += ' selected-match';
                else if (analysis.is_compatible) cardClass += ' compatible';
                else cardClass += ' incompatible';
                
                html += `
                    <div class="${cardClass}" onclick="highlightDriver(${analysis.driver_id})">
                        <div class="driver-name">
                            ${isMatched ? '⭐ ' : ''}${analysis.driver_name}
                            <span style="color: #888; font-weight: normal; font-size: 0.85em;">
                                (${driver.vehicle_type})
                            </span>
                        </div>
                        <div style="font-size: 0.85em; color: #888; margin-top: 3px;">
                            Schedule: ${driver.schedule}:00 | 
                            Pickup: ${analysis.pickup_distance.toFixed(2)}km | 
                            Dropoff: ${analysis.dropoff_distance.toFixed(2)}km
                        </div>
                        <div class="distance-bar">
                            <div class="distance-fill" style="
                                width: ${Math.min(analysis.pickup_distance / data.config.search_radius_km * 100, 100)}%;
                                background: ${analysis.pickup_distance <= data.config.search_radius_km ? '#2ecc71' : '#e74c3c'};
                            "></div>
                        </div>
                `;
                
                if (!analysis.is_compatible) {
                    html += `<div class="rejection-reason">`;
                    for (const reason of analysis.reasons) {
                        html += `• ${reason}<br>`;
                    }
                    html += `</div>`;
                } else if (!isMatched && p.matched) {
                    html += `<div class="rejection-reason" style="border-color: #f39c12; color: #f39c12;">
                        • Another passenger was a better match for this driver
                    </div>`;
                }
                
                html += `</div>`;
            }
            
            html += `</div></div>`;
            container.innerHTML = html;
        }
        
        function renderDriverInfo(container, d) {
            let html = `
                <div class="panel">
                    <div class="panel-title">🚗 ${d.name}</div>
                    <div class="info-row">
                        <span class="info-label">Vehicle</span>
                        <span class="info-value">${d.vehicle_type}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Schedule</span>
                        <span class="info-value">${d.schedule}:00</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Route Distance</span>
                        <span class="info-value">${d.route_distance.toFixed(2)} km</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Home Area</span>
                        <span class="info-value">${d.home_neighborhood}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Work Area</span>
                        <span class="info-value">${d.work_area}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Passengers</span>
                        <span class="info-value ${d.passenger_count > 0 ? 'matched' : 'unmatched'}">
                            ${d.passenger_count} / ${data.config.max_capacity}
                        </span>
                    </div>
                </div>
            `;
            
            if (d.passenger_count > 0) {
                html += `
                    <div class="panel">
                        <div class="panel-title">👥 Passengers (${d.passenger_count})</div>
                `;
                
                for (const pId of d.passenger_ids) {
                    const passenger = data.passengers.find(p => p.id === pId);
                    html += `
                        <div class="driver-card compatible" onclick="selectPassenger(${pId})">
                            <div class="driver-name">${passenger.name}</div>
                            <div style="font-size: 0.85em; color: #888;">
                                Pickup: ${passenger.pickup_distance.toFixed(3)}km | 
                                Dropoff: ${passenger.dropoff_distance.toFixed(3)}km
                            </div>
                        </div>
                    `;
                }
                
                html += `</div>`;
            }
            
            container.innerHTML = html;
        }
        
        function highlightDriver(driverId) {
            const driver = data.drivers.find(d => d.id === driverId);
            if (driver) {
                // Temporarily highlight this driver
                render();
                
                const pos = worldToScreen(driver.origin.lon, driver.origin.lat);
                ctx.beginPath();
                ctx.arc(pos.x, pos.y, 25, 0, Math.PI * 2);
                ctx.strokeStyle = '#f39c12';
                ctx.lineWidth = 3;
                ctx.stroke();
            }
        }
        
        function selectPassenger(passengerId) {
            const passenger = data.passengers.find(p => p.id === passengerId);
            if (passenger) {
                selectedEntity = { type: 'passenger', data: passenger };
                updateSelectionInfo();
                render();
            }
        }
        
        function render() {
            if (!data || !ctx) return;
            
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw grid
            drawGrid();
            
            // Draw neighborhood circles (residential areas)
            // Convert km to degrees: 1 degree ≈ 111.32 km
            const clusterRadiusDeg = data.config.cluster_radius_km / 111.32;
            
            for (const n of data.neighborhoods) {
                const pos = worldToScreen(n.lon, n.lat);
                // Calculate radius in screen pixels
                const radiusPixels = clusterRadiusDeg * viewScale;
                
                // Draw filled circle for neighborhood
                ctx.beginPath();
                ctx.arc(pos.x, pos.y, radiusPixels, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(52, 152, 219, 0.15)';
                ctx.fill();
                ctx.strokeStyle = 'rgba(52, 152, 219, 0.5)';
                ctx.lineWidth = 2;
                ctx.setLineDash([5, 5]);
                ctx.stroke();
                ctx.setLineDash([]);
                
                // Draw center marker
                ctx.beginPath();
                ctx.arc(pos.x, pos.y, 6, 0, Math.PI * 2);
                ctx.fillStyle = '#3498db';
                ctx.fill();
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 2;
                ctx.stroke();
                
                // Draw label
                ctx.font = '11px Arial';
                ctx.fillStyle = '#3498db';
                ctx.textAlign = 'center';
                ctx.fillText(n.name, pos.x, pos.y - 12);
            }
            
            // Draw work areas (destination clusters)
            for (const w of data.work_areas) {
                const pos = worldToScreen(w.lon, w.lat);
                const radiusPixels = clusterRadiusDeg * viewScale;
                
                // Draw filled circle for work area
                ctx.beginPath();
                ctx.arc(pos.x, pos.y, radiusPixels, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(155, 89, 182, 0.15)';
                ctx.fill();
                ctx.strokeStyle = 'rgba(155, 89, 182, 0.5)';
                ctx.lineWidth = 2;
                ctx.setLineDash([5, 5]);
                ctx.stroke();
                ctx.setLineDash([]);
                
                // Draw center marker (star shape)
                ctx.beginPath();
                const starSize = 8;
                for (let i = 0; i < 5; i++) {
                    const angle = (i * 4 * Math.PI / 5) - Math.PI / 2;
                    const x = pos.x + starSize * Math.cos(angle);
                    const y = pos.y + starSize * Math.sin(angle);
                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }
                ctx.closePath();
                ctx.fillStyle = '#9b59b6';
                ctx.fill();
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 1;
                ctx.stroke();
                
                // Draw label
                ctx.font = '11px Arial';
                ctx.fillStyle = '#9b59b6';
                ctx.textAlign = 'center';
                ctx.fillText(w.name, pos.x, pos.y - 14);
            }
            
            // Draw driver routes
            for (const d of data.drivers) {
                const from = worldToScreen(d.origin.lon, d.origin.lat);
                const to = worldToScreen(d.dest.lon, d.dest.lat);
                
                ctx.beginPath();
                ctx.moveTo(from.x, from.y);
                ctx.lineTo(to.x, to.y);
                ctx.strokeStyle = d.passenger_count > 0 ? 'rgba(46, 204, 113, 0.3)' : 'rgba(231, 76, 60, 0.2)';
                ctx.lineWidth = 2;
                ctx.stroke();
                
                // Draw arrow
                drawArrow(from, to, ctx.strokeStyle);
            }
            
            // Draw match connections
            if (selectedEntity && selectedEntity.type === 'passenger' && selectedEntity.data.matched) {
                const p = selectedEntity.data;
                const driver = data.drivers.find(d => d.id === p.matched_driver_id);
                if (driver) {
                    const pPos = worldToScreen(p.origin.lon, p.origin.lat);
                    const dPos = worldToScreen(driver.origin.lon, driver.origin.lat);
                    const pDest = worldToScreen(p.dest.lon, p.dest.lat);
                    const dDest = worldToScreen(driver.dest.lon, driver.dest.lat);
                    
                    // Pickup line
                    ctx.beginPath();
                    ctx.moveTo(dPos.x, dPos.y);
                    ctx.lineTo(pPos.x, pPos.y);
                    ctx.strokeStyle = '#f39c12';
                    ctx.lineWidth = 3;
                    ctx.setLineDash([5, 5]);
                    ctx.stroke();
                    ctx.setLineDash([]);
                    
                    // Dropoff line
                    ctx.beginPath();
                    ctx.moveTo(dDest.x, dDest.y);
                    ctx.lineTo(pDest.x, pDest.y);
                    ctx.strokeStyle = '#e67e22';
                    ctx.lineWidth = 2;
                    ctx.setLineDash([5, 5]);
                    ctx.stroke();
                    ctx.setLineDash([]);
                }
            }
            
            // Draw all match connections (faint)
            for (const d of data.drivers) {
                for (const pId of d.passenger_ids) {
                    const p = data.passengers.find(pass => pass.id === pId);
                    if (p) {
                        const dPos = worldToScreen(d.origin.lon, d.origin.lat);
                        const pPos = worldToScreen(p.origin.lon, p.origin.lat);
                        
                        ctx.beginPath();
                        ctx.moveTo(dPos.x, dPos.y);
                        ctx.lineTo(pPos.x, pPos.y);
                        ctx.strokeStyle = 'rgba(46, 204, 113, 0.4)';
                        ctx.lineWidth = 1;
                        ctx.stroke();
                    }
                }
            }
            
            // Draw passengers
            for (const p of data.passengers) {
                if (!shouldShowEntity(p)) continue;
                
                const pos = worldToScreen(p.origin.lon, p.origin.lat);
                const isSelected = selectedEntity?.type === 'passenger' && selectedEntity.data.id === p.id;
                const isHovered = hoveredEntity?.type === 'passenger' && hoveredEntity.data.id === p.id;
                
                ctx.beginPath();
                ctx.arc(pos.x, pos.y, isSelected ? 10 : (isHovered ? 8 : 6), 0, Math.PI * 2);
                
                if (isSelected) {
                    ctx.fillStyle = '#f39c12';
                } else if (p.matched) {
                    ctx.fillStyle = '#27ae60';
                } else {
                    ctx.fillStyle = '#95a5a6';
                }
                ctx.fill();
                
                if (isSelected || isHovered) {
                    ctx.strokeStyle = '#fff';
                    ctx.lineWidth = 2;
                    ctx.stroke();
                }
                
                // Draw destination for selected
                if (isSelected) {
                    const destPos = worldToScreen(p.dest.lon, p.dest.lat);
                    ctx.beginPath();
                    ctx.arc(destPos.x, destPos.y, 6, 0, Math.PI * 2);
                    ctx.fillStyle = '#e74c3c';
                    ctx.fill();
                    ctx.strokeStyle = '#fff';
                    ctx.lineWidth = 2;
                    ctx.stroke();
                    
                    // Line to destination
                    ctx.beginPath();
                    ctx.moveTo(pos.x, pos.y);
                    ctx.lineTo(destPos.x, destPos.y);
                    ctx.strokeStyle = 'rgba(241, 196, 15, 0.5)';
                    ctx.lineWidth = 2;
                    ctx.setLineDash([10, 5]);
                    ctx.stroke();
                    ctx.setLineDash([]);
                }
            }
            
            // Draw drivers
            for (const d of data.drivers) {
                const pos = worldToScreen(d.origin.lon, d.origin.lat);
                const isSelected = selectedEntity?.type === 'driver' && selectedEntity.data.id === d.id;
                const isHovered = hoveredEntity?.type === 'driver' && hoveredEntity.data.id === d.id;
                
                const size = isSelected ? 14 : (isHovered ? 12 : 10);
                
                ctx.beginPath();
                ctx.rect(pos.x - size/2, pos.y - size/2, size, size);
                
                if (isSelected) {
                    ctx.fillStyle = '#f39c12';
                } else if (d.passenger_count > 0) {
                    ctx.fillStyle = '#2ecc71';
                } else {
                    ctx.fillStyle = '#e74c3c';
                }
                ctx.fill();
                ctx.strokeStyle = '#000';
                ctx.lineWidth = 2;
                ctx.stroke();
                
                // Draw search radius for selected driver
                if (isSelected) {
                    const radius = data.config.search_radius_km * viewScale / 111.32 * 100;
                    ctx.beginPath();
                    ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);
                    ctx.strokeStyle = 'rgba(243, 156, 18, 0.5)';
                    ctx.lineWidth = 2;
                    ctx.setLineDash([5, 5]);
                    ctx.stroke();
                    ctx.setLineDash([]);
                    
                    // Draw destination
                    const destPos = worldToScreen(d.dest.lon, d.dest.lat);
                    ctx.beginPath();
                    ctx.rect(destPos.x - 6, destPos.y - 6, 12, 12);
                    ctx.fillStyle = '#e74c3c';
                    ctx.fill();
                    ctx.strokeStyle = '#fff';
                    ctx.lineWidth = 2;
                    ctx.stroke();
                }
            }
        }
        
        function drawGrid() {
            ctx.strokeStyle = 'rgba(255,255,255,0.05)';
            ctx.lineWidth = 1;
            
            const gridSize = 0.01 * viewScale;
            
            for (let x = 0; x < canvas.width; x += gridSize) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, canvas.height);
                ctx.stroke();
            }
            
            for (let y = 0; y < canvas.height; y += gridSize) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(canvas.width, y);
                ctx.stroke();
            }
        }
        
        function drawArrow(from, to, color) {
            const angle = Math.atan2(to.y - from.y, to.x - from.x);
            const headLen = 10;
            
            ctx.beginPath();
            ctx.moveTo(to.x, to.y);
            ctx.lineTo(
                to.x - headLen * Math.cos(angle - Math.PI / 6),
                to.y - headLen * Math.sin(angle - Math.PI / 6)
            );
            ctx.moveTo(to.x, to.y);
            ctx.lineTo(
                to.x - headLen * Math.cos(angle + Math.PI / 6),
                to.y - headLen * Math.sin(angle + Math.PI / 6)
            );
            ctx.strokeStyle = color;
            ctx.lineWidth = 2;
            ctx.stroke();
        }
    </script>
</body>
</html>
'''
    
    # Replace placeholder with actual data
    html_content = html_content.replace('__DATA_JSON_PLACEHOLDER__', data_json)
    
    with open('interactive_map.html', 'w') as f:
        f.write(html_content)
    
    print(f"Generated interactive visualization: interactive_map.html")

# --- 7. DETAILED REPORTING ---

def print_pool_details(drivers, passengers, neighborhoods, work_areas):
    """Print details about the generated pool"""
    print("\n" + "=" * 60)
    print(f"{'POOL DETAILS':^60}")
    print("=" * 60)
    
    print(f"\n{'--- CLUSTER CENTERS ---':^60}")
    print("Residential Neighborhoods:")
    for n in neighborhoods:
        print(f"  {n['name']}: ({n['center'][0]:.4f}, {n['center'][1]:.4f})")
    print("\nWork Areas:")
    for w in work_areas:
        print(f"  {w['name']}: ({w['center'][0]:.4f}, {w['center'][1]:.4f})")
    
    print(f"\n{'--- DRIVERS ---':^60}")
    print(f"{'ID':<4} {'Name':<12} {'Vehicle':<10} {'Sched':<6} {'Route':<8}")
    print("-" * 50)
    for d in drivers[:10]:
        route_dist = d.get_route_distance()
        print(f"{d.id:<4} {d.name:<12} {d.vehicle_type:<10} {d.schedule}:00  {route_dist:>5.2f}km")
    if len(drivers) > 10:
        print(f"... and {len(drivers) - 10} more drivers")
    
    print(f"\n{'--- PASSENGERS ---':^60}")
    print(f"{'ID':<4} {'Name':<12} {'Sched':<6} {'Trip':<8}")
    print("-" * 40)
    for p in passengers[:10]:
        trip_dist = p.get_trip_distance()
        print(f"{p.id:<4} {p.name:<12} {p.schedule}:00  {trip_dist:>5.2f}km")
    if len(passengers) > 10:
        print(f"... and {len(passengers) - 10} more passengers")

def print_matching_results(drivers, passengers, match_details):
    """Print detailed matching results"""
    print("\n" + "=" * 60)
    print(f"{'MATCHING RESULTS':^60}")
    print("=" * 60)
    
    matched_passengers = [p for p in passengers if p.matched_driver is not None]
    unmatched_passengers = [p for p in passengers if p.matched_driver is None]
    
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
    
    total_capacity = len(drivers) * MAX_CAPACITY
    used_capacity = len(matched_passengers)
    fleet_occupancy = used_capacity / total_capacity * 100 if total_capacity > 0 else 0
    
    print(f"\n{'--- CAPACITY UTILIZATION ---':^60}")
    print(f"Total Fleet Capacity:     {total_capacity} seats")
    print(f"Used Capacity:            {used_capacity} seats")
    print(f"Fleet Occupancy:          {fleet_occupancy:.1f}%")

# --- 8. MAIN EXECUTION ---

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print(f"{'CARPOOLING SIMULATION':^60}")
    print(f"{'Optimized Matching Algorithm':^60}")
    print("=" * 60)
    print(f"Run Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # A. Generate Random Pool
    drivers, passengers, neighborhoods, work_areas = generate_random_pool()
    
    # B. Print Pool Details
    print_pool_details(drivers, passengers, neighborhoods, work_areas)
    
    # C. Run Algorithm
    print("\n" + "=" * 60)
    print(f"{'RUNNING MATCHING ALGORITHM':^60}")
    print("=" * 60)
    match_details = match_algorithm(drivers, passengers)
    
    # D. Print Results
    print_matching_results(drivers, passengers, match_details)
    
    # E. Export data for interactive visualization
    print("\n" + "=" * 60)
    print(f"{'GENERATING INTERACTIVE VISUALIZATION':^60}")
    print("=" * 60)
    viz_data = export_visualization_data(drivers, passengers, neighborhoods, work_areas, match_details)
    generate_interactive_html(viz_data)
    
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
    print(f"\n  Output files:")
    print(f"    - simulation_data.json (data)")
    print(f"    - interactive_map.html (visualization)")
    print(f"\n  Open interactive_map.html in a browser to explore!")
    print("=" * 60 + "\n")
    
    # Try to open in browser
    try:
        html_path = os.path.abspath('interactive_map.html')
        print(f"Opening visualization in browser...")
        webbrowser.open(f'file://{html_path}')
    except:
        print("Could not auto-open browser. Please open interactive_map.html manually.")
