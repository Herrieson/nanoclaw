import os
import sqlite3

def build_env():
    base_dir = "assets/data_249"
    emails_dir = os.path.join(base_dir, "emails")
    
    os.makedirs(emails_dir, exist_ok=True)
    
    # Generate mock emails
    emails = {
        "email_01.txt": "Hi Ian,\n\nCount me in for the Blue Ridge trip! Our Q3 budget is $75,000 for this project, so we are good to go.\n\nBest,\nSarah Jenkins\nTechCorp\ns.jenkins@techcorp.com",
        "email_02.txt": "Ian,\n\nI'd love to go to Blue Ridge but we only have 40,000 USD allocated right now. I don't think we can swing it.\n\n- Mike\nBuildIt\nmike@buildit.com",
        "email_03.txt": "Hey man,\n\nI'm down for the camping trip, but we want to do the Smoky Mountains instead. Budget is $100k.\n\n- David Row\nArchinc\ndavid@archinc.com",
        "email_04.txt": "Ian! \n\nBlue Ridge sounds perfect. We've got 55,000 to spend. Let's do it.\n\nCheers,\nEmily Chen\nDesignCo\nemily.chen@designco.com",
        "email_05.txt": "We are confirmed for Blue Ridge. Budget: $120,000.\n\n- Robert Vance\nVance Refrigeration\nbob@vance.com",
        "email_06.txt": "Hey Ian, Blue ridge sounds fun. However, my boss just slashed our budget to $48,000. Sorry!\n\nBest, \nJim\nPaperCo\njim@paperco.com"
    }
    
    for filename, content in emails.items():
        with open(os.path.join(emails_dir, filename), "w") as f:
            f.write(content)
            
    # Generate SQLite DB
    db_path = os.path.join(base_dir, "campsites.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE permits (
            location TEXT,
            min_size INTEGER,
            max_size INTEGER,
            permit_code TEXT
        )
    ''')
    
    permit_data = [
        ('Blue Ridge', 1, 3, 'BR-SMALL-99'),
        ('Blue Ridge', 4, 10, 'BR-MED-42'),
        ('Blue Ridge', 11, 20, 'BR-LARGE-01'),
        ('Smoky Mountains', 1, 5, 'SM-BASE'),
        ('Yosemite', 1, 10, 'YOS-100')
    ]
    
    cursor.executemany('INSERT INTO permits VALUES (?, ?, ?, ?)', permit_data)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_env()
