"""4 个独立 LLM session 管理."""

from __future__ import annotations

# TODO: 实现 ChatSession / SessionManager
# - 4 个独立 messages 列表 (dm, tuhengyu, matu, moss)
# - 上下文窗口: 每 session 保留最近 10 轮
# - 系统提示词从 prompts/*.md 加载
