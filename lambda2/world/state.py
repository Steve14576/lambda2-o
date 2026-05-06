"""WorldState dataclass — 全局运行时状态."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Stage(Enum):
    """2 分钟轮回阶段."""

    IDLE = "idle"  # 待机,黑屏无声
    AWAKENING = "awakening"  # 0-40s 平稳
    DISSOLVING = "dissolving"  # 40-90s 侵蚀
    COLLAPSING = "collapsing"  # 90-115s 崩坏
    RESET = "reset"  # 115-120s 强制重置


@dataclass
class WorldState:
    """全局世界状态 — 单实例,所有模块共享."""

    run_id: str = ""  # 本次开机唯一
    cycle_id: int = 0  # 第几轮
    stage: Stage = Stage.IDLE
    elapsed: float = 0.0  # 0-120 秒
    erosion: int = 0  # 0-100
    ambient_hum: float = 0.0  # 0.0-1.0
    water_level: int = 0  # 0-100
    has_udisk: bool = False
    active_scene: str = "idle"  # idle | server_room | waterroom | ...
    char_positions: dict[str, str] = field(default_factory=dict)
    flags: dict[str, bool] = field(default_factory=dict)
    last_speaker: str | None = None
    emotion_baseline: dict[str, str] = field(default_factory=dict)

    def reset(self) -> None:
        """重置为新轮回初始状态."""
        self.cycle_id += 1
        self.stage = Stage.AWAKENING
        self.elapsed = 0.0
        self.erosion = 0
        self.ambient_hum = 0.0
        self.water_level = 0
        self.has_udisk = False
        self.active_scene = "server_room"
        self.char_positions = {}
        self.flags = {}
        self.last_speaker = None
        self.emotion_baseline = {
            "tuhengyu": "calm",
            "matu": "calm",
            "moss": "mechanical",
        }
