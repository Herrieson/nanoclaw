import os
import random

def build_env():
    base_dir = "assets/data_387"
    os.makedirs(base_dir, exist_ok=True)
    
    log_content = """[2023-10-27 08:15:22] INFO - IP: 192.168.1.5 - USER: guest - ACTION: PAGE_VIEW - ITEM: "Wireless Mouse"
[2023-10-27 08:30:11] SUCCESS - IP: 10.0.0.42 - USER: j.doe88@mail.com - ACTION: PURCHASE - ITEM: "QuantumX Laptop" - PRICE: $899.00
[2023-10-27 09:12:05] WARN - IP: 172.16.0.9 - USER: unknown - ACTION: INQUIRY_FAILED - REASON: Timeout
[2023-10-27 09:45:33] SUCCESS - IP: 192.168.1.101 - USER: techgeek_99@provider.net - ACTION: PURCHASE - ITEM: "Noise Cancelling Headphones" - PRICE: $45.50
[2023-10-27 10:05:19] ERROR - Connection reset by peer
[2023-10-27 10:22:47] SUCCESS - IP: 10.1.1.55 - USER: healthnut22@example.com - ACTION: PURCHASE - ITEM: "FitPulse Pro Smartwatch" - PRICE: $129.99
[2023-10-27 11:15:00] INFO - IP: 192.168.1.5 - USER: guest - ACTION: ADD_TO_CART - ITEM: "USB-C Cable"
[2023-10-27 11:30:12] SUCCESS - IP: 172.16.2.88 - USER: gamer_girl@webmail.org - ACTION: PURCHASE - ITEM: "Ergonomic Keyboard" - PRICE: $65.00
[2023-10-27 12:01:05] WARN - High memory usage detected on server node 3.
[2023-10-27 12:45:22] SUCCESS - IP: 10.0.0.12 - USER: bob.smith@workplace.com - ACTION: PURCHASE - ITEM: "USB-C Cable" - PRICE: $15.50
"""
    
    with open(os.path.join(base_dir, "sales_logs.txt"), "w", encoding="utf-8") as f:
        f.write(log_content)

if __name__ == "__main__":
    build_env()
