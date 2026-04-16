import os
import json
import subprocess
import shutil

def run_cmd(cmd, cwd=None):
    subprocess.run(cmd, shell=True, check=True, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def build_env():
    base_dir = os.path.abspath("assets/data_400/hike_project")
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir)

    # 1. Initialize Git Repo
    run_cmd("git init", cwd=base_dir)
    run_cmd("git config user.name 'Grumpy Hiker'", cwd=base_dir)
    run_cmd("git config user.email 'grumpy@example.com'", cwd=base_dir)

    # 2. Create trails.json
    trails_data = [
        {"name": "Pine Ridge", "base_risk": 15},
        {"name": "Bear Creek", "base_risk": 22},
        {"name": "Devil's Backbone", "base_risk": 35},
        {"name": "Sunny Meadow", "base_risk": 5},
        {"name": "Deadman's Pass", "base_risk": 40}
    ]
    with open(os.path.join(base_dir, "trails.json"), "w") as f:
        json.dump(trails_data, f, indent=4)

    # 3. Create mock weather script
    weather_script = """#!/usr/bin/env python3
import argparse
import sys
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', required=True)
    parser.add_argument('--location', required=True)
    args = parser.parse_args()

    if args.token != "hk_992_alpha_tango":
        print(json.dumps({"error": "Invalid token"}), file=sys.stderr)
        sys.exit(1)
    
    if args.location == "Mount_Baldy":
        print(json.dumps({"location": "Mount_Baldy", "multiplier": 1.8}))
    else:
        print(json.dumps({"location": args.location, "multiplier": 1.0}))

if __name__ == "__main__":
    main()
"""
    script_path = os.path.join(base_dir, "get_weather.py")
    with open(script_path, "w") as f:
        f.write(weather_script)
    os.chmod(script_path, 0o755)

    # Commit 1: Initial commit
    run_cmd("git add trails.json get_weather.py", cwd=base_dir)
    run_cmd("git commit -m 'Initial commit of trail data and weather script'", cwd=base_dir)

    # 4. Create the file with the token
    token_file_path = os.path.join(base_dir, "api_keys.txt")
    with open(token_file_path, "w") as f:
        f.write("WEATHER_API_TOKEN=hk_992_alpha_tango\n")
    
    # Commit 2: Accidentally commit token
    run_cmd("git add api_keys.txt", cwd=base_dir)
    run_cmd("git commit -m 'Adding api keys for local testing'", cwd=base_dir)

    # Commit 3: Delete the token file
    run_cmd("git rm api_keys.txt", cwd=base_dir)
    run_cmd("git commit -m 'Oops, removed hardcoded api keys. Will use env vars.'", cwd=base_dir)

    # Commit 4: Unrelated change
    with open(os.path.join(base_dir, "README.md"), "w") as f:
        f.write("# Hike Patrol System\nStill a work in progress.\n")
    run_cmd("git add README.md", cwd=base_dir)
    run_cmd("git commit -m 'Add readme'", cwd=base_dir)

if __name__ == "__main__":
    build_env()
