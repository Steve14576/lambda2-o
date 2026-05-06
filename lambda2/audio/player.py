"""流式播放器 — 带打断支持."""

from __future__ import annotations

# TODO: 实现 StreamPlayer
# - 从 audio_queue 取 PCM 帧播放
# - 支持 interrupt() 即刻静音清队列
# - 预缓冲 2 帧 (80ms @ 24kHz)
