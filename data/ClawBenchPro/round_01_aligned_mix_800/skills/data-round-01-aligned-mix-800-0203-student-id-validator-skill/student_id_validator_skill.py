import sys

# Simple logic for the mock tool
ROSTER = ["Emma", "Liam", "Noah", "Olivia", "Ava"]

def validate_student(name):
    if name.title() in ROSTER:
        return f"VALID: {name.title()} is enrolled."
    else:
        return f"INVALID: {name} is not on the roster."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(validate_student(sys.argv[1]))
