import os

def service(file_path):
    if not os.path.exists(file_path):
        return "Error: File not found."
    # Simplified mock: In a real env, this would use PyPDF2.
    # Here it reads the text-based mock PDF we created.
    with open(file_path, "r") as f:
        return f.read()
