"""TTSBackend 抽象基类."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator


class TTSBackend(ABC):
    """TTS 后端抽象 — 所有实现必须提供流式 PCM 输出."""

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        character: str,
        emotion: str = "calm",
        intensity: float = 0.5,
    ) -> AsyncIterator[bytes]:
        """流式生成 PCM 音频帧 (24kHz, mono, s16le, 40ms/帧)."""
        ...

    @abstractmethod
    async def cancel(self, request_id: str) -> None:
        """取消正在生成的请求."""
        ...
