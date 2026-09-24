import json
import sys

def main():
    # Mock PDF parser: reads the file content as if it were a PDF
    try:
        import sys
        # In this task, the env_builder creates a text file with .pdf extension
        with open("messy_records/intake_forms.pdf", "r") as f:
            content = f.read()
        print(json.dumps({"content": content}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
