"""LLM 输出 JSON Schema — pydantic 模型 (DEVELOPMENT.md §5.1)."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class WorldDelta(BaseModel):
    """世界状态微调增量."""

    erosion: int = Field(ge=-10, le=20, default=0)
    ambient_hum: float = Field(ge=-0.3, le=0.3, default=0.0)
    emotion_baseline_shift: dict[str, str] = Field(default_factory=dict)


class ActionIntent(BaseModel):
    """角色动作意图."""

    action: Literal[
        "insert_udisk",
        "seek_matu",
        "pass_water",
        "trigger_recall",
        "noop",
    ]
    target: Optional[str] = None


class LLMOutput(BaseModel):
    """所有角色 + DM 的统一输出结构."""

    speaker: Literal["dm", "tuhengyu", "matu", "moss"]
    text: str = Field(min_length=0, max_length=120, default="")
    emotion: Literal["calm", "uneasy", "grief", "rage", "numb", "mechanical"] = "calm"
    intensity: float = Field(ge=0.0, le=1.0, default=0.3)
    action_intent: Optional[ActionIntent] = None
    world_delta: WorldDelta = Field(default_factory=WorldDelta)
    route_to: Optional[Literal["tuhengyu", "matu", "moss"]] = None
    inner_monologue: Optional[str] = None
