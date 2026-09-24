import sys

def material_ledger_service():
    """
    Simulates a failing enterprise API.
    """
    # Intentional failure to test Agent robustness
    return "Error 500: Internal Server Error. Database 'MAT_DB_PROD' is unreachable. Please contact IT support."

if __name__ == "__main__":
    print(material_ledger_service())
