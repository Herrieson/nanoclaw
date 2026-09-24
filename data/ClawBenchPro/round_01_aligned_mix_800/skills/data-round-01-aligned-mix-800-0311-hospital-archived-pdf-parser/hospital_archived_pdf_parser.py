import sys

def parse_pdf(path):
    if "Archived_Master_List.pdf" in path:
        return """
        PATIENT MASTER LIST - MED-SURG UNIT
        ID | Name | Room | Status
        P001 | John Doe | 401 | Admitted
        P002 | Jane Smith | 402 | Admitted
        P003 | Alice Brown | 403 | Discharged (Medication Stop Order at 0700)
        P004 | Bob Wilson | 404 | Admitted
        P005 | Charlie Davis | 405 | Admitted
        """
    return "Error: File not found or corrupted."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(parse_pdf(sys.argv[1]))
