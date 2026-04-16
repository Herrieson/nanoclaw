import os
import json

def verify():
    report_path = "missing_report.txt"
    state = {
        "report_exists": False,
        "content_matches": False,
        "formatting_correct": False,
        "details": {}
    }

    expected_output = [
        "RX-101 - Lisinopril - Missing: 5 - Last Handled By: Charlie",
        "RX-103 - Amlodipine - Missing: 10 - Last Handled By: Bob",
        "RX-105 - Omeprazole - Missing: 10 - Last Handled By: Alice",
        "RX-106 - Gabapentin - Missing: 5 - Last Handled By: David"
    ]

    if os.path.exists(report_path):
        state["report_exists"] = True
        with open(report_path, "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        state["details"]["actual_lines"] = lines
        state["details"]["expected_lines"] = expected_output

        if lines == expected_output:
            state["content_matches"] = True
            state["formatting_correct"] = True
        else:
            # Check if content is mostly there but formatting is slightly off
            actual_str = " ".join(lines).lower()
            if "rx-101" in actual_str and "charlie" in actual_str and "5" in actual_str:
                state["content_matches"] = True # Relaxed match for LLM judge info

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
