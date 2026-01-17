# Algorithmic Implementation: Heuristic Spatial Matching

## 1. Overview
The core of the system is the `BatchMatch` function. To ensure scalability, we avoid a brute-force $O(N^2)$ comparison of all drivers against all passengers. Instead, we utilize a **Spatial Index (R-Tree or K-D Tree)** to perform radius queries in logarithmic time.

## 2. Pseudo-Code

```python
FUNCTION BatchMatch(Drivers, Passengers):
    """
    Input: 
      Drivers: List of Driver objects (capacity, origin, dest, schedule)
      Passengers: List of Passenger objects (origin, dest, schedule)
    Output: 
      Matches: List of tuples (Driver, [Passenger_1, ... Passenger_k])
    """
    
    # 1. Initialization
    Matches = []
    Unmatched_Passengers = Queue(Passengers)
    
    # 2. Spatial Indexing
    # Construct a K-D Tree for efficient nearest neighbor search
    # Complexity: O(P log P) where P is number of passengers
    Passenger_Spatial_Index = BuildKDTree(Passengers.Origin_Coordinates)

    # 3. Matching Loop
    FOR each driver IN Drivers:
        
        # Stop if driver is full
        IF driver.current_occupancy >= 4:
            CONTINUE

        # A. Radius Search (Pruning Phase)
        # Find passengers whose Origin is within 1km of Driver Origin
        # Complexity: O(log P)
        Nearby_Origins = Passenger_Spatial_Index.Query(
            center = driver.origin, 
            radius = 1.0 km
        )

        # B. Candidate Validation (Filtering Phase)
        Candidates = []
        FOR passenger IN Nearby_Origins:
            
            # Check Destination Proximity (User Requirement #5)
            # Distance check using Haversine formula
            IF Distance(driver.dest, passenger.dest) > 1.0 km:
                CONTINUE

            # Check Schedule Compatibility (User Requirement #1)
            # Intersection of time windows must be sufficient for the trip
            IF NOT TimeOverlap(driver.window, passenger.window):
                CONTINUE
            
            # Check Days of Week
            IF NOT CommonDays(driver.days, passenger.days):
                CONTINUE

            Candidates.append(passenger)

        # C. Heuristic Scoring (Optimization Phase)
        # We score candidates to prioritize those who minimize driver detour
        # Score = (1 / Origin_Dist) + (1 / Dest_Dist) + (Pricing_Incentive)
        Scored_Candidates = CalculateScores(driver, Candidates)
        
        # Sort by Score Descending
        Sort(Scored_Candidates)

        # D. Assignment
        # Select up to remaining capacity (Max 4)
        Slots_Available = 4 - driver.current_occupancy
        Selected = Scored_Candidates[0 : Slots_Available]
        
        Matches.append(driver, Selected)
        
        # Remove selected from the global pool to prevent double-booking
        Passenger_Spatial_Index.Remove(Selected)

    RETURN Matches
