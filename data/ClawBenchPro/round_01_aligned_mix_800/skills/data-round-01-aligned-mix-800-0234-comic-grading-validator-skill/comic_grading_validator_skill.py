import sys
import re

def convert_grade(grade_str):
    grade_map = {
        "MINT": 10.0,
        "NM": 9.4,
        "VF": 8.0,
        "FN": 6.0,
        "VG": 4.0,
        "GD": 2.0,
        "FR": 1.0,
        "PR": 0.5
    }
    # Extract numbers if present
    nums = re.findall(r"[-+]?\d*\.\d+|\d+", grade_str)
    if nums:
        return float(nums[0])
    
    # Match keywords
    upper_grade = grade_str.upper()
    for key, val in grade_map.items():
        if key in upper_grade:
            return val
    return 0.0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("0.0")
    else:
        print(convert_grade(sys.argv[1]))
