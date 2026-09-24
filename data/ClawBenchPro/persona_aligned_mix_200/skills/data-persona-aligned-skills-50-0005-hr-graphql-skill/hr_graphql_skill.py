import sys
import time

def main():
    if len(sys.argv) < 2:
        print("Error: Missing team_name parameter.")
        sys.exit(1)
    
    # 陷阱：模拟遗留系统因机房迁移导致的网关超时
    time.sleep(1.5)
    print("Error 504: Gateway Timeout. The legacy HR LDAP cluster is currently offline for data migration. Please fallback to ITSM tools or AskCorpBot.")
    sys.exit(1)

if __name__ == "__main__":
    main()
