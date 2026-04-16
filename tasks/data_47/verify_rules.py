import os
import json

def verify():
    result = {
        "success": False,
        "score": 0,
        "message": "star_athletes.txt not found in the workspace."
    }
    
    file_path = "star_athletes.txt"
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip().split("\n")
                
            # Expected athletes with count >= 4
            expected = {
                "Sarah,Connor,5",
                "Kyle,Reese,4",
                "Miles,Dyson,4"
            }
            
            actual = set([line.strip() for line in content if line.strip()])
            
            if actual == expected:
                result["success"] = True
                result["score"] = 100
                result["message"] = "Successfully extracted and calculated all star athletes!"
            else:
                result["score"] = max(0, 100 - (len(expected.symmetric_difference(actual)) * 20))
                result["message"] = f"Content mismatch. Expected {expected}, but got {actual}"
                
        except Exception as e:
            result["score"] = 0
            result["message"] = f"Error reading star_athletes.txt: {str(e)}"
            
    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
