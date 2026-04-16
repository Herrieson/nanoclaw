import os

def build_env():
    base_dir = "assets/data_286"
    os.makedirs(base_dir, exist_ok=True)

    log_content = """2023-10-01 09:55:00 - SYSTEM STARTUP
2023-10-01 10:00:00 - signup - User: Maria Garcia | Tel: 555-0101 | Commitment: tres horas
2023-10-01 10:05:00 - error - connection reset by peer
2023-10-01 10:10:00 - signup - User: John Smith | Tel: 555-0102 | Commitment: 4
2023-10-01 10:12:00 - debug - memory flush
2023-10-01 10:15:00 - signup - User: Elena Cruz | Tel: 555-0103 | Commitment: dos
2023-10-01 10:20:00 - signup - User: Robert Jones | Tel: 555-0104 | Commitment: 2.5 hours
2023-10-01 10:25:00 - signup - User: Karen Angry | Tel: 555-0999 | Commitment: 10
2023-10-01 10:30:00 - signup - User: Luis Perez | Tel: 555-0105 | Commitment: cinco
2023-10-01 10:35:00 - signup - User: Sarah Connor | Tel: 555-0106 | Commitment: one hour
2023-10-01 10:40:00 - error - timeout
2023-10-01 10:45:00 - signup - User: Miguel Sanchez | Tel: 555-0888 | Commitment: ocho
2023-10-01 10:50:00 - signup - User: David Miller | Tel: 555-0107 | Commitment: 1.5
2023-10-01 10:55:00 - signup - User: Lucia Gomez | Tel: 555-0108 | Commitment: cuatro horas
2023-10-01 11:00:00 - SYSTEM SHUTDOWN
"""
    
    do_not_call_content = """# DO NOT CONTACT THESE NUMBERS
555-0999
555-0888
"""

    with open(os.path.join(base_dir, "raw_signups.log"), "w", encoding="utf-8") as f:
        f.write(log_content)
        
    with open(os.path.join(base_dir, "do_not_call.txt"), "w", encoding="utf-8") as f:
        f.write(do_not_call_content)

if __name__ == "__main__":
    build_env()
