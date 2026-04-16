import os

def build_env():
    base_dir = "assets/data_253"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Messy payment logs
    # Los Amigos shortages:
    # Miguel: 45 * 22 = 990. Paid: 800. Shortage = 190
    # Carlos: 30 * 22 = 660. Paid: 550. Shortage = 110
    # Hector: 40 * 25 = 1000. Paid: 850. Shortage = 150
    # Total Shortage = 450
    log_content = """
    [SYSTEM DUMP 2023-10]
    TX-9920 | Titan Concrete | Worker: John | Hrs: 40 | Rate: $30/hr | Actual Paid: $1200 | Note: clear
    TX-9921 | Los Amigos Builders | Worker: Miguel | Hrs: 45 | Rate: $22/hr | Actual Paid: $800 | Note: uniform fee $50, admin fee $140
    TX-9922 | Apex Framing | Worker: Dave | Hrs: 20 | Rate: $25/hr | Actual Paid: $500 
    ERROR_LINE: null data
    TX-9923 | Los Amigos Builders | Worker: Carlos | Hrs: 30 | Rate: $22/hr | Actual Paid: $550 | Note: late fee $110
    TX-9924 | City Plumbers | Worker: Sam | Hrs: 10 | Rate: $50/hr | Actual Paid: $500
    TX-9925 | Los Amigos Builders | Worker: Hector | Hrs: 40 | Rate: $25/hr | Actual Paid: $850 | Note: truck rental $150
    [END DUMP]
    """
    
    with open(os.path.join(base_dir, "gc_payment_logs.txt"), "w", encoding="utf-8") as f:
        f.write(log_content.strip())

    # 2. HTML Directory
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>Local Legal Aid</title></head>
    <body>
        <h1>Legal Directory</h1>
        <div class="lawyer-card">
            <h2>James Mitchell</h2>
            <p>Specialty: Corporate Law</p>
            <p>Email: j.mitchell@law-mock.com</p>
        </div>
        <div class="lawyer-card">
            <h2>Sofia Ramirez</h2>
            <p>Specialty: Immigrant Workers Rights & Wage Theft</p>
            <p>Email: s.ramirez@workersjustice-mock.org</p>
            <p>Phone: 555-0192</p>
        </div>
        <div class="lawyer-card">
            <h2>David Chen</h2>
            <p>Specialty: Family Law</p>
            <p>Email: d.chen@familylaw-mock.org</p>
        </div>
    </body>
    </html>
    """
    
    with open(os.path.join(base_dir, "legal_aid_directory.html"), "w", encoding="utf-8") as f:
        f.write(html_content.strip())

if __name__ == "__main__":
    build_env()
