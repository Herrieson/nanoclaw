import os
import json

def build_env():
    base_dir = "assets/data_268"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Product Catalog
    catalog = {
        "FUR-001": {"name": "Oak Dining Table", "price": 450},
        "FUR-002": {"name": "Leather Sofa", "price": 899},
        "FUR-003": {"name": "Bookshelf", "price": 120},
        "FUR-004": {"name": "Coffee Table", "price": 85},
        "FUR-005": {"name": "Recliner Chair", "price": 300}
    }
    with open(os.path.join(base_dir, "product_catalog.json"), "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=4)
        
    # 2. Register Logs (Contains valid and invalid/cancelled sales)
    register_logs = """[09:00] SYSTEM START
[10:05] SALE - Cus: John Doe, Ph: 555-0101, Item: FUR-001, Del: 2023-11-05
[10:30] CANCELLED - Cus: Alice, Ph: 555-9999, Item: FUR-004
[11:00] SALE - Cus: Mary Smith, Ph: 555-0202, Item: FUR-003, Del: 2023-11-03
[11:15] CASH REGISTER OPEN
"""
    with open(os.path.join(base_dir, "register_logs_monday.txt"), "w", encoding="utf-8") as f:
        f.write(register_logs)

    # 3. Notes to self (A messy text file with personal notes and some actual orders)
    notes = """Need to buy more milk and eggs after shift.
Oh, Mr. Jackson called. Ph: 555-0999. Wants FUR-002 delivered on 2023-11-04.
Church bake sale next Sunday, bring cupcakes.
Little Timmy lost his action figure toy again, need to look under the register.
Order for Sarah Lee, 555-1234, Item FUR-005, date 2023-11-02. She paid cash so I didn't ring it through the main system yet.
Do not forget to pick up the kids at 5 PM!
"""
    with open(os.path.join(base_dir, "notes_to_self.log"), "w", encoding="utf-8") as f:
        f.write(notes)

if __name__ == "__main__":
    build_env()
