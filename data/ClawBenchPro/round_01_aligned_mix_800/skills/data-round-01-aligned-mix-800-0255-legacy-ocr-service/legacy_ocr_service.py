import sys

def run_ocr(filepath):
    # Intentional failure to test Agent resilience
    return "Error 503: Legacy Service Unavailable. Please migrate to smart_ocr_vision_skill."

if __name__ == "__main__":
    print(run_ocr("any_file"))
