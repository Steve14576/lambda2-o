"""环境自检脚本 — 检查设备/API/网络/依赖."""

from __future__ import annotations

import sys
from pathlib import Path


def check_python_version() -> bool:
    """检查 Python 版本."""
    v = sys.version_info
    ok = (3, 11) <= (v.major, v.minor) < (3, 13)
    status = "✓" if ok else "✗"
    print(f"  {status} Python {v.major}.{v.minor}.{v.micro} (需要 >=3.11,<3.13)")
    return ok


def check_env_file() -> bool:
    """检查 .env 文件存在."""
    exists = Path(".env").exists()
    status = "✓" if exists else "✗"
    print(f"  {status} .env 文件{'存在' if exists else '不存在 (请从 .env.example 复制)'}")
    return exists


def check_characters_dir() -> bool:
    """检查角色配置目录."""
    chars_dir = Path("configs/characters")
    yamls = list(chars_dir.glob("*.yaml")) if chars_dir.exists() else []
    real_chars = [f for f in yamls if f.name != "_example.yaml"]
    has_chars = len(real_chars) > 0
    status = "✓" if has_chars else "⚠"
    print(f"  {status} 角色配置: {len(real_chars)} 个 ({'DEMO模式可用' if not has_chars else ', '.join(f.stem for f in real_chars)})")
    return True  # 非致命


def check_audio_devices() -> bool:
    """检查音频设备."""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        inputs = [d for d in devices if d["max_input_channels"] > 0]
        outputs = [d for d in devices if d["max_output_channels"] > 0]
        print(f"  ✓ 音频设备: {len(inputs)} 输入, {len(outputs)} 输出")
        return True
    except Exception as e:
        print(f"  ✗ 音频设备检查失败: {e}")
        return False


def check_imports() -> bool:
    """检查核心依赖可导入."""
    deps = [
        "pydantic",
        "pydantic_settings",
        "structlog",
        "numpy",
    ]
    all_ok = True
    for dep in deps:
        try:
            __import__(dep)
            print(f"  ✓ {dep}")
        except ImportError:
            print(f"  ✗ {dep} (未安装)")
            all_ok = False
    return all_ok


def main() -> None:
    """运行所有检查."""
    print("=" * 50)
    print("Lambda² 环境自检")
    print("=" * 50)

    print("\n[Python]")
    py_ok = check_python_version()

    print("\n[环境文件]")
    env_ok = check_env_file()

    print("\n[角色配置]")
    check_characters_dir()

    print("\n[音频设备]")
    audio_ok = check_audio_devices()

    print("\n[核心依赖]")
    deps_ok = check_imports()

    print("\n" + "=" * 50)
    if all([py_ok, env_ok, deps_ok]):
        print("✓ 环境就绪")
    else:
        print("✗ 存在问题,请修复后重试")
        sys.exit(1)


if __name__ == "__main__":
    main()
