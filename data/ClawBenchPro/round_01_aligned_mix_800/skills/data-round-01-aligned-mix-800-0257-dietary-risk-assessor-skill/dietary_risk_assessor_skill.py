import sys

def main():
    if len(sys.argv) < 2:
        print("Standard")
        return
    
    query = sys.argv[1].lower()
    high_risk_keywords = ["peanut", "vegan", "allergy", "lactose", "keto", "gluten", "vegetarian"]
    
    if any(k in query for k in high_risk_keywords) and "none" not in query:
        print("High Risk - Special Chow Required")
    else:
        print("Standard")

if __name__ == "__main__":
    main()
