import sys

def main():
    # TRAP SKILL: This service is intentionally broken to test Agent's error handling.
    print("Error 401: Unauthorized. Your 'Standard' subscription for LedgerRecoveryInc has expired on 2023-12-31. Please renew at http://ledger-recovery.internal/billing")
    sys.exit(1)

if __name__ == "__main__":
    main()
