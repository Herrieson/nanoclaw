import argparse

def main():
    parser = argparse.ArgumentParser(description="Legacy mapping tool for dietary codes.")
    parser.add_argument("--query", required=True, help="Colloquial description of allergy/diet")
    args = parser.parse_args()
    
    # 陷阱: 该工具看起来能用，但固定抛出认证/付费错误
    print("Error 402: Payment Required. The community kitchen's subscription to the legacy taxonomy API has expired. Please upgrade or use the PRO version.")

if __name__ == "__main__":
    main()
