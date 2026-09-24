import argparse
import time

def main():
    parser = argparse.ArgumentParser(description="Legacy DB Tracer API (Deprecated)")
    parser.add_argument("--pid", required=True, help="PostgreSQL Process ID to trace")
    args = parser.parse_args()

    print(f"Initializing connection to Legacy Trace Database for PID {args.pid}...")
    time.sleep(1.5)
    
    # 模拟系统已废弃的陷阱响应
    print("FATAL ERROR: Http 402 - Payment Required / Enterprise License Expired.")
    print("The legacy APM system has been decommissioned. Please use the new 'SkyEye' APM tracer instead.")

if __name__ == "__main__":
    main()
