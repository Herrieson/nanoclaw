import os

def build_env():
    # Create directories
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("skills", exist_ok=True)
    
    # Create the 'PDF' file (mocked as a text file for the skill to read)
    # Content structure: Trail_ID | Encoded_KM | Issue_Type | Severity
    pdf_content = """
    OFFICIAL TRAIL INSPECTION LOG 2023 - POST-STORM
    ----------------------------------------------
    T-01 | KM_1.2 | Fallen Tree | 9
    T-01 | KM_2.5 | Clear | 1
    T-02 | KM_0.5 | Erosion | 8
    T-02 | INVALID | Fallen Tree | 10
    T-03 | KM_3.0 | Overgrowth | 4
    T-03 | KM_4.1 | Mudslide | 9
    T-04 | KM_1.1 | Fallen Tree | 8
    T-05 | KM_2.2 | Wasp Nest | 7
    T-06 | MISSING | Erosion | 9
    T-07 | KM_5.5 | Fallen Tree | 10
    """
    
    with open("raw_data/trail_logs_2023.pdf", "w", encoding="utf-8") as f:
        f.write(pdf_content)

if __name__ == "__main__":
    build_env()
