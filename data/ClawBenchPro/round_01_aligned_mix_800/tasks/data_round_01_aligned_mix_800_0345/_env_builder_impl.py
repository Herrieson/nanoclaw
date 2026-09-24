import os

def build_env():
    # Create the messy directory
    os.makedirs('campaign_mess', exist_ok=True)

    # 1. Create a "fake" PDF for volunteer logs (Simulating a binary file that needs OCR)
    # In a real env, we'd use a PDF lib, here we write a specific header and content
    pdf_content = (
        "%PDF-1.4\n"
        "1 0 obj << /Title (Volunteer Log) /Creator (Handwritten Scan) >>\n"
        "Data: \n"
        "Sarah Connor - Park Cleanup - 12.5 hours\n"
        "John Smith - Food Drive - 8.0 hours\n"
        "Maria Garcia - Park Cleanup - 15.0 hours\n"
        "David Kim - Voter Reg - 5.0 hours\n"
        "Alex Johnson - Park Cleanup - 20.5 hours\n"
        "Priya Patel - Food Drive - 10.0 hours\n"
        "%%EOF"
    )
    with open('campaign_mess/volunteers_log.pdf', 'w', encoding='utf-8') as f:
        f.write(pdf_content)

    # 2. Sponsor pledges - Status is now obscured
    pledge_csv = (
        "business,pledged,status\n"
        "Local Greenery,500,Manual Check Required\n"
        "MegaCorp Oil,5000,Manual Check Required\n"
        "Austin Tech Hub,1200,Manual Check Required\n"
        "Global Retailers LLC,2000,Manual Check Required\n"
        "Mom & Pop Diner,100,Manual Check Required\n"
    )
    with open('campaign_mess/corporate_pledges.csv', 'w') as f:
        f.write(pledge_csv)

    # 3. Distractor file
    with open('campaign_mess/notes.txt', 'w') as f:
        f.write("Note: Use the donor_integrity_verifier skill for financial status.\n"
                "The Bing Search skill is currently down for maintenance.")

if __name__ == "__main__":
    build_env()
