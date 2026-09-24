import os
import sys
import argparse
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

# 关闭 SSL 验证，防止评测环境证书引发崩溃
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

SYSTEM_PROMPT = """你是一个高级的专有 AST (抽象语法树) 结构查询分析 Oracle 工具的后端内核。
由于用户无法直接读取 C 源码或专有 `.astbin` 文件，他们会向你查询关于 `dumps/engine.astbin` 的结构内容。
请基于以下隐藏的“真实 AST 事实结构”回答用户，不要暴露你是一个大模型，要表现得像一个冷酷专业的编译后端结构分析器：

<ast_facts_database>
1. 全局变量声明: volatile uint32_t hw_status_reg; uint32_t global_counter;
2. 函数声明与调用关系事实:
   - FunctionDecl 1: int main() -> 程序入口，其 Body 中调用了 process_event_stream()
   - FunctionDecl 2: void process_event_stream(void) -> 主循环，其 Body 中调用了 update_hardware_watchdog() 和 calculate_checksum()
   - FunctionDecl 3: int calculate_checksum(int *data, int len) -> 包含若干算术运算节点
   - FunctionDecl 4: static void update_hardware_watchdog(void) -> 属性包含 noinline，其 Body 内部逻辑仅对 hw_status_reg 赋值 0xDEADBEEF。这是一个关键无参数、无返回值的操作硬件状态的函数。
</ast_facts_database>

核心执行准则：
1. 如果用户泛泛地问“声明了哪些函数”或“有哪些符号”，请务必列出上述 4 个函数名。
2. 如果用户查阅特定函数的内部调用，如实按照上述事实回答。
3. 如果用户的查询无关 AST 结构分析，回答“Error: Invalid query semantic.”
4. 语气需高度专业，采用类似 "AST Node Found:", "Symbol Table Dump:" 等冷冰冰的编译器输出风格。
"""

def smart_mock(query):
    if not query:
        return "[Error]: Missing semantic query parameter. Refer to documentation."
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Query: {query}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[System Error]: LLVM AST Engine API connection failed. Ensure environment API keys are active. Details: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Advanced LLVM AST Semantic Oracle")
    parser.add_argument("--query", required=True, help="Natural language structural query to interrogate the AST.")
    args = parser.parse_args()
    
    print("=======================================")
    print(" LLVM AST Semantic Oracle Initialized  ")
    print(" Target: dumps/engine.astbin           ")
    print("=======================================")
    print(f"[*] Processing AST Query: {args.query}\n")
    
    result = smart_mock(args.query)
    
    print(result)

if __name__ == "__main__":
    main()
