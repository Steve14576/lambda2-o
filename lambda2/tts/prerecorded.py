"""预录音频兜底 — 最后防线."""

from __future__ import annotations

# TODO: 实现 PrerecordedFallback(TTSBackend)
# - 从 assets/prerecorded/{character}/{emotion}_{n}.wav 加载
# - 按当前 stage + emotion 随机选一条
# - 每角色每情绪 5-10 条
