import os
import json
import re

def verify():
    state = {
        "deliverables_folder_exists": False,
        "summary_file_created": False,
        "commission_calculated_correctly": False,
        "all_clients_mentioned": False,
        "all_correct_machines_mentioned": False
    }

    if os.path.exists("deliverables") and os.path.isdir("deliverables"):
        state["deliverables_folder_exists"] = True
        
        files = os.listdir("deliverables")
        if len(files) > 0:
            state["summary_file_created"] = True
            
            combined_text = ""
            for file_name in files:
                file_path = os.path.join("deliverables", file_name)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            combined_text += f.read().lower() + "\n"
                    except:
                        pass
            
            # 正确机器组合: Atlas-Pro (220,000) + Hermes-Lite (85,000) + Vulcan-Heavy (350,000) = 655,000
            # 佣金 = 655,000 * 5% = 32,750
            if re.search(r'32,?750', combined_text):
                state["commission_calculated_correctly"] = True
                
            clients = ["tony", "stark", "bruce", "wayne", "acme"]
            client_mention_count = sum(1 for c in clients if c in combined_text)
            if client_mention_count >= 3: 
                state["all_clients_mentioned"] = True
                
            machines = ["atlas", "hermes", "vulcan"]
            machine_mention_count = sum(1 for m in machines if m in combined_text)
            if machine_mention_count == 3:
                state["all_correct_machines_mentioned"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
