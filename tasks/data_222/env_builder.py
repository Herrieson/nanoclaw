import os
import csv

def build_env():
    # Define paths
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../assets/data_222'))
    os.makedirs(base_dir, exist_ok=True)

    # 1. Mock HTML Festival Site
    html_content = """
    <html>
    <head><title>Peach State Beats Festival</title></head>
    <body>
        <h1>Welcome to Peach State Beats!</h1>
        <div id="tickets">
            <h2>Tickets</h2>
            <ul>
                <li class="ticket" data-type="GA" data-price="150">General Admission - $150</li>
                <li class="ticket" data-type="VIP" data-price="350">VIP Pass - $350</li>
            </ul>
        </div>
        <div id="schedule">
            <h2>Schedule</h2>
            <div class="performance">
                <span class="artist">The Midnight</span> - <span class="time">18:00</span>
            </div>
            <div class="performance">
                <span class="artist">Neon Indian</span> - <span class="time">19:30</span>
            </div>
            <div class="performance">
                <span class="artist">Tame Impala</span> - <span class="time">21:00</span>
            </div>
            <div class="performance">
                <span class="artist">Kendrick Lamar</span> - <span class="time">22:30</span>
            </div>
        </div>
    </body>
    </html>
    """
    with open(os.path.join(base_dir, 'festival_site.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)

    # 2. Broken Python Script
    broken_script = """
import re
import json

def parse_html():
    with open('festival_site.html', 'r') as f:
        content = f.read()
    
    # Oops, bad regex and bad logic
    artists = re.findall(r'<span class="artist">(.*?)</span>', content)
    times = re.findall(r'<span class="time">(.*?)</span>', content)
    
    # this will zip them, but I forgot to write to a file properly
    schedule = dict(zip(artists, times))
    
    # Intentional error: writing dictionary directly without json dumps
    with open('lineup.json', 'w') as f:
        f.write(schedule)

if __name__ == "__main__":
    parse_html()
"""
    with open(os.path.join(base_dir, 'get_lineup.py'), 'w', encoding='utf-8') as f:
        f.write(broken_script)

    # 3. Budget CSV (Net balance: 500 (Income) - 100 (Expense) = 400. Enough for VIP)
    budget_data = [
        ['Date', 'Description', 'Type', 'Amount'],
        ['2023-10-01', 'Retail Job Paycheck', 'Income', '600.00'],
        ['2023-10-02', 'Student Loan Payment', 'Expense', '250.00'],
        ['2023-10-05', 'Groceries', 'Expense', '75.00'],
        ['2023-10-10', 'Clothes Shopping', 'Expense', '125.00'],
        ['2023-10-15', 'Babysitting', 'Income', '250.00']
    ]
    # Total Income: 850
    # Total Expense: 450
    # Net: 400
    with open(os.path.join(base_dir, 'budget.csv'), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(budget_data)

    # 4. Favorite Artists Text File
    faves = "Neon Indian\nKendrick Lamar\n"
    with open(os.path.join(base_dir, 'my_faves.txt'), 'w', encoding='utf-8') as f:
        f.write(faves)

if __name__ == "__main__":
    build_env()
