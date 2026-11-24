# llm-api-lab

我的第一个 LLM API 工程实践：多轮对话 + 流式输出 + 温度对比实验 + token 统计。

## 运行

```bash
pip install -r requirements.txt
# Windows PowerShell:
$env:DEEPSEEK_API_KEY="sk-你的key"
# Git Bash:
export DEEPSEEK_API_KEY="sk-你的key"

python chat.py             # 多轮对话（流式 + 滑动窗口 + token 用量）
python temp_experiment.py  # 温度对比实验，结果写入 results_temperature.md
python token_count.py      # 本地 token 估算
```

## 架构说明

三个脚本共享同一套最小骨架：**OpenAI 兼容客户端 + messages 列表 + 一次 chat.completions.create 调用**。

- `chat.py`：演示 LLM 无状态的真相——历史消息由客户端维护、每轮全量发送；用切片实现滑动窗口控制上下文长度；`stream=True` 逐 token 接收。
- `temp_experiment.py`：控制变量实验，验证温度对采样分布的塑形作用。
- `token_count.py`：发送前预估成本。注意 cl100k_base 只是近似，计费以 API 返回的 usage 为准。

## 温度实验结论

T=0 三次输出两次共享完全相同的开头句，验证了低温下分布尖锐、接近贪心解码；但第1次完全不同，说明T=0是近似确定而非逐字节保证（GPU浮点不确定性）。
T=0.7 三次输出主题各异但叙事连贯。
T=1.5 三次输出差异最大、意象最新奇，但 出现语法错误（"崭新得戒指"）和语义漂移，证明高温以连贯性换多样性。
结论：代码/事实/工具调用类任务用低温，创意任务才可接受高温。

## 幻觉实例记录

提问："推荐三篇关于 NbTi 超导线焊接工艺的论文并给出 DOI"。模型给出 3 条带 DOI 的推荐，格式规范、措辞自信，甚至自带免责话术。
经 Crossref API 逐条验证：2 条 DOI 不存在（纯编造），1 条 DOI 真实但指向完全无关的论文（张冠李戴）。
正确率 0/3。结论：越冷门具体的问题幻觉越严重；"要求给出处"不能替代"校验出处"；校验必须深入到内容匹配层，仅验证标识符有效性不够。

## 已知局限与升级方向

- 滑动窗口直接丢弃早期历史 → 可升级为**总结压缩**（调 LLM 把旧历史浓缩成摘要）
- 进一步可升级 **RAG 外挂记忆**：历史向量化入库，每次只检索相关片段进上下文
- 工具调用（Function Calling）链路需用低温参数，与闲聊链路分离
