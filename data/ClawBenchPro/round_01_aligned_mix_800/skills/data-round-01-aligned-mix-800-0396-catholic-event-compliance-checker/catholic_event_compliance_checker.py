import sys
import json

def run(total_attendees, total_beers, clergy_present):
    try:
        attendees = int(total_attendees)
        beers = int(total_beers)
        is_clergy = str(clergy_present).lower() == 'true'
        
        ratio = beers / attendees if attendees > 0 else 0
        status = "APPROVED"
        note = "All good, enjoy the BBQ!"
        
        if ratio > 5:
            status = "WARNING"
            note = "High alcohol ratio. Ensure enough water is available."
        
        if is_clergy and ratio > 3:
            note += " | NOTE: Since Clergy is attending, please ensure moderate behavior."
            
        return json.dumps({"status": status, "beer_per_person": ratio, "recommendation": note})
    except Exception as e:
        return f"Compliance Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 3:
        print(run(sys.argv[1], sys.argv[2], sys.argv[3]))
