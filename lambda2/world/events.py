"""事件总线 — asyncio.Queue + pub/sub."""

from __future__ import annotations

from dataclasses import dataclass

from lambda2.world.state import Stage


# ===== 基类 =====

@dataclass
class Event:
    """事件基类."""
    pass


# ===== 音频侧 =====

@dataclass
class UserSpeakingStarted(Event):
    """VAD 检测到用户开始说话."""
    pass


@dataclass
class UserSpeakingEnded(Event):
    """VAD 检测到用户说完,ASR 产出最终文本."""
    text: str = ""


@dataclass
class TTSFrameReady(Event):
    """TTS 产出一帧 PCM."""
    request_id: str = ""
    pcm: bytes = b""


@dataclass
class TTSCompleted(Event):
    """TTS 生成完毕."""
    request_id: str = ""


# ===== 世界侧 =====

@dataclass
class StageAdvanced(Event):
    """Stage 前进."""
    from_: Stage = Stage.IDLE
    to: Stage = Stage.IDLE


@dataclass
class WorldDeltaApplied(Event):
    """WorldDelta 已应用."""
    pass


@dataclass
class CycleStarted(Event):
    """新轮回开始."""
    cycle_id: int = 0


@dataclass
class CycleReset(Event):
    """轮回重置."""
    cycle_id: int = 0


@dataclass
class ActionTriggered(Event):
    """动作触发."""
    action: str = ""
