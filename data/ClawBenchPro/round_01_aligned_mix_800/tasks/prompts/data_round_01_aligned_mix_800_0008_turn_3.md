Last hurdle before we hit the road! It’s time to pack 'em into the buses. The fleet details are in `logistics/buses.json`. 

We have to fit all the attending kids, the cleared chaperones, AND myself (your lovely lead teacher) onto these buses. Here is the catch: look at `students/behavior.csv`. Anyone marked 'Code Red' is a walking disaster area. Under no circumstances can two 'Code Red' students be on the same bus. If we don't separate these hooligans, it'll be like herding cats in a thunderstorm.

Furthermore, every single bus we use MUST have at least one adult on it (that means a cleared chaperone, or me). And don't forget my accessibility needs and the kids' needs—anyone who requires a wheelchair MUST be assigned to a bus that actually has a wheelchair lift. 

Figure out this logistical puzzle and output the final seating chart as `planning/bus_assignments.json`. The JSON should be keyed by bus ID, with a list of the names of everyone (students and adults) riding that bus. Use as few buses as possible to get the job done, but don't break any of my rules!
