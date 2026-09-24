import os
import csv

def build_env():
    os.makedirs("incoming_data", exist_ok=True)
    
    leads = [
        {"Company_Name": "TechNova Solutions", "Phone": "5551234567", "District": "East", "Type": "Corporation", "Email": "contact@technova.com"},
        {"Company_Name": "Downtown Soup Kitchen", "Phone": "5559876543", "District": "East", "Type": "Non-Profit", "Email": "help@downtownsoup.org"},
        {"Company_Name": "Westside Plumbers", "Phone": "5554443333", "District": "West", "Type": "Small Business", "Email": "plumber@westside.com"},
        {"Company_Name": "South District Retail", "Phone": "555-888-9999", "District": "South", "Type": "Retail", "Email": "sales@southretail.com"}, # Invalid phone format (hyphens) -> wait, prompt says "clean, valid 10-digit US phone number (absolutely no letters, weird characters...)" - hyphens are weird characters in this strict context, but let's make it clearer by providing a truly messy one
        {"Company_Name": "Alpha Logistics", "Phone": "555ABC1234", "District": "East", "Type": "Corporation", "Email": "alpha@logistics.com"},
        {"Company_Name": "Crescent Community Center", "Phone": "5557778888", "District": "South", "Type": "Community Center", "Email": "director@crescentcc.org"},
        {"Company_Name": "Eastern Telecom Partners", "Phone": "1234567890", "District": "East", "Type": "Partnership", "Email": "partner@etp.com"},
        {"Company_Name": "Northside Cafe", "Phone": "9998887777", "District": "North", "Type": "Small Business", "Email": "cafe@northside.com"},
        {"Company_Name": "Global Imports", "Phone": "12345", "District": "South", "Type": "Corporation", "Email": "info@global.com"}
    ]
    
    with open("incoming_data/leads_dump.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Company_Name", "Phone", "District", "Type", "Email"])
        writer.writeheader()
        writer.writerows(leads)

if __name__ == "__main__":
    build_env()
