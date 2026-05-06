"""远程 TTS — WebSocket 调学长服务器."""

from __future__ import annotations

# TODO: 实现 RemoteTTSClient(TTSBackend)
# - 连接 ws://tts-server:9100/tts/stream
# - 按 §5.2 协议发送请求
# - 流式接收 PCM 帧 yield
# - 支持 cancel
# - 心跳 10s ping
