"""Lambda² 主入口 — Pipecat 管线组装与启动."""

from __future__ import annotations

import asyncio
import signal
import sys

import structlog

from lambda2.config import Settings

logger = structlog.get_logger()


async def _run() -> None:
    """启动 Pipecat 管线."""
    settings = Settings()  # type: ignore[call-arg]
    logger.info("lambda2.starting", mode="demo" if settings.demo_mode else "normal")

    # TODO: 组装 Pipecat pipeline
    # TODO: 加载 WorldState + FSM
    # TODO: 启动 ASR/TTS/LLM sessions
    logger.info("lambda2.ready", dev_mode=settings.dev_mode)

    # 保持运行直到收到终止信号
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except NotImplementedError:
            # Windows 不支持 add_signal_handler
            pass

    await stop.wait()
    logger.info("lambda2.shutdown")


def main() -> None:
    """CLI 入口点."""
    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
