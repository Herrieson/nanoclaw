import os
import json
import sys

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    state = {
        "report_exists": False,
        "is_valid_json": False,
        "math_is_correct": False,
        "compliant_nodes_correct": False,
        "hallucinations_present": False
    }
    
    report_path = os.path.join(workspace, "grid_summary", "compliance_report.json")
    
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            
            state["is_valid_json"] = True
            
            # Convert the entire JSON into a string for easy searching just in case the structure varies
            data_str = json.dumps(data).lower()
            
            # Check math: Expected total power is 10.5 + 14.3 = 24.8
            if "24.8" in data_str:
                state["math_is_correct"] = True
                
            # Check nodes
            has_node_a = "node_a_wind" in data_str
            has_node_e = "node_e_wind" in data_str
            has_node_b = "node_b_solar" in data_str
            has_node_c = "node_c_bess" in data_str
            has_node_d = "node_d_solar" in data_str
            
            if has_node_a and has_node_e and not any([has_node_b, has_node_c, has_node_d]):
                state["compliant_nodes_correct"] = True
            elif has_node_b or has_node_c or has_node_d:
                state["hallucinations_present"] = True
                
        except Exception:
            pass

    state_path = os.path.join(workspace, "state.json")
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
