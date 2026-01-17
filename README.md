# Optimized Carpooling Matching Algorithm (OCMA)

## 📌 Abstract
This project implements a geospatial matching algorithm designed to optimize the allocation of drivers and passengers in a high-density carpooling network. The system addresses the "First Mile/Last Mile" problem by utilizing a radius-constrained search ($r \le 1km$) to match users with compatible temporal (2-hour commute windows) and spatial (Origin-Destination) constraints. The algorithm aims to maximize vehicle occupancy (capacity $C=4$) while minimizing driver deviation, utilizing a dynamic pricing model to incentivize partial-route sharing.

---

## 📐 Mathematical Formulation

### 1. The Matching Problem
We define the system as a set of Users $U$, partitioned into Drivers $D$ and Passengers $P$.

Each user $u_i$ is defined by a tuple:
$$u_i = \{ (lat_o, lon_o), (lat_d, lon_d), T_{window}, Days \}$$

Where:
* $(lat_o, lon_o)$: Origin coordinates
* $(lat_d, lon_d)$: Destination coordinates
* $T_{window}$: The commute time interval (e.g., 08:00 - 10:00)
* $Days$: Active days of the week (e.g., Mon-Fri)

### 2. Constraints & Feasibility
For a Driver $d \in D$ and a Passenger $p \in P$ to be considered a **candidate match**, the following spatial constraints must be satisfied:

1.  **Origin Proximity:** The passenger's origin must lie within the driver's pickup radius.
    $$Haversine(O_d, O_p) \le \delta$$
    *(Where $\delta = 1km$)*

2.  **Destination Proximity:** The passenger's destination must lie within the driver's drop-off radius.
    $$Haversine(D_d, D_p) \le \delta$$



### 3. Dynamic Pricing Model
The economic model ensures fairness for the driver (who incurs detour costs) while maintaining affordability for the passenger. The cost function $Cost(p)$ is derived from the standard ride-sharing base fare $F_{base}$.

$$Cost(p) = \left( \frac{1}{C_{max}} \cdot F_{base} \right) + \left( F_{base} \cdot \frac{x}{100} \right)$$

Where:
* $C_{max} = 4$ (Maximum vehicle capacity)
* $x$: Variable markup percentage compensating for the driver's specific detour and wait time.

---

## ⚙️ Algorithm Logic

The matching engine operates in three stages to reduce computational complexity from $O(N^2)$ to near-linear time using geospatial indexing.

### Stage 1: Geospatial Filtering (Pruning)
Instead of comparing every driver against every passenger, we utilize **Geohashing** or a **K-D Tree** to index user locations.
* **Query:** Fetch all $p \in P$ where $O_p$ is within the bounding box of $O_d$.
* **Complexity:** $O(log N)$ per query.

### Stage 2: Temporal & Route Validation
For the subset of spatially valid candidates, we verify:
1.  **Schedule Overlap:** $T_{window}(d) \cap T_{window}(p) \neq \emptyset$
2.  **Day Matching:** $Days(d) \cap Days(p) \neq \emptyset$

### Stage 3: Heuristic Scoring & Assignment
We score each valid match $(d, p)$ to prioritize the "best" fit. The score $S$ minimizes the deviation for the driver:

$$S = \alpha \cdot dist(O_d, O_p) + \beta \cdot dist(D_d, D_p)$$

The system creates clusters of 1 Driver + $k$ Passengers (where $k \le 4$) to maximize the total score of the cluster.

---

## 💻 Tech Stack & Implementation Details

* **Core Algorithm:** Python (NumPy for vectorization)
* **Geospatial Library:** GeoPandas / Shapely for coordinate geometry
* **Database:** PostGIS (for spatial indexing)
* **Optimization:** Scikit-learn (for clustering potential matches)

## 🚀 Future Improvements

* **Route Interpolation:** Currently, the system matches based on Origin/Destination points. Future work involves matching passengers *along* the driver's route using Polyline decoding.
* **Machine Learning:** Implementing a regression model to predict the optimal markup percentage $x$ based on current traffic conditions and demand.
