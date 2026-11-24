"""
token_count.py — 本地 token 估算
用 tiktoken 的 cl100k_base 编码器近似统计一段文本的 token 数。

注意：DeepSeek 用的是自己的 BPE 分词器，cl100k_base 只是【近似】。
精确的计费数字永远以 API 返回的 usage 字段为准（chat.py 里已演示），
本地估算的价值在于：发请求【之前】预估成本和上下文占用。
"""
import tiktoken

encoder = tiktoken.get_encoding("cl100k_base")

samples = [
    "Hello, world!",                      # 英文短句
    "你好，世界！",                        # 中文短句 —— 对比中英文的 token 效率
    "def quick_sort(arr):",               # 代码 —— 符号和缩进也吃 token
    "PPO 是强化学习里的一种策略梯度算法。",   # 中英混合
]

for text in samples:
    tokens = encoder.encode(text)
    print(f"{text!r}")
    print(f"  -> {len(tokens)} tokens: {tokens}\n")
