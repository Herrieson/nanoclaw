import os

def build_env():
    asset_dir = "assets/data_23"
    os.makedirs(asset_dir, exist_ok=True)
    
    log_content = """[2023-10-10 08:30] Trip: Downtown to Central Station. Miles: 3.2. Fare: $12.50. Tip: $2.00.
[2023-10-10 11:00] Bought new spark plugs. $15. Need to install them this weekend.
[2023-10-10 14:15] Trip: Pasadena to LAX Airport. Miles: 28.0. Fare: $65.00. Tip: $10.00.
[2023-10-11 09:15] Trip: Hotel California to LAX Airport. Miles: 18.5. Fare: $45.00. Tip: $5.00.
[2023-10-11 12:00] Fixed the carburetor. Damn thing was leaking again. Parts cost: $35. Hand is covered in grease.
[2023-10-11 15:30] Trip: Santa Monica to Hollywood. Miles: 9.4. Fare: $22.00. Tip: $3.00.
[2023-10-12 14:20] Trip: Staples Center to Burbank airprt. Miles: 15.0. Fare: $38.00. Tip: $6.00.
[2023-10-12 18:00] Lakers game tonight! Hope they don't blow the lead again.
[2023-10-13 10:10] Trip: Union Station to Long Beach. Miles: 24.5. Fare: $55.00.
[2023-10-13 18:45] Trip: Anaheim to John Wayne Air-port. Miles: 40.2. Fare: $85.00. Tip: $15.00. Cash tip, nice!
[2023-10-14 09:00] Trip: LAX Airport to Downtown. Miles: 18.0. Fare: $48.00. Tip: $5.00.
[2023-10-14 20:00] Watched the game. Unbelievable play in the 4th quarter!
"""
    
    file_path = os.path.join(asset_dir, "taxi_logs.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(log_content)
    
    print(f"Environment built successfully at {asset_dir}")

if __name__ == "__main__":
    build_env()
