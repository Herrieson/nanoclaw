import os
import json
import random

def build_env():
    base_dir = "assets/data_494"
    os.makedirs(base_dir, exist_ok=True)
    
    gps_dir = os.path.join(base_dir, "gps_dumps")
    os.makedirs(gps_dir, exist_ok=True)
    
    # County warnings regarding pollution
    warnings_content = """
COUNTY ENVIRONMENTAL BOARD - OFFICIAL NOTICE
Date: October 14th

Attention all Scenic and Sightseeing Transportation operators:
Recent industrial spills and corporate negligence have severely impacted certain areas of our historical trail network. 
Effective immediately, 'Smog Valley' has been deemed hazardous due to airborne toxins from the nearby plastic processing plant. 
Additionally, 'Plasticville' has suffered a major chemical leak affecting the groundwater. 

To protect our delicate ecosystem and the health of your tour groups, all guided tours must completely avoid routing through Smog Valley and Plasticville until further notice.

Please respect our environment.
    """
    with open(os.path.join(base_dir, "county_warnings.txt"), "w") as f:
        f.write(warnings_content.strip())
        
    # Trail network definition
    # Shortest path A -> G is A->C->G (3+4=7), but C is polluted.
    # Second shortest is A->E->G (2+6=8), but E is polluted.
    # Valid shortest path: A->B->D->F->G (5+2+4+3=14)
    edges = [
        ("Ohio Pioneer Monument", "Smog Valley", 3),
        ("Smog Valley", "Green River Delta", 4),
        ("Ohio Pioneer Monument", "Plasticville", 2),
        ("Plasticville", "Green River Delta", 6),
        ("Ohio Pioneer Monument", "Whispering Pines", 5),
        ("Whispering Pines", "Old Settler's Cabin", 2),
        ("Old Settler's Cabin", "Eagle Peak", 4),
        ("Eagle Peak", "Green River Delta", 3),
        # Distractions and dead ends
        ("Whispering Pines", "Smog Valley", 1),
        ("Eagle Peak", "Plasticville", 1),
        ("Old Settler's Cabin", "Lost Miner Cave", 8),
        ("Lost Miner Cave", "Green River Delta", 10),
        ("Ohio Pioneer Monument", "Muddy Creek", 7),
        ("Muddy Creek", "Lost Miner Cave", 3)
    ]
    
    # Shuffle and write into fragmented files to simulate the intern's "digitization"
    random.seed(42)
    random.shuffle(edges)
    
    for i, (src, dst, dist) in enumerate(edges):
        frag_content = f"[SEGMENT LOG]\nDate: Auto-generated\nFrom: {src}\nTo: {dst}\nDist: {dist}\nStatus: OK\n"
        # Bidirectional graph, let's randomly flip some directions in the text 
        # to test if the agent treats it as an undirected graph.
        if random.choice([True, False]):
            frag_content = f"[SEGMENT LOG]\nDate: Auto-generated\nFrom: {dst}\nTo: {src}\nDist: {dist}\nStatus: OK\n"
            
        with open(os.path.join(gps_dir, f"route_frag_{i}.dat"), "w") as f:
            f.write(frag_content)

if __name__ == "__main__":
    build_env()
