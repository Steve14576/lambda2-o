"""TTS 三级 fallback 调度器."""

from __future__ import annotations

# TODO: 实现 TTSDispatcher
# - Level 1: RemoteTTSClient (学长服务器)
# - Level 2: LocalTTSFallback (本地 5060)
# - Level 3: PrerecordedFallback (预录兜底)
# - 自动降级: 远程超时/异常 → 本地 → 预录
# - 健康检查 /health ping 每 5s
