import sys
import json

def main():
    try:
        data = json.loads(sys.argv[1])
        moisture = int(str(data.get("moisture_content", "100")).replace("%", ""))
        grade = data.get("fungi_grade", "Grade D").upper()
        
        if moisture < 15 and grade in ["GRADE A", "GRADE B"]:
            print(json.dumps({"status": "Usable", "detail": "Structural integrity confirmed."}))
        else:
            print(json.dumps({"status": "Rotted/Unusable", "detail": "High risk of failure. Do not use for porch."}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
