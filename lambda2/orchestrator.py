"""全局调度器 — 串联 ASR/LLM/TTS/FSM."""

from __future__ import annotations

# TODO: 实现 Orchestrator
# - 监听事件总线
# - UserSpeakingEnded → 路由到 LLM
# - LLMOutput → 路由到 TTS
# - TTSFrameReady → 路由到 Player
# - 打断处理: UserSpeakingStarted → cancel TTS + LLM
