import os
import json

def build_env():
    # Setup directories
    os.makedirs("records/spectra", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # Create the "Hard-to-read" compliance policy (Mocking a PDF content as text for the task logic)
    # In a real scenario, this could be a real PDF, but here we place a file that requires a 'Parser'
    policy_content = """
    OFFICIAL COMPLIANCE POLICY - FLORIDA CITRUS ECO-ALLIANCE
    Approved Organic Active Ingredients:
    - Seaweed Extract (Kelp)
    - Bone Meal (Calcium Phosphate)
    - Alfalfa Protein
    - Fish Hydrolysate
    - Compost-derived microorganisms
    
    Strictly Prohibited: Any synthetic nitrogen sources (Ammonium Nitrate, Urea), Synthetic Phosphorus, or Glyphosate-based carriers.
    """
    with open("compliance_policy.pdf", "w") as f:
        f.write(policy_content)
        
    # Log data with "Obstacles"
    # Grove_North: Pass
    # Grove_South: Fail (pH 5.8)
    # Grove_East: Fail (Unapproved Chemical: 'Nitro-Max' contains Ammonium Nitrate)
    # Grove_West: Pass
    # Grove_Central: Fail (pH 5.2 AND Unapproved Chemical: 'Quick-Green' contains Urea)
    
    logs = [
        {"field_id": "Grove_North", "spectrogram_ref": "spectra/sn_001.dat", "fertilizer_brand": "Ocean-Pure Kelp"},
        {"field_id": "Grove_South", "spectrogram_ref": "spectra/sn_002.dat", "fertilizer_brand": "Organic Bone Dust"},
        {"field_id": "Grove_East", "spectrogram_ref": "spectra/sn_003.dat", "fertilizer_brand": "Nitro-Max"},
        {"field_id": "Grove_West", "spectrogram_ref": "spectra/sn_004.dat", "fertilizer_brand": "Alfalfa Gold"},
        {"field_id": "Grove_Central", "spectrogram_ref": "spectra/sn_005.dat", "fertilizer_brand": "Quick-Green"}
    ]
    
    # Mapping for the Skill Mockers to "Read"
    ph_values = {
        "spectra/sn_001.dat": 6.8,
        "spectra/sn_002.dat": 5.8,
        "spectra/sn_003.dat": 6.2,
        "spectra/sn_004.dat": 7.1,
        "spectra/sn_005.dat": 5.2
    }
    
    # Save logs and mock "binary" spectra files
    for i, log in enumerate(logs):
        log_file = os.path.join("records", f"log_2023_{i+1}.json")
        with open(log_file, "w") as f:
            json.dump(log, f, indent=2)
            
        spec_path = os.path.join("records", log["spectrogram_ref"])
        with open(spec_path, "wb") as f:
            # Write some dummy binary data
            f.write(os.urandom(128))
            
    # Create a hidden mapping file for the skills to use (to simulate a backend)
    mapping = {
        "ph_data": ph_values,
        "chemicals": {
            "Ocean-Pure Kelp": "Ingredients: Seaweed Extract. Status: Organic.",
            "Organic Bone Dust": "Ingredients: Bone Meal. Status: Organic.",
            "Nitro-Max": "Ingredients: Synthetic Ammonium Nitrate, Clay. Status: Non-Organic.",
            "Alfalfa Gold": "Ingredients: Alfalfa Protein. Status: Organic.",
            "Quick-Green": "Ingredients: Urea, Synthetic Phosphorus. Status: Non-Organic."
        }
    }
    with open(".hidden_skill_metadata.json", "w") as f:
        json.dump(mapping, f)

if __name__ == "__main__":
    build_env()
