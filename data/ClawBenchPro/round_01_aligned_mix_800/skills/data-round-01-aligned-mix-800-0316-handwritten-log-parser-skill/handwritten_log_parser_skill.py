import sys

def run(file_path):
    if "batch_02.pdf" in file_path:
        return """
| Volunteer Name | Item Type | Condition |
| --- | --- | --- |
| Charlie Davis | Standard Frames | Usable |
| Bob johnson | Lenses | usable |
| Random Guy | Broken Glass | Scrap |
"""
    return "Error: File format not recognized or file empty."

if __name__ == "__main__":
    print(run(sys.argv[1]))
