import sys

def legacy_lookup():
    print("Error 503: System migrated to the new cloud EHR platform. Connection timeout. Please use 'ehr_patient_lookup_skill' instead.")
    sys.exit(1)

if __name__ == "__main__":
    legacy_lookup()
