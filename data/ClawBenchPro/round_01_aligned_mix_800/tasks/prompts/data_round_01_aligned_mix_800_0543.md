Greetings. I am currently between appointments—having recently concluded a rather exhausting tenure analyzing biometric variables for a medical-surgical hospital—and I find myself optimizing my personal time with some topological analysis. Frankly, solving mathematical constraints is far more relaxing than dealing with hospital administration.

I am volunteering to organize a restorative hike for a group of recovering outpatients. Unfortunately, the local forestry department recently migrated their systems, turning the telemetry database into a fractured mess. 

Here is what you must navigate to assist me:
The medical clearance constraints for this patient group are no longer static; I have documented the precise cardiovascular boundary limits in `hospital_records/clearance_policy.json`. This includes the acceptable range for monotonic positive elevation accumulation (total positive gain, strictly ignoring descents) and the maximum permissible steepness (discrete first derivative of elevation with respect to distance between consecutive waypoints).

Due to recent mudslides, most of the regional trails are closed. The forestry department sent over a messy text dump (`forestry_dept/active_trails_q3.txt`) listing the only trails legally open this quarter. Do not bother analyzing trails that are not explicitly authorized on this list.

The raw telemetry itself is a nightmare. It was dumped into the `telemetry_dumps` directory. Each trail has its own folder, but the waypoints have been shattered into isolated JSON fragments. To make matters worse, the backup process scrambled the file names. If you sort or process the waypoints alphabetically by filename, you will get impossible topological geometries. You must reassemble the chronological trajectory of each trail using the internal `timestamp` embedded within each waypoint file.

Your objective is to isolate the subset of *active* trails that satisfy *both* boundary conditions from the policy. Synthesize your findings into a structured JSON payload named `optimal_routes.json` and place it in a newly created `results` directory. For the trails that pass the constraints, map the trail's base identifier (e.g., `trail_042`) to a nested object containing its `total_gain` and `max_steepness`. Please round these metrics to two decimal places.

Time is of the essence. Sift through the noise, reassemble the fragments correctly, apply the policy, and execute this flawlessly.
