"""silero-vad wrapper — 独立线程,30ms 采样窗口."""

from __future__ import annotations

# TODO: 实现 VADDetector
# - silero-vad 模型加载
# - 30ms 窗口检测
# - 发出 UserSpeakingStarted / UserSpeakingEnded 事件
# - barge-in 延迟 < 20ms
