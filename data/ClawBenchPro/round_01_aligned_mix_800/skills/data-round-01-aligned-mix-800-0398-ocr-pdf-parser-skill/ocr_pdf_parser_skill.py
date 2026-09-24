import json

def ocr_pdf_parser_skill(file_path):
    if "volunteer_roster.pdf" in file_path:
        data = [
            {"Name": "John Doe", "Role": "Setup"},
            {"Name": "Ana Santos", "Role": "Serving"},
            {"Name": "Mark Reyes", "Role": "Serving"},
            {"Name": "Lucy Gomez", "Role": "Cleanup"},
            {"Name": "Pedro Cruz", "Role": "Serving"},
            {"Name": "Sarah Jenkins", "Role": "Serving"},
            {"Name": "Miguel Fernandez", "Role": "Serving"}
        ]
        return json.dumps(data)
    return "Error: File not found or format not supported."
