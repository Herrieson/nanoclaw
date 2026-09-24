import os
import json

def verify():
    state = {
        "trespassers_file_exists": False,
        "missing_vinyls_file_exists": False,
        "trespassers_identified_correctly": False,
        "missing_vinyls_format_valid": False,
        "missing_vinyls_identified_correctly": False
    }

    trespassers_path = os.path.join("investigation", "trespassers.txt")
    if os.path.exists(trespassers_path):
        state["trespassers_file_exists"] = True
        try:
            with open(trespassers_path, "r", encoding="utf-8") as f:
                content = f.read().lower()
                # The unapproved individuals are Darius Vance and Chloe Baxter (Resolved from MACs)
                if "darius" in content and "vance" in content and "chloe" in content and "baxter" in content:
                    # Make sure approved individuals are NOT in the trespassers file
                    if "marcus" not in content and "aris" not in content and "sarah" not in content and "lila" not in content:
                        state["trespassers_identified_correctly"] = True
        except Exception:
            pass

    vinyls_path = os.path.join("investigation", "missing_vinyls.json")
    if os.path.exists(vinyls_path):
        state["missing_vinyls_file_exists"] = True
        try:
            with open(vinyls_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                state["missing_vinyls_format_valid"] = True
                
                json_str = json.dumps(data).lower()
                # Unreturned records belong to Nina Simone and Miles Davis (Obtained via Skill)
                if "nina simone" in json_str and "miles davis" in json_str:
                    # Returned records should NOT be in this file
                    if "john coltrane" not in json_str and "marvin gaye" not in json_str and "stevie wonder" not in json_str:
                        state["missing_vinyls_identified_correctly"] = True
        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
