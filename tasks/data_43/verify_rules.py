import os
import json
import xml.etree.ElementTree as ET

def verify():
    results = {
        "restock_xml_exists": False,
        "restock_xml_correct_count": 0,
        "report_exists": False,
        "data_accuracy_score": 0,
        "errors": []
    }

    xml_path = "restock_order.xml"
    report_path = "report.txt"

    # 1. 检查 XML
    if os.path.exists(xml_path):
        results["restock_xml_exists"] = True
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            # 预期：MH-001 (20->150), MH-002 (-15+40=25->150), MH-004 (10->150), MH-006 (-5+15=10->150)
            # 都是 Apparel 且修复后库存均 < 50
            skus = [item.find('SKU').text for item in root.findall('SKU/..')]
            expected_skus = ["MH-001", "MH-002", "MH-004", "MH-006"]
            if set(skus) == set(expected_skus):
                results["data_accuracy_score"] += 50
                
            # 检查订购数量计算 (例如 MH-001 应订购 130)
            for item in root:
                if item.find('SKU').text == "MH-001":
                    if int(item.find('Order_Quantity').text) == 130:
                        results["data_accuracy_score"] += 10
        except Exception as e:
            results["errors"].append(f"XML parsing error: {str(e)}")

    # 2. 检查 Report 内容是否反映了修复逻辑
    if os.path.exists(report_path):
        results["report_exists"] = True
        with open(report_path, 'r') as f:
            content = f.read().lower()
            if "2" in content and "price" in content: # 修复了 MH-001 和 MH-004 的价格
                results["data_accuracy_score"] += 20
            if "2" in content and "inventory" in content or "negative" in content: # 处理了 2 个负库存
                results["data_accuracy_score"] += 20

    with open("verify_result.json", "w") as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    verify()
