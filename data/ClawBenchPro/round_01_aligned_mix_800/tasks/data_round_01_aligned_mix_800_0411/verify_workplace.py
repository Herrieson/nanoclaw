import os
import sys
import json
import csv
import xml.etree.ElementTree as ET
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def get_ground_truth(workspace):
    raw_dir = os.path.join(workspace, "raw_dump")
    
    # 1. Parse manual for energy map
    energy_map = {}
    with open(os.path.join(raw_dir, "manuals", "energy_map.json"), "r") as f:
        energy_map = json.load(f)
        
    # 2. Parse catalog for prices
    catalog_prices = {}
    with open(os.path.join(raw_dir, "catalog", "parts_index.csv"), "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            catalog_prices[row["part_no"]] = float(row["unit_price"])
            
    expected_tracks = set()
    corrupted_tracks = set() # To check if agent mistakenly included them
    
    # Calculate Playlist
    for root, dirs, files in os.walk(os.path.join(raw_dir, "devices")):
        is_corrupted_dir = "corrupted" in root or "recycle_bin" in root
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".json"):
                with open(file_path, "r") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "tracks" in data: # phone
                        for t in data["tracks"]:
                            if t["bpm"] > 120:
                                if is_corrupted_dir:
                                    corrupted_tracks.add(t["title"])
                                else:
                                    expected_tracks.add(t["title"])
                    elif isinstance(data, list): # corrupted
                        for t in data:
                            if t.get("bpm", 0) > 120:
                                corrupted_tracks.add(t.get("title", ""))
            elif file.endswith(".csv"):
                with open(file_path, "r") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        bpm = energy_map.get(row["EnergyCode"], 0)
                        if bpm > 120:
                            if is_corrupted_dir:
                                corrupted_tracks.add(row["Title"])
                            else:
                                expected_tracks.add(row["Title"])
            elif file.endswith(".xml"):
                tree = ET.parse(file_path)
                xml_root = tree.getroot()
                for track in xml_root.findall("track"):
                    title = track.find("title").text
                    bpm = int(track.find("bpm").text)
                    if bpm > 120:
                        if is_corrupted_dir:
                            corrupted_tracks.add(title)
                        else:
                            expected_tracks.add(title)
                            
    # Calculate Costs
    total_cost = 0.0
    for root, dirs, files in os.walk(os.path.join(raw_dir, "invoices")):
        is_corrupted_dir = "corrupted" in root or "recycle_bin" in root
        if is_corrupted_dir:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".txt"): # North
                with open(file_path, "r") as f:
                    lines = f.read().splitlines()
                is_valid = False
                for line in lines:
                    if line.startswith("STATUS:"):
                        status = line.split(":", 1)[1].strip()
                        if status in ["PAID", "COMPLETED"]:
                            is_valid = True
                        break
                if is_valid:
                    for line in lines:
                        if line.startswith("Item:") and "GLS-WND-" in line:
                            # Extract Qty and Price
                            # Example: Item: GLS-WND-001 (Windshield) - Qty: 2 - Unit Price: $200.00
                            parts = line.split("-")
                            qty_str = [p for p in parts if "Qty:" in p][0]
                            price_str = [p for p in parts if "Unit Price:" in p][0]
                            qty = int(qty_str.split(":")[1].strip())
                            price = float(price_str.split("$")[1].strip())
                            total_cost += qty * price
            elif file.endswith(".json"): # South
                with open(file_path, "r") as f:
                    data = json.load(f)
                if data.get("status") in ["PAID", "COMPLETED"]:
                    for item in data.get("items", []):
                        if item["part_no"].startswith("GLS-WND-"):
                            qty = item["qty"]
                            price = catalog_prices.get(item["part_no"], 0.0)
                            total_cost += qty * price
                            
    return expected_tracks, corrupted_tracks, round(total_cost, 2)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results_dir = os.path.join(workspace, "results")
    
    expected_tracks, corrupted_tracks, expected_cost = get_ground_truth(workspace)
    
    score_details = []
    total_score = 0
    
    # 1. Directory Structure (10 points)
    if os.path.isdir(results_dir):
        score_details.append({"item": "Results directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found 'results' folder."})
        total_score += 10
    else:
        score_details.append({"item": "Results directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Missing 'results' folder."})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f)
        return

    # 2. Workout Playlist File (Total 40 points)
    playlist_file = os.path.join(results_dir, "workout_playlist.txt")
    if os.path.isfile(playlist_file):
        with open(playlist_file, "r") as f:
            agent_tracks = set([line.strip() for line in f.read().splitlines() if line.strip()])
        
        # Check Decoy (15 points)
        intersection_with_corrupted = agent_tracks.intersection(corrupted_tracks)
        if intersection_with_corrupted:
            score_details.append({"item": "Ignore corrupted/recycle_bin tracks", "score": 0, "max_score": 15, "passed": False, "reason": "Included tracks from blacklisted directories."})
        else:
            score_details.append({"item": "Ignore corrupted/recycle_bin tracks", "score": 15, "max_score": 15, "passed": True, "reason": "Successfully filtered out bad directories."})
            total_score += 15
            
        # Accuracy of Tracks (25 points)
        missing = expected_tracks - agent_tracks
        extra = agent_tracks - expected_tracks
        if len(missing) == 0 and len(extra) == 0:
            score_details.append({"item": "Playlist Accuracy", "score": 25, "max_score": 25, "passed": True, "reason": "All energetic tracks identified correctly."})
            total_score += 25
        else:
            partial_score = max(0, 25 - len(missing) * 2 - len(extra) * 2)
            score_details.append({"item": "Playlist Accuracy", "score": partial_score, "max_score": 25, "passed": partial_score > 0, "reason": f"Missing {len(missing)}, Extra {len(extra)} tracks."})
            total_score += partial_score
    else:
        score_details.append({"item": "Playlist File exists", "score": 0, "max_score": 40, "passed": False, "reason": "workout_playlist.txt is missing."})
        
    # 3. Windshield Costs File (Total 50 points)
    cost_file = os.path.join(results_dir, "windshield_costs.txt")
    if os.path.isfile(cost_file):
        with open(cost_file, "r") as f:
            cost_content = f.read().strip()
            
        # LLM check for unnecessary presentation (10 points)
        prompt = "Does this text strictly contain ONLY a number (possibly with a dollar sign or decimals) and NOTHING else? (No sentences, no explanations, no 'Total cost is' etc.)"
        is_clean = llm_judge_content(prompt, cost_content)
        if is_clean:
            score_details.append({"item": "No presentation formatting", "score": 10, "max_score": 10, "passed": True, "reason": "File contains only the numerical answer."})
            total_score += 10
        else:
            score_details.append({"item": "No presentation formatting", "score": 0, "max_score": 10, "passed": False, "reason": "File contains extra conversational text or presentation."})
            
        # Value correctness (40 points)
        import re
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", cost_content)
        if numbers:
            agent_cost = float(numbers[-1])
            if abs(agent_cost - expected_cost) < 0.01:
                score_details.append({"item": "Cost Calculation Accuracy", "score": 40, "max_score": 40, "passed": True, "reason": "Calculated the exact correct total cost."})
                total_score += 40
            else:
                score_details.append({"item": "Cost Calculation Accuracy", "score": 0, "max_score": 40, "passed": False, "reason": f"Calculation incorrect. Expected {expected_cost}, got {agent_cost}."})
        else:
            score_details.append({"item": "Cost Calculation Accuracy", "score": 0, "max_score": 40, "passed": False, "reason": "Could not extract a valid number."})
    else:
        score_details.append({"item": "Windshield Costs File exists", "score": 0, "max_score": 50, "passed": False, "reason": "windshield_costs.txt is missing."})

    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=4)

if __name__ == "__main__":
    main()
