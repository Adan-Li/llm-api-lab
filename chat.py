"""
chat.py — 多轮对话 demo
演示三件事：
1. LLM 无状态：历史消息存在我们自己维护的列表里，每次全量发给 API
2. 滑动窗口：历史超过 MAX_HISTORY 条就砍掉最旧的，防止上下文爆炸
3. 流式输出（SSE）：逐 token 接收并打印，模拟真实聊天产品的体验
"""
import os
from openai import OpenAI

# 一个 OpenAI 兼容客户端 = 任意厂商的 API 入口
# 换厂商只需要改 base_url 和 api_key，代码一行不动
client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],  # key 从环境变量读，绝不写死在代码里
    base_url="https://api.deepseek.com",
)

MODEL = "deepseek-chat"
MAX_HISTORY = 10  # 滑动窗口：最多保留最近 10 条消息（5 轮对话）


def build_messages(history):
    """组装请求体：system 提示词永远在 + 最近 N 条历史"""
    system = [{"role": "system", "content": "你是一个简洁的编程学习助手。"}]
    return system + history[-MAX_HISTORY:]  # 切片 = 滑动窗口的全部实现


def chat_stream(messages):
    """发一次请求，流式接收回复，返回 (完整回复文本, token 用量)"""
    stream = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
        stream=True,                            # 打开 SSE 流式
        stream_options={"include_usage": True}, # 流式模式下要求最后返回 token 统计
    )
    reply = ""
    usage = None
    for chunk in stream:  # 每收到一小段就打印，不等全部生成完
        if chunk.choices and chunk.choices[0].delta.content:
            piece = chunk.choices[0].delta.content
            print(piece, end="", flush=True)
            reply += piece
        if chunk.usage:  # usage 在最后一个 chunk 里
            usage = chunk.usage
    print()  # 流式打印完后补个换行
    return reply, usage


def main():
    history = []  # 多轮对话的全部记忆就这一个列表 —— 模型本身什么都记不住
    print("输入 exit 退出")
    while True:
        user_input = input("\n你: ").strip()
        if user_input in ("exit", "quit"):
            break
        if not user_input:
            continue

        history.append({"role": "user", "content": user_input})
        print("AI: ", end="")
        reply, usage = chat_stream(build_messages(history))
        history.append({"role": "assistant", "content": reply})

        if usage:
            print(f"[tokens] 输入 {usage.prompt_tokens} + "
                  f"输出 {usage.completion_tokens} = 总计 {usage.total_tokens}")


if __name__ == "__main__":
    main()
