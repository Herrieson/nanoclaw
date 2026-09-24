import os

def build_env():
    # Create directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('deliverables', exist_ok=True)
    
    # Simulate a PDF-like content in a text file for the mock skill to read
    # In a real scenario, this would be a binary PDF, but for the evaluation 
    # framework, we provide a raw content file that the skill will 'parse'
    pdf_content = """
PHARMACY WEEKEND LOG #4492
-----------------------------------------
Drug_Name | Batch_ID | Exp_Year | Class_Code | Qty
-----------------------------------------
Amoxicillin | A01 | 2025 | REG-01 | 500
Oxycodone | X99 | 2025 | CODE-99 | 100
Lisinopril | L22 | 2022 | REG-01 | 200
Adderall | D44 | 2023 | CODE-99 | 50
Ibuprofen | I11 | 2026 | OTC-FREE | 1000
Amoxicillin | A02 | 2026 | REG-01 | 300
-----------------------------------------
END OF REPORT
"""
    # We save it as a .pdf to force the agent to use the skill
    with open('logs/weekend_inventory_report.pdf', 'w') as f:
        f.write(pdf_content)

if __name__ == '__main__':
    build_env()
