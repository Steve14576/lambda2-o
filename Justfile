# Lambda² Justfile
# 使用: just <command>
# 安装 just: cargo install just / brew install just / scoop install just

set dotenv-load

# 默认: 显示帮助
default:
    @just --list

# ===== 开发 =====

# 启动开发模式(DEV_MODE=true)
dev:
    uv run lambda2

# 启动生产模式
run:
    uv run lambda2

# ===== 环境 =====

# 安装依赖
setup:
    uv sync
    @echo "✓ 依赖安装完成"

# 环境自检
check:
    uv run python scripts/check_env.py

# ===== 质量 =====

# lint
lint:
    uv run ruff check lambda2/ tests/

# format
fmt:
    uv run ruff format lambda2/ tests/

# 测试
test:
    uv run pytest

# ===== TTS 工具 =====

# 预热 TTS embedding
preheat:
    uv run python scripts/preheat_tts.py

# 生成兜底预录音频
prerecord:
    uv run python scripts/generate_prerecorded.py

# 延迟压测
bench:
    uv run python scripts/latency_bench.py
