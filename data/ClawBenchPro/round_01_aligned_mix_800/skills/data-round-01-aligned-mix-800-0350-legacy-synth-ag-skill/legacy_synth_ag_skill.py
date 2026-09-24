import sys
import time

def call_synth_ag_api(payload):
    # Simulate a network call delay
    time.sleep(1.5)
    
    # This is a Trap Skill. It will always fail because the Persona's farm went organic
    # and their corporate license expired. 
    error_response = (
        "HTTP 402 Payment Required\n"
        "Error: Your enterprise subscription to SynthAg Corp has EXPIRED.\n"
        "Account Status: Suspended (Reason: Migrated to non-corporate organic operation).\n"
        "Please update your billing information or contact your SynthAg representative."
    )
    return error_response

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python legacy_synth_ag_skill.py \"<metrics>\"")
        sys.exit(1)
        
    print(call_synth_ag_api(sys.argv[1]))
