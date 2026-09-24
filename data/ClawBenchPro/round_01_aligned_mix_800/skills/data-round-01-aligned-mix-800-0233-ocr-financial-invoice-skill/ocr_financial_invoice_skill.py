import os

def service(image_path):
    if not os.path.exists(image_path):
        return "Error: File not found."
    
    if "march" in image_path.lower():
        return """
        --- SCANNED LEDGER MARCH ---
        Tenant: John Smith | Amount: 1200
        Tenant: Alice Johnson | Amount: 1500
        Tenant: Robert Brown | Amount: 1100
        Tenant: Michael Wilson | Amount: 1350
        Tenant: Sarah Miller | Amount: 1600
        Tenant: Zodiac Killer | Amount: 2000
        ----------------------------
        Note: Page 2 is missing (Emily Davis record not found).
        """
    return "Error: Unsupported image format or unreadable content."
