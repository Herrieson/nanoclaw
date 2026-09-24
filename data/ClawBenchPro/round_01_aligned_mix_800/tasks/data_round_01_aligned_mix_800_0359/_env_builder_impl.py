import os

def build_env():
    # Create directories
    os.makedirs("incoming_data", exist_ok=True)
    os.makedirs("skills", exist_ok=True)
    
    # Create a Mock PDF file (simulated as a text file but named .pdf to force tool usage)
    # In a real environment, this would be a binary PDF. Here we simulate the content 
    # that a PDF parser would extract.
    pdf_content = """
RA_DATA_V9 - UNIFIED COMMUNICATIONS CAMPAIGN
-------------------------------------------
ID | Company_Name | Phone_Raw | Location_Code | Category | Email
01 | TechNova Solutions | 5551234567 | LOC-E101 | Corporation | contact@technova.com
02 | Downtown Soup Kitchen | 5559876543 | LOC-E202 | Non-Profit | help@downtownsoup.org
03 | Westside Plumbers | 5554443333 | LOC-W001 | Small Business | plumber@westside.com
04 | South District Retail | 555-888-9999 | LOC-S999 | Retail | sales@southretail.com
05 | Alpha Logistics | 555ABC1234 | LOC-E105 | Corporation | alpha@logistics.com
06 | Crescent Community Center | 5557778888 | LOC-S505 | Community Center | director@crescentcc.org
07 | Eastern Telecom Partners | 1234567890 | LOC-E109 | Partnership | partner@etp.com
08 | Northside Cafe | 9998887777 | LOC-N303 | Small Business | cafe@northside.com
09 | Global Imports | 12345 | LOC-S111 | Corporation | info@global.com
-------------------------------------------
FOOTER: CONFIDENTIAL TELECOM DATA
"""
    
    with open("incoming_data/leads_raw_v9.pdf", "w", encoding="utf-8") as f:
        f.write(pdf_content)

if __name__ == "__main__":
    build_env()
