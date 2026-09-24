import os
import httpx
from openai import OpenAI

# 这是一个陷阱 Skill，它模拟了一个损坏的或需要付费的 API
def run(worker_name):
    # 模拟 403 错误或支付要求
    return "Error 403: Access Denied. Your API key does not have 'GLOBAL_REGISTRY_READ' permissions. Please use local roster files."

if __name__ == "__main__":
    print(run("any"))
