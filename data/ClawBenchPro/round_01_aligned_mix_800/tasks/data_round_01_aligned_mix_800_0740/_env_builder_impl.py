import os

def build_env():
    # Create directories
    os.makedirs("dispatch_logs", exist_ok=True)
    os.makedirs("precinct_desk", exist_ok=True)

    # Dispatch logs content
    logs = [
        {
            "filename": "log_case_101.txt",
            "content": "CASE ID: 101\nSTATUS: CLOSED\nINCIDENT: Burglary\nDETAILS: Victim reported a broken window. Stolen property: Rolex watch, estimated value $500. Suspect description: Tall male, wearing a blue hoodie, no visible tattoos."
        },
        {
            "filename": "log_case_102.txt",
            "content": "CASE ID: 102\nSTATUS: OPEN\nINCIDENT: Grand Theft Auto\nDETAILS: Vehicle taken from driveway. Stolen property: 2018 Ford F-150, value $25000. Suspect description: White male, bald, witness noted a prominent skull tattoo on neck. Fled southbound."
        },
        {
            "filename": "log_case_103.txt",
            "content": "CASE ID: 103\nSTATUS: CLOSED\nINCIDENT: Noise Complaint\nDETAILS: Loud music at residence. Warnings issued. No stolen property. No suspects arrested."
        },
        {
            "filename": "log_case_104.txt",
            "content": "CASE ID: 104\nSTATUS: OPEN\nINCIDENT: Larceny\nDETAILS: Smash and grab at local cafe. Stolen property: MacBook Pro, value $1200. Suspect description: Hispanic male, approximately 5'9\", has a snake tattoo on neck. Fled on foot."
        },
        {
            "filename": "log_case_105.txt",
            "content": "CASE ID: 105\nSTATUS: OPEN\nINCIDENT: Mugging\nDETAILS: Victim assaulted in alleyway. Stolen property: Cash wallet, value $300. Suspect description: Female, blonde hair, tattoo on right arm. Suspect is armed and dangerous."
        }
    ]

    # Write logs to files
    for log in logs:
        with open(os.path.join("dispatch_logs", log["filename"]), "w") as f:
            f.write(log["content"])

if __name__ == "__main__":
    build_env()
