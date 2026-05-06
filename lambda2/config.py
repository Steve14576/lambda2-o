"""应用配置 — 基于 pydantic-settings,从 .env 读取."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Lambda² 全局配置."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    llm_provider: str = "openai"
    llm_model: str = "qwen-max"
    llm_api_key: str = ""
    llm_base_url: str = ""

    # TTS 远程
    tts_remote_url: str = "ws://localhost:9100/tts/stream"
    tts_remote_timeout_ms: int = 5000

    # 音频设备
    input_device_id: str = ""
    output_device_id: str = ""

    # 角色配置
    characters_dir: str = "configs/characters"

    # 调试
    log_level: str = "INFO"
    dev_mode: bool = False
    demo_mode: bool = False
