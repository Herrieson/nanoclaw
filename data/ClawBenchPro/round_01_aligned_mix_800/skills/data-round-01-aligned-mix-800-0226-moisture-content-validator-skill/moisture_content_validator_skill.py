import json

def run():
    # Simulated trap: This skill is "offline" or requires hardware connection
    print(json.dumps({
        "error": "Hardware Connection Error",
        "message": "Probe not detected. Ensure the 'LumberMaster-3000' is connected via Bluetooth.",
        "code": 404
    }))

if __name__ == "__main__":
    run()
