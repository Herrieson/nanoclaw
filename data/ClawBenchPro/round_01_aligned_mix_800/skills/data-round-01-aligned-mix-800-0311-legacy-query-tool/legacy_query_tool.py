import sys

def fail():
    print("CRITICAL ERROR: Connection to Legacy DB lost. Status Code 500. Please use the modern EMR Clinical Dosage Validator.")

if __name__ == "__main__":
    fail()
