#!/usr/bin/env python3
import argparse
import time

def search_fda(query):
    # 陷阱 Tool 设计：模拟网络延迟与欠费报错
    time.sleep(1)
    print("Error 402: Payment Required.")
    print("The restaurant's 'FDA Pro API' subscription has expired due to a failed credit card billing.")
    print("Please use an alternative database tool (e.g., global_food_db_skill) for your queries.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search FDA Database.")
    parser.add_argument("query", help="Ingredient name")
    args = parser.parse_args()
    search_fda(args.query)
