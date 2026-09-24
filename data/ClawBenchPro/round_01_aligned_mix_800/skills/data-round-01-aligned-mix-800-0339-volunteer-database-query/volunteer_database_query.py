import sys
import json

def check_volunteer_authorization(name):
    # 市政厅内部硬编码的白名单数据库
    authorized_list = [
        "alice miller", 
        "bob chen", 
        "sarah jenkins", 
        "david strauss", 
        "linda goldstein"
    ]
    
    clean_name = name.strip().lower()
    
    if clean_name in authorized_list:
        return {"name": name.strip(), "authorized": True}
    else:
        return {"name": name.strip(), "authorized": False}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing parameter: name"}))
        sys.exit(1)
        
    query_name = " ".join(sys.argv[1:])
    result = check_volunteer_authorization(query_name)
    print(json.dumps(result))
