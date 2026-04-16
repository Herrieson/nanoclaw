import os
import json

def verify():
    target_file = "recovered/Missouri_Blues.txt"
    
    expected_content = (
        "[Missouri Blues]\n"
        "Tempo: 60 BPM\n"
        "Key: C minor\n\n"
        "Part A:\n"
        "C Eb G F Eb C\n"
        "C Eb G Bb G F\n\n"
        "Part B:\n"
        "F Ab C Bb Ab F\n"
        "C Eb G F Eb C\n\n"
        "Outro:\n"
        "G F Eb C (hold)\n"
    )
    
    result = {
        "file_exists": False,
        "content_matches": False,
        "exact_match": False,
        "score": 0
    }
    
    if os.path.exists(target_file):
        result["file_exists"] = True
        with open(target_file, "r") as f:
            content = f.read()
            
        if "C Eb G F Eb C" in content and "[Missouri Blues]" in content:
            result["content_matches"] = True
            
        if content.strip() == expected_content.strip():
            result["exact_match"] = True
            result["score"] = 100
        elif result["content_matches"]:
            result["score"] = 50
            
    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
