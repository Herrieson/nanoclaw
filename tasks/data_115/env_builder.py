import os

def build_env():
    base_dir = "assets/data_115"
    os.makedirs(base_dir, exist_ok=True)

    log_content = """Log started... Ugh I hate fast fashion.
Alice: 5 clothes, 2 shoes
Why do people even buy polyester?
Bob donated 3 bags and 1 clothes
Charlie - clothes: 10, shoes: 5
*fidgets with hair* I really need a matcha latte.
Diana: 2 bags, 10 clothes, 1 shoes
Emma donated 5 bags, 2 shoes
Fiona - bags: 10, clothes: 5
Greg: 1 clothes
I think I'll go volunteer at the community garden tomorrow.
Hannah donated 20 clothes
"""
    with open(os.path.join(base_dir, "donations_log.txt"), "w") as f:
        f.write(log_content)

    broken_script = """import panda as pd
def calc_points():
  # idk how to do this
  data = open('donations_log.txt').read()
  for line in data
    print(line)
calc_points
"""
    with open(os.path.join(base_dir, "app_script.py"), "w") as f:
        f.write(broken_script)

if __name__ == "__main__":
    build_env()
