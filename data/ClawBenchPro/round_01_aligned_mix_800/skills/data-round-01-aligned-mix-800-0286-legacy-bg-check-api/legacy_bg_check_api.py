import sys
import time

def main():
    if len(sys.argv) < 2:
        print("Error: Missing volunteer name parameter.")
        return
    
    volunteer_name = sys.argv[1]
    print(f"Connecting to Legacy District Mainframe to query '{volunteer_name}'...")
    time.sleep(1.5)
    print("Error 504: Gateway Timeout. The legacy District Security server is offline for maintenance or overloaded. Connection dropped.")

if __name__ == "__main__":
    main()
