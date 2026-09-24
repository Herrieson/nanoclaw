import os
import json

def verify():
    state = {
        "resultados_dir_exists": False,
        "output_file_created": False,
        "found_B103": False,
        "found_B105": False,
        "found_B108": False,
        "no_false_positives": True,
        "correct_total_volume_260": False
    }

    if os.path.exists("resultados") and os.path.isdir("resultados"):
        state["resultados_dir_exists"] = True
        files = os.listdir("resultados")
        
        if len(files) > 0:
            state["output_file_created"] = True
            combined_content = ""
            
            for f in files:
                filepath = os.path.join("resultados", f)
                if os.path.isfile(filepath):
                    try:
                        with open(filepath, "r", encoding="utf-8") as file:
                            combined_content += file.read() + " "
                    except Exception:
                        pass
            
            # Check for the correct mathematical sum (260 liters of good Cherry stain)
            if "260" in combined_content:
                state["correct_total_volume_260"] = True

            # Check for the ruined batch IDs
            if "B103" in combined_content:
                state["found_B103"] = True
            if "B105" in combined_content:
                state["found_B105"] = True
            if "B108" in combined_content:
                state["found_B108"] = True

            # Check that they didn't erroneously include good batches or other woods
            false_ids = ["B101", "B102", "B104", "B106", "B107", "B109"]
            for fid in false_ids:
                if fid in combined_content:
                    state["no_false_positives"] = False

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
