import os
import json
import csv

def verify():
    base_dir = "."
    csv_path = os.path.join(base_dir, "delivery_schedule.csv")
    
    state = {
        "csv_exists": False,
        "has_correct_headers": False,
        "row_count": 0,
        "is_sorted_by_date": False,
        "data_accuracy": 0, # out of 4 correct rows
        "error_message": ""
    }
    
    if not os.path.exists(csv_path):
        state["error_message"] = "delivery_schedule.csv not found."
        print(json.dumps(state))
        return
        
    state["csv_exists"] = True
    
    expected_headers = ["Delivery Date", "Customer Name", "Phone", "Item Name", "Price"]
    expected_data = [
        {"Delivery Date": "2023-11-02", "Customer Name": "Sarah Lee", "Phone": "555-1234", "Item Name": "Recliner Chair", "Price": "300"},
        {"Delivery Date": "2023-11-03", "Customer Name": "Mary Smith", "Phone": "555-0202", "Item Name": "Bookshelf", "Price": "120"},
        {"Delivery Date": "2023-11-04", "Customer Name": "Mr. Jackson", "Phone": "555-0999", "Item Name": "Leather Sofa", "Price": "899"},
        {"Delivery Date": "2023-11-05", "Customer Name": "John Doe", "Phone": "555-0101", "Item Name": "Oak Dining Table", "Price": "450"}
    ]
    
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, [])
            
            # Allow minor case/space differences in headers
            clean_headers = [h.strip().lower() for h in headers]
            expected_clean_headers = [h.lower() for h in expected_headers]
            
            if clean_headers == expected_clean_headers:
                state["has_correct_headers"] = True
            
            rows = list(reader)
            state["row_count"] = len(rows)
            
            # Map columns by index if possible
            date_idx = clean_headers.index("delivery date") if "delivery date" in clean_headers else 0
            
            # Check sorting
            dates = [row[date_idx].strip() for row in rows if len(row) > date_idx]
            if dates == sorted(dates) and len(dates) == 4:
                state["is_sorted_by_date"] = True
            
            # Check accuracy
            correct_matches = 0
            for exp in expected_data:
                matched = False
                for row in rows:
                    row_str = " ".join(row).lower()
                    if (exp["Delivery Date"].lower() in row_str and 
                        exp["Customer Name"].lower() in row_str and 
                        exp["Phone"].lower() in row_str and 
                        exp["Item Name"].lower() in row_str and 
                        exp["Price"] in row_str):
                        matched = True
                        break
                if matched:
                    correct_matches += 1
            
            state["data_accuracy"] = correct_matches
            
    except Exception as e:
        state["error_message"] = f"Error reading CSV: {str(e)}"
        
    print(json.dumps(state))

if __name__ == "__main__":
    verify()
