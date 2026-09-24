import sys
import json

def classify(title):
    children_titles = ["goodnight moon", "charlotte's web", "the cat in the hat", 
                       "green eggs and ham", "one fish two fish", "lorax"]
    adult_titles = ["the shining", "american psycho", "it"]
    
    t = title.lower()
    if any(k in t for k in children_titles):
        return {"category": "Children"}
    if any(k in t for k in adult_titles):
        return {"category": "Adult"}
    return {"category": "Unknown"}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(json.dumps(classify(sys.argv[1])))
    else:
        print(json.dumps({"error": "No title provided"}))
