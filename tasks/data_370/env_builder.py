import os
import sqlite3

def build_env():
    base_dir = "assets/data_370"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create complaints.txt
    complaints_content = """
    Omg where is my package?? I ordered it three weeks ago. Tracking is TX-RT-8821. Please help!
    Hey, my tracking number TX-RT-1092 says it's delivered but it's not here.
    I am very upset. The shipment TX-RT-4433 is still pending! And what about my other one, TX-RT-9999?
    Hello, tracking CA-RT-5555 is broken.
    Is my thing coming? tracking: TX-RT-7710. Also TX-RT-8821 again, I'm double emailing!
    The system says TX-RT-2001 is lost.
    """
    with open(os.path.join(base_dir, "complaints.txt"), "w") as f:
        f.write(complaints_content)

    # 2. Create shipping_db.sqlite
    db_path = os.path.join(base_dir, "shipping_db.sqlite")
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE shipments (
            tracking_id TEXT PRIMARY KEY,
            status TEXT,
            current_location TEXT,
            customer_email TEXT
        )
    """)

    # Insert data
    # TX-RT-8821: DELAYED (Target)
    # TX-RT-1092: DELIVERED (Ignore)
    # TX-RT-4433: DELAYED (Target)
    # TX-RT-9999: IN_TRANSIT (Ignore)
    # TX-RT-7710: DELAYED (Target)
    # TX-RT-2001: LOST (Ignore - prompt only asked for DELAYED)
    # TX-RT-3000: DELAYED (Not in text, Ignore)

    shipments = [
        ("TX-RT-8821", "DELAYED", "Warehouse A", "angry_dude@email.com"),
        ("TX-RT-1092", "DELIVERED", "Front Porch", "happy_gal@email.com"),
        ("TX-RT-4433", "DELAYED", "Transit Hub 2", "waiting123@email.com"),
        ("TX-RT-9999", "IN_TRANSIT", "Truck 42", "trucker@email.com"),
        ("TX-RT-7710", "DELAYED", "Sort Facility", "spontaneous@email.com"),
        ("TX-RT-2001", "LOST", "Unknown", "sadness@email.com"),
        ("TX-RT-3000", "DELAYED", "Warehouse B", "ghost@email.com")
    ]

    cursor.executemany("INSERT INTO shipments VALUES (?, ?, ?, ?)", shipments)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_env()
