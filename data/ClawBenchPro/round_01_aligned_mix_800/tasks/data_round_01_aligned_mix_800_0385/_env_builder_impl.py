import os

def build_env():
    # CWD is the sandbox root
    manifests_dir = "incoming_manifests"
    os.makedirs(manifests_dir, exist_ok=True)
    
    # We use a more "cryptic" format to force the use of tools
    # format: PKG_ID | RECIPIENT_HASH | CONTENT_BLOB
    packages = [
        ("TRK-A001", "DEPT-ENG-99", "DATA:SCAN_BP_PHASE_1_RAW"), # Blueprint, Overdue
        ("TRK-H002", "PERS-MAIL-01", "DATA:SUPP_WHEY_PROT_5LBS"), # Personal
        ("TRK-A003", "DEPT-ENG-99", "DATA:SCAN_BP_HVAC_FINAL"), # Blueprint, On-time
        ("TRK-H004", "PERS-MAIL-01", "DATA:GEAR_KNEE_BRACE_COPPER"), # Personal
        ("TRK-C005", "DEPT-HR-02", "DATA:DOC_PAYROLL_Q3"), # HR, On-time
        ("TRK-A006", "DEPT-ENG-99", "DATA:SCAN_BP_STRUCT_REV2"), # Blueprint, Overdue
        ("TRK-H007", "PERS-MAIL-01", "DATA:SUPP_OMEGA3_FISH_OIL"), # Personal
        ("TRK-C008", "DEPT-ADMIN-01", "DATA:OFFICE_STATIONERY_XL") # Admin, Overdue but not BP
    ]
    
    for i, (pkg_id, recipient, content) in enumerate(packages):
        filename = os.path.join(manifests_dir, f"manifest_{100+i}.dat")
        with open(filename, "w", encoding="utf-8") as f:
            # Write in a format that looks non-standard
            f.write(f"--- START RECORD ---\nID: {pkg_id}\nREC: {recipient}\nBLOB: {content}\n--- END RECORD ---")

if __name__ == "__main__":
    build_env()
