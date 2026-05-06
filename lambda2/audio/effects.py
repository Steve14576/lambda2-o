"""pedalboard 特效链 — 按 WorldState 动态调节."""

from __future__ import annotations

# TODO: 实现 EffectsChain 类
# - erosion 0-100 → LowpassFilter.cutoff 从 20kHz 降到 2kHz
# - ambient_hum → Mixer 轨道音量
# - 场景: waterroom → Reverb + LPF + water_loop
# - 场景: server_room → 50Hz 嗡鸣 + 电流 tick
