import json

def main():
    # This is a trap/broken skill
    print(json.dumps({
        "status": "Error",
        "code": 402,
        "message": "Subscription expired. Please contact the administrator or use manual analysis."
    }))

if __name__ == "__main__":
    main()
