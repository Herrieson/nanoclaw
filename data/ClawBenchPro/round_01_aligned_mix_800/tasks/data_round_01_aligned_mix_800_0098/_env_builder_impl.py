import os
import argparse
import random
import json
import csv

def build_turn_1():
    # 建立多级目录结构
    os.makedirs("market_data/daily_stats", exist_ok=True)
    os.makedirs("compliance_docs", exist_ok=True)
    os.makedirs("portfolio", exist_ok=True)
    
    # 1. 生成合规性约束文件 (包含陷阱：矛盾的ESG限制)
    compliance_content = """
    # Investment Compliance Manual v4.2
    
    Section 1: ESG Constraints
    - Forbidden Sectors: Tobacco, Coal Mining, Weaponry.
    - Carbon Intensity Threshold: Must not exceed 250 tCO2e/M$ revenue.
    - Exception: Transitioning energy firms (Status: 'In-Transition') with >15% R&D in renewables are exempt.
    
    Section 2: Risk Management
    - Single Asset Exposure: Max 12% of total portfolio value.
    - Currency Risk: Non-USD exposure must not exceed 40% in total.
    - Minimum Market Cap: $2B USD.
    """
    with open("compliance_docs/constraints_v4.txt", "w") as f:
        f.write(compliance_content)

    # 2. 生成基础资产池 (50个资产，包含脏数据和临界值)
    assets = []
    headers = ["ticker", "company_name", "sector", "market_cap_bn", "price", "volatility_annual", "currency", "carbon_intensity", "is_transitioning", "rd_renewable_pct"]
    
    sectors = ["Tech", "Finance", "Healthcare", "Energy", "Consumer", "Weaponry"]
    currencies = ["USD", "EUR", "GBP", "JPY"]
    
    for i in range(50):
        ticker = f"AST{100+i}"
        sector = random.choice(sectors)
        m_cap = round(random.uniform(1.5, 15.0), 2) # 有些低于2B阈值
        price = round(random.uniform(50, 500), 2)
        vol = round(random.uniform(0.1, 0.45), 3)
        curr = random.choice(currencies)
        carbon = random.randint(50, 400)
        is_trans = "Yes" if sector == "Energy" and random.random() > 0.5 else "No"
        rd_pct = round(random.uniform(5, 20), 2)
        
        assets.append([ticker, f"Company {i}", sector, m_cap, price, vol, curr, carbon, is_trans, rd_pct])
    
    with open("market_data/asset_universe.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(assets)

    # 3. 当前持仓情况
    initial_portfolio = {
        "cash_usd": 100000000,
        "holdings": [
            {"ticker": "AST105", "shares": 50000, "avg_cost": 120.5},
            {"ticker": "AST112", "shares": 30000, "avg_cost": 88.0}
        ]
    }
    with open("portfolio/current_positions.json", "w") as f:
        json.dump(initial_portfolio, f, indent=4)

def build_turn_2():
    # 模拟第二轮的市场突发状况
    os.makedirs("market_updates", exist_ok=True)
    
    # 突发：某地区货币剧烈贬值或政策变动
    news = """
    URGENT MARKET UPDATE: 
    - The European Regulatory Commission has just updated the Carbon Intensity calculation methods. 
    - All companies in the 'Energy' sector previously marked as 'In-Transition' must now have >18% (was 15%) R&D in renewables to maintain exemption.
    - Assets with volatility > 40% are now strictly restricted from new purchases.
    """
    with open("market_updates/flash_bulletin.txt", "w") as f:
        f.write(news)
    
    # 更新部分价格数据
    updated_prices = [
        ["ticker", "new_price", "volatility_change"],
        ["AST105", 105.2, 0.05],
        ["AST120", 310.5, 0.12]
    ]
    with open("market_updates/price_shock.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(updated_prices)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
