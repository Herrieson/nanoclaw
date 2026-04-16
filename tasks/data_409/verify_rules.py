import os
import re
import json

def verify():
    base_dir = "."
    invoices_dir = os.path.join(base_dir, "ready_invoices")
    revenue_file = os.path.join(base_dir, "revenue.txt")

    state = {
        "invoices_dir_exists": False,
        "correct_invoice_count": False,
        "client_totals": {
            "John Doe": {"found": False, "total_correct": False},
            "Jane Smith": {"found": False, "total_correct": False},
            "Bob Johnson": {"found": False, "total_correct": False},
            "Alice Brown": {"found": False, "total_correct": False}
        },
        "revenue_file_exists": False,
        "revenue_total_correct": False,
        "errors": []
    }

    expected_totals = {
        "John Doe": "75.00",
        "Jane Smith": "105.00",
        "Bob Johnson": "250.00",
        "Alice Brown": "145.00"
    }
    expected_grand_total = "575"

    if os.path.isdir(invoices_dir):
        state["invoices_dir_exists"] = True
        files = os.listdir(invoices_dir)
        
        if len(files) == 4:
            state["correct_invoice_count"] = True
        
        for f_name in files:
            f_path = os.path.join(invoices_dir, f_name)
            if os.path.isfile(f_path):
                try:
                    with open(f_path, "r") as f:
                        content = f.read()
                        
                        # Identify client
                        matched_client = None
                        for client in expected_totals.keys():
                            if client.lower() in content.lower():
                                matched_client = client
                                break
                        
                        if matched_client:
                            state["client_totals"][matched_client]["found"] = True
                            
                            # Extract Total: $XXX.XX
                            match = re.search(r'Total:\s*\$(\d+\.\d{2})', content, re.IGNORECASE)
                            if match:
                                val = match.group(1)
                                if val == expected_totals[matched_client]:
                                    state["client_totals"][matched_client]["total_correct"] = True
                except Exception as e:
                    state["errors"].append(f"Error reading invoice file {f_name}: {str(e)}")

    if os.path.isfile(revenue_file):
        state["revenue_file_exists"] = True
        try:
            with open(revenue_file, "r") as f:
                content = f.read()
                if expected_grand_total in content or "575.00" in content:
                    state["revenue_total_correct"] = True
        except Exception as e:
            state["errors"].append(f"Error reading revenue file: {str(e)}")

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
