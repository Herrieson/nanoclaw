import os
import json
import re

def verify():
    result = {
        "invitation_file_exists": False,
        "plot_correct": False,
        "emails_correct": False,
        "format_correct": False,
        "found_plot": None,
        "found_emails": []
    }

    target_file = "invitation.txt"
    expected_plot = "D-92"
    expected_emails = {"sarah.green@earth.org", "mike.plants@eco.net", "tom_volunteer@yahoo.com"}
    wrong_emails = {"david_88@mail.com", "anna_nature@gmail.com"}

    if os.path.exists(target_file):
        result["invitation_file_exists"] = True
        with open(target_file, "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        if len(lines) >= 2:
            # Check Plot
            plot_line = lines[0]
            if plot_line.lower().startswith("plot:"):
                result["format_correct"] = True
                plot_val = plot_line.split(":", 1)[1].strip()
                result["found_plot"] = plot_val
                if expected_plot.lower() in plot_val.lower():
                    result["plot_correct"] = True

            # Check Emails
            email_line = lines[1]
            if email_line.lower().startswith("to:"):
                emails_str = email_line.split(":", 1)[1]
                # Extract all emails using regex just in case
                found_emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', emails_str))
                result["found_emails"] = list(found_emails)

                if found_emails == expected_emails:
                    result["emails_correct"] = True
                elif expected_emails.issubset(found_emails) and not found_emails.intersection(wrong_emails):
                    result["emails_correct"] = True # Slightly lenient if they added extra non-conflicting things, but shouldn't happen.

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
