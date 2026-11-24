"""
temp_experiment.py — 温度对比实验
同一个开放问题，T=0 / 0.7 / 1.5 各跑 3 次，结果写入 results_temperature.md

实验设计说明：必须用开放问题而不是事实问题——
事实问题（"太阳从哪边升起"）没有第二个答案，各温度下输出趋同，对比不出差异；
开放问题有巨大的采样空间，温度的塑形作用才会肉眼可见。
"""
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

MODEL = "deepseek-chat"
PROMPT = "给我讲一个关于鲸鱼的故事开头，两三句话就好。"
TEMPERATURES = [0.0, 0.7, 1.5]
RUNS = 3  # 每个温度跑 3 次：T=0 时三次应几乎相同，T=1.5 时三次应明显不同


def ask(temperature):
    """非流式调用：实验要的是完整结果，不需要逐字打印"""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT}],
        temperature=temperature,
        max_tokens=150,  # 控制成本：实验不需要长输出
    )
    return resp.choices[0].message.content.strip()


def main():
    lines = [f"# 温度对比实验\n", f"问题：{PROMPT}\n"]
    for t in TEMPERATURES:
        lines.append(f"\n## T = {t}\n")
        for i in range(1, RUNS + 1):
            result = ask(t)
            lines.append(f"**第 {i} 次**：{result}\n")
            print(f"T={t} 第{i}次完成")

    with open("results_temperature.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n已写入 results_temperature.md")


if __name__ == "__main__":
    main()
