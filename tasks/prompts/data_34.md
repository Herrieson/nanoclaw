Listen, I've got this new trail route I'm trying to map out. I'm a map and compass guy, usually out on the trails. I don't care much for these newfangled digital files the park rangers handed me, but rules are rules. I believe in protecting our nature, and they told me there are some protected ecological zones we absolutely cannot enter.

I put everything in my workspace (`/workspace/./`). There's a `visitor_center.txt` with our starting coordinates. I've got a `waypoints.csv` with potential historical stops, a `eco_zones.json` with the bounding boxes of the restricted areas, and a `history_notes.txt` with some facts I scribbled down for each spot. 

Here's what I need you to do:
1. Throw out any waypoint that falls *inside* or *exactly on the edge* of the bounding boxes in `eco_zones.json`.
2. Map out a route for me. Start at the Visitor Center. From there, always go to the absolute closest next valid waypoint, and keep doing that until you've visited them all. You have to use the Haversine formula to calculate the distances (use an Earth radius of exactly `6371.0` km).
3. Write up a final itinerary for me. Save it as `itinerary.md` right in `/workspace/`. 

I'm tapping my foot waiting here, so make sure the format looks exactly like this:
