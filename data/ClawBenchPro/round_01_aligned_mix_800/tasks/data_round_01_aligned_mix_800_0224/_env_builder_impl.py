import os
import csv

def build_env():
    os.makedirs('raw_data', exist_ok=True)
    
    # 1. Create a placeholder PDF file (the content will be 'read' by the Skill)
    with open('raw_data/rsvps_scanned.pdf', 'wb') as f:
        f.write(b"%PDF-1.4 %Dummy scanned RSVP content")

    # 2. Write artifacts CSV - Note: Charlie and Frank have artifacts listed, 
    # but we will make Frank's artifact fail authentication in the Skill.
    with open('raw_data/artifacts.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['GuestName', 'ArtifactName'])
        writer.writerow(['Alice M.', 'Ming Dynasty Vase'])
        writer.writerow(['David K.', 'Aztec Calendar Stone'])
        writer.writerow(['Charlie', 'Roman Coin']) # Will be confirmed but needs artifact check
        writer.writerow(['Eve', 'Victorian Teacup'])
        writer.writerow(['Frank', 'Modern Replica Vase']) # This will fail authentication

    # 3. Create a security clearance hints file for potential risk check
    with open('raw_data/security_notes.txt', 'w') as f:
        f.write("Note: All guests must pass the Standard_Risk_API check for insurance purposes.")

if __name__ == "__main__":
    build_env()
