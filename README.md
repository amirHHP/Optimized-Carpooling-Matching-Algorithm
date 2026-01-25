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

## 4. Future Work: Dynamic Pricing Optimization (Machine Learning)

### 4.1. Research Problem
The current implementation utilizes a static markup parameter ($x\%$) to compensate drivers for detours. However, this static value creates market inefficiencies:
* **If $x$ is too low:** Drivers reject matches due to insufficient compensation for traffic/fuel.
* **If $x$ is too high:** Passengers reject the ride, preferring alternative transport.

The research objective is to replace the static $x$ with a dynamic variable $x_{opt}$ predicted by a Machine Learning model that maximizes the **Global Match Conversion Rate**.

### 4.2. Proposed Methodology: Logistic Regression for Elasticity
We propose a supervised learning approach to model the **Probability of Acceptance** ($P_{accept}$) based on the offered price markup.

#### A. Feature Engineering ($X$)
The model inputs (feature vector) will describe the context of the specific ride request:
1.  **Detour Magnitude:** $\Delta d = dist(Driver_{route}) - dist(Shared_{route})$
2.  **Traffic Factor:** Real-time congestion index on the detour segments.
3.  **Supply/Demand Ratio:** Number of available drivers vs. active requests in the $1km$ radius.
4.  **Temporal context:** Time of day (Rush hour vs. off-peak).

#### B. The Prediction Model
We define the probability of a user accepting a ride with markup $x$ using a logistic function:

$$P(match \mid x, \mathbf{f}) = \frac{1}{1 + e^{-(\beta_0 + \beta_1 x + \mathbf{w}^T \mathbf{f})}}$$

Where:
* $x$: The proposed markup percentage.
* $\mathbf{f}$: The feature vector (traffic, detour, etc.).
* $\mathbf{w}$: Learned weights representing user sensitivity to different factors.



#### C. Optimization Function
Once the model is trained, for every new match candidate, we numerically solve for the specific $x$ that maximizes the **Expected Value** of the match:

$$x_{opt} = \arg\max_{x} \left[ P(match \mid x, \mathbf{f}) \times \text{DriverUtility}(x) \right]$$

### 4.3. Reinforcement Learning Extension
For a more advanced implementation, this system could be modeled as a **Contextual Multi-Armed Bandit** problem, where the "arms" are different price points, and the "reward" is the successful formation of a carpool group. This allows the system to learn online and adapt to changing user behaviors over time without a static training dataset.

![image](./Screenshot%202026-01-25%20at%205.18.49 PM.png)
