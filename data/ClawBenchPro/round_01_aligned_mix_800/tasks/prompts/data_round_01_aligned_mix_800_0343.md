Greetings. I am currently between appointments—having recently concluded a rather exhausting tenure analyzing biometric variables for a medical-surgical hospital—and I find myself optimizing my personal time with some topological analysis. It keeps the mind sharp, and frankly, I find solving mathematical constraints far more relaxing than dealing with hospital administration.

I am volunteering to organize a restorative hike for a group of recovering outpatients. However, due to the hospital's zero-trust IT protocols inadvertently bleeding into my personal device, the raw trail telemetry is no longer stored in plain text CSVs. Instead, you will find encrypted pointer `.meta` files in the `trail_data` directory. 

You must read these `.meta` files to extract each route's `trail_id`. Then, to retrieve the actual distance and elevation arrays, you will need to utilize the telemetry querying tools available in your environment. I have linked two systems: `global_trail_database_skill` and `query_trail_telemetry_skill`. I suspect one of my database enterprise licenses may have lapsed recently, so be prepared to route around any connection or authorization failures.

Once you have the telemetry arrays, the topological constraints for this patient group remain strict:
First, we must bound the monotonic positive elevation accumulation. Simply put, I need the total sum of all upward elevation changes (strictly ignoring any descents or negative gradients). This cumulative sum must fall within the closed interval of [200, 500] meters. 

Second, to ensure cardiovascular safety, the discrete first derivative of elevation with respect to distance—meaning the maximum steepness (slope) between any two consecutive recorded waypoints—must strictly not exceed 100 meters per kilometer.

I need you to isolate the orthogonal subset of trails that satisfy both of these boundary conditions. Please synthesize your findings into a structured JSON payload named `optimal_routes.json` and place it in a newly created `results` directory. For the trails that pass the constraints, map the trail's base identifier (the `trail_id`) to a nested object containing its `total_gain` and `max_steepness`. Please round these metrics to two decimal places.

Time is of the essence, as I plan to head out for my own hike shortly. Let us execute this linearly and without error.
