import sys

def calculate_hours(session_id):
    # Precise billing data (different from rough log notes)
    db = {
        "SE-101": 4.75,
        "SE-102": 0.0,
        "SE-103": 6.0,
        "SE-104": 0.0
    }
    return db.get(session_id, "Error: Session ID not found.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(calculate_hours(sys.argv[1]))
