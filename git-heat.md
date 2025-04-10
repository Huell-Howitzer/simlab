import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from collections import defaultdict

# Configuration
GITLAB_API_URL = "https://gitlab.com/api/v4"
PRIVATE_TOKEN = "your_access_token_here"
PROJECT_ID = "your_project_id_here"
USERS = ["username1", "username2", "username3"]

HEADERS = {"PRIVATE-TOKEN": PRIVATE_TOKEN}

# Date range
end_date = datetime.utcnow()
start_date = end_date - timedelta(days=365)

# Data container
contrib_data = defaultdict(lambda: defaultdict(int))  # {username: {date: count}}

# Fetch commits for each user
for username in USERS:
    page = 1
    while True:
        r = requests.get(
            f"{GITLAB_API_URL}/projects/{PROJECT_ID}/repository/commits",
            headers=HEADERS,
            params={
                "author": username,
                "since": start_date.isoformat(),
                "until": end_date.isoformat(),
                "per_page": 100,
                "page": page
            }
        )
        commits = r.json()
        if not commits:
            break

        for commit in commits:
            date = commit["committed_date"][:10]
            contrib_data[username][date] += 1

        page += 1

# Convert to DataFrame
records = []
for user, days in contrib_data.items():
    for date_str, count in days.items():
        records.append({
            "user": user,
            "date": datetime.strptime(date_str, "%Y-%m-%d"),
            "count": count
        })

df = pd.DataFrame(records)

# Fill in missing dates with 0
all_dates = pd.date_range(start=start_date, end=end_date)
users = list(contrib_data.keys())

heat_df = (
    df.set_index("date")
    .groupby(["user", "date"])["count"]
    .sum()
    .unstack(fill_value=0)
    .reindex(index=users, columns=all_dates, fill_value=0)
)

# Plot heatmap
plt.figure(figsize=(18, len(users) * 0.5 + 2))
sns.heatmap(heat_df, cmap="Greens", linewidths=0.1, linecolor="gray", cbar=True)
plt.title("GitLab Contributions Heatmap")
plt.xlabel("Date")
plt.ylabel("User")
plt.tight_layout()
plt.show()






---

Alright, that’s a great setup to walk through a real-world 6-DOF flight sim scenario and calculate G-forces at each stage. Let’s step through it logically and build the physics as we go. Here’s the breakdown:

⸻

Initial Setup

Assumptions:
	•	You’re flying straight and level north, constant speed.
	•	Let’s say:
	•	Altitude = 10,000 ft (~3,048 m)
	•	True Airspeed = 150 m/s
	•	No wind
	•	Aircraft is trimmed, no pitch/roll/yaw motion
	•	Gravity = 9.81 m/s² downward

At this stage:
	•	Linear acceleration = 0 (steady velocity)
	•	Rotational rates (p, q, r) = 0
	•	G-forces:
	•	Only gravity acts
	•	So: Gx = 0, Gy = 0, Gz = 1 (you feel 1G straight down in body frame)

⸻

Start of the U-Turn

Let’s say you bank left to start the turn:

Assumptions:
	•	You roll into a 45° bank
	•	Maintain level altitude
	•	Maintain speed (150 m/s)
	•	Radius of turn depends on speed and bank angle:

R = V² / (g * tan(bank_angle)) = (150²) / (9.81 * tan(45°)) ≈ 2,295 m

Centripetal Acceleration:

This causes lateral G-force (inward) in the body frame.

a_c = V² / R ≈ 150² / 2295 ≈ 9.81 m/s² → exactly 1G

So now the G-force in the aircraft’s frame is:
	•	Gx = 0 (no forward accel)
	•	Gy = 1 (to the right of the aircraft)
	•	Gz = 1 (vertical lift force needed to counter gravity)

But here’s the trick: the pilot feels the total G-load from both lift (upward) and the lateral turn.

So:

G_total = sqrt(Gy² + Gz²) = sqrt(1² + 1²) ≈ 1.41 G

This is the load factor the pilot feels, toward the seat (through the body).

⸻

Mid-Turn
	•	Still 45° bank, constant speed
	•	Still pulling 1.41 G total
	•	Direction changing smoothly
	•	Aircraft is yawed into the turn (coordinated), so no side-slip

⸻

End of Turn (Back South)

You roll out:
	•	Bank angle returns to 0°
	•	Accelerations drop back to 0
	•	Gz returns to 1 G (gravity only)
	•	Gx = 0, Gy = 0

⸻

Summary of G-Force Profile Over Time
	1.	Straight flight:
	•	Gx = 0, Gy = 0, Gz = 1
	2.	Rolling into turn:
	•	Small G increase from the roll input
	3.	In turn (45° bank):
	•	Gx = 0, Gy = 1, Gz = 1 → Total = 1.41 G
	4.	Rolling out:
	•	Small G changes again
	5.	Straight again:
	•	Back to 1 G

⸻

Want to continue by adding vertical maneuvers (like pitching up during the turn), or maybe visualize the G-loads over time?


---

Nice — let’s push it into the red and see what happens to those G-loads.

⸻

Objective

We’ll keep adjusting the bank angle (and optionally speed) until the total G-load exceeds human tolerance, say:
	•	Sustained G-limit for trained pilots: ~9 G
	•	Untrained person: blackouts start at ~5-6 G

We’ll keep speed at 150 m/s for now and increase bank angle.

⸻

Total G-Load in Level Banked Turn

For level flight (constant altitude), the load factor (Gz) is:

Gz = 1 / cos(bank_angle)

Because lift must increase to balance gravity when banked.

Let’s see the load factor at different bank angles:

Bank Angle	Gz (Load Factor)	Tolerable?
0°	1.00	Easy
30°	1.15	Comfortable
45°	1.41	Normal turn
60°	2.00	Feels heavy
70°	2.92	Red zone starts
80°	5.76	Blackout likely
85°	11.47	Unconscious
89°	57.29	Structural fail



⸻

So even at 80°, you’re already past the point where most people would stay conscious without G-suits or reclined seats.

⸻

Want More Gs Without Steeper Bank? Increase Speed

If we don’t increase bank but instead crank the speed while holding the same turn radius (e.g., sharp turn at low altitude), centripetal acceleration (a_c = V² / R) climbs fast.

Let’s say:
	•	Radius = 2295 m (from earlier)
	•	Try 250 m/s instead of 150:

a_c = 250² / 2295 ≈ 27.22 m/s²
G = 27.22 / 9.81 ≈ 2.77 G lateral

Combine with vertical G (1 G), total:

G_total = sqrt(1² + 2.77²) ≈ 2.95 G

Still okay, but try 400 m/s:

a_c = 400² / 2295 ≈ 69.74 m/s² → 7.11 G lateral
G_total = sqrt(1² + 7.11²) ≈ 7.18 G

Now you’re solidly into military pilot-only territory, and most people would be out cold.

⸻

So: How Do We Push Over the Limit?
	•	Bank angle over ~80°
	•	High speed turns (especially at low altitude)
	•	Pulling up rapidly (like in a loop or high-G pitch-up)

⸻

Want to simulate a loop or high-G pull-up next? That’s where vertical Gs get wild.




---


Oh yes — now we’re talking high-speed, high-G maneuvering. Let’s crunch the numbers.

⸻

Scenario Setup

You’re flying at Mach 1.4 at sea level (for worst-case G-loads).
	•	Mach 1.4 at sea level ≈ 477 m/s (depends on air temp/density)
	•	You want to do a 180° turn (a U-turn)
	•	Question: What’s the minimum turn radius that keeps G-forces below human tolerance?

Let’s assume a sustained 9 G limit — pretty much the max trained fighter pilots can endure with a G-suit.

⸻

Centripetal Acceleration Equation

To maintain a level coordinated turn:

a_c = v² / R  
G = a_c / g  
→ R = v² / (G_limit * g)

Plug in:
	•	v = 477 m/s
	•	G_limit = 9
	•	g = 9.81 m/s²

R = (477²) / (9 * 9.81)  
  ≈ 227529 / 88.29  
  ≈ 2577 meters



⸻

Answer:

You need at least a ~2.58 km turn radius to stay at or below 9 Gs during a 180° turn at Mach 1.4 at sea level.

⸻

What Happens If It’s Tighter?

If you cut that radius to, say, 1 km, let’s calculate the Gs:

a_c = v² / R = 477² / 1000 ≈ 227.5 m/s²  
G = 227.5 / 9.81 ≈ 23.2 G

Yeah… you’re paste at that point. Not survivable for humans or aircraft.

⸻

Want to play with altitude effects (e.g., Mach 1.4 at 30,000 ft)? Speed of sound drops, so true airspeed is lower, and Gs change. Want to go there next?



---

Great question — this gets to the heart of aerodynamic energy management. Here’s why a sharp turn scrubs speed:

⸻

1. Increased Drag in a Turn

When you bank and turn, you need to generate more lift to counteract gravity — because only a component of lift is now vertical. The total lift increases by the load factor (which is also the G-force):

Lift_required = Weight * Load Factor = mg * (1 / cos(bank_angle))

More lift = more induced drag, because:

Induced drag ∝ Lift²

So turning increases drag a lot, and that drag slows you down unless you’re adding thrust to compensate.

⸻

2. Energy Trade-Off (Kinetic to Heat)
	•	In a tight turn, you’re applying force (lift) sideways to curve your path.
	•	That force isn’t doing work in the forward direction — it’s not helping maintain speed.
	•	But drag is doing negative work — it’s bleeding energy.

So, unless you increase throttle, you’ll lose kinetic energy (i.e., speed).

⸻

3. G-Forces Amplify It

In a 6 G turn, you’re generating 6x the lift, and the induced drag skyrockets. That drag eats into your speed like crazy.

For example:
	•	In a 60° bank (2 Gs), drag might double or triple compared to straight-and-level flight.
	•	In a 9 G turn? Drag is massive. You must apply afterburner or you’ll bleed speed fast.

⸻

4. Real-World Effect

Fighter jets doing hard turns often lose hundreds of knots in seconds unless they light the burners. That’s why turn rate vs. energy management is a key tradeoff in dogfights.

⸻

In short:
Sharp turns scrub speed because generating high lift to turn creates high drag, and that drag sucks away kinetic energy unless you power through it.

Want to go deeper and plot how quickly speed drops in a sustained turn?


---

Perfect — TSPI (Time-Space Position Information) data is exactly what we need to compute G-forces over time.

Let’s walk through how to calculate G-forces from TSPI step-by-step.

⸻

Assumptions

Your TSPI data likely includes, per timestamp:
	•	Position: x, y, z (in meters, in some global/inertial frame)
	•	Possibly orientation: roll, pitch, yaw or quaternion
	•	Timestamp: t

Let me know if you also have velocity or acceleration already — but I’ll assume we only have position and time for now.

⸻

Steps to Calculate G-Forces

1. Compute Velocity

Using finite differences:

v = (pos[i+1] - pos[i]) / dt

2. Compute Acceleration

Same way:

a = (v[i+1] - v[i]) / dt

Now you have acceleration in the global frame.

3. Subtract Gravity

Convert acceleration to net (specific) acceleration by subtracting gravitational acceleration vector:

a_specific = a - g

Where g = [0, 0, -9.81] (if z is up).

4. Rotate to Body Frame

If you have orientation data, you can convert the global acceleration to the body frame using the rotation matrix derived from roll/pitch/yaw or quaternions.

a_body = R_world_to_body * a_specific

If you don’t have orientation data, we can estimate an approximate “pseudo-body frame” using velocity vectors.

5. Normalize to G Units

Divide by gravitational acceleration:

Gx = a_body_x / 9.81
Gy = a_body_y / 9.81
Gz = a_body_z / 9.81



⸻

6. (Optional) Compute Total G-Force

G_total = sqrt(Gx² + Gy² + Gz²)



⸻

Want to Start Now?

If you upload your TSPI dataset (CSV, JSON, etc.), I can:
	•	Parse it
	•	Calculate G-forces at each point
	•	Plot the G-loads over time
	•	Export it back to you with Gs included

Want to go ahead and upload the file?

---

Here’s the simulated TSPI dataset with calculated G-forces. It includes position, velocity, acceleration, specific acceleration (with gravity removed), and the resulting G-loads (Gx, Gy, Gz, and total G-force G_total) over time.

If you’d like, I can:
	•	Plot the G-loads over time
	•	Highlight sections where G-forces exceed safe limits
	•	Export this to a CSV for download

What would you like next? ￼