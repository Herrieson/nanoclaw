import os

def build_env():
    base_dir = "assets/data_424/workspace"
    os.makedirs(base_dir, exist_ok=True)
    
    mixed_content = """
    My notes on the Old Market:
    The Old Market is a neighborhood located in downtown Omaha, Nebraska. It is bordered by South 10th Street.
    
    [DISPATCH LOG] 1998-04-10 | Robbery | 4500 W Dodge Rd
    
    The area retains its brick paved streets from the turn of the century.
    
    [DISPATCH LOG] 1998-04-12 | Vandalism | 10th and Jackson St, Old Market
    
    Many of the buildings were built in the 1880s.
    
    [DISPATCH LOG] 1998-04-15 | Public Intoxication | 1100 Howard St (Old Market)
    
    I need to visit the Durham Museum this weekend with the kids.
    
    [DISPATCH LOG] 1998-04-18 | Traffic Collision | 72nd and Pacific
    
    [DISPATCH LOG] 1998-04-20 | Burglary | 1200 Harney St, Old Market Area
    
    St. Cecilia Cathedral is quite beautiful.
    """
    
    with open(os.path.join(base_dir, "mixed_records.txt"), "w") as f:
        f.write(mixed_content.strip())

if __name__ == "__main__":
    build_env()
