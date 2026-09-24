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
        "correct_total_volume_260": False # 50 (B101) + 200 (B106) + 10 (B107) = 260
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
            
            if "260" in combined_content:
                state["correct_total_volume_260"] = True

            # Ruined batches: B103 (18%), B105 (16%), B108 (20%)
            if "B103" in combined_content: state["found_B103"] = True
            if "B105" in combined_content: state["found_B105"] = True
            if "B108" in combined_content: state["found_B108"] = True

            # False positives: B101, B106, B107 (Good Cherry), B102, B104, B109 (Other Wood)
            false_ids = ["B101", "B102", "B104", "B106", "B107", "B109"]
            for fid in false_ids:
                if fid in combined_content:
                    state["no_false_positives"] = False

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
