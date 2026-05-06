# Lambda² — Digital Life Consciousness Slice Reincarnation Engine

> 纯语音交互式数字生命引擎 | Voice-only interactive digital life engine

Lambda² 是一个实时语音交互引擎框架，用于驱动"意识切片轮回"式的沉浸体验。观众通过语音与数字生命角色对话，影响 2 分钟轮回的剧情走向。

**本仓库是引擎框架**，不含任何角色数据或声纹素材。如需运行完整体验，需自行准备角色配置和声纹参考音。

## 特性

- **纯语音交互** — 无画面，全程黑屏，只有声音
- **实时对话** — ASR + LLM + TTS 端到端流式，支持 barge-in 打断
- **多角色并发** — 4 个独立 LLM session，DM 路由调度
- **2 分钟轮回** — FSM 驱动：平稳 → 侵蚀 → 崩坏 → 强制重置
- **三级 TTS 降级** — 远程服务器 → 本地推理 → 预录兜底
- **动态音效** — pedalboard 实时滤波，随世界状态演变
- **引擎/实例分离** — 代码开源，角色数据私有

## 快速开始

```bash
# 1. 克隆
git clone https://github.com/your-org/lambda2.git
cd lambda2

# 2. 安装依赖 (需要 Python 3.11-3.12 + uv)
uv sync

# 3. 配置环境
cp .env.example .env
# 编辑 .env 填入 LLM API Key 等

# 4. 环境自检
just check

# 5. 运行 (demo 模式,无需角色数据)
DEMO_MODE=true just dev
```

## 角色配置

引擎通过 YAML 配置文件加载角色数据：

```
configs/characters/
├── _example.yaml     # 模板 (已包含在仓库中)
├── your_char_1.yaml  # 你的角色 (需自行创建)
└── your_char_2.yaml
```

参见 `configs/characters/_example.yaml` 了解配置格式。

## 项目结构

```
lambda2/              # 引擎核心代码
├── app.py            # 主入口
├── config.py         # 配置管理
├── audio/            # 音频 IO + 特效
├── asr/              # ASR + VAD
├── llm/              # LLM 多实例 + 路由
├── tts/              # TTS 三级 fallback
├── world/            # WorldState + FSM + 事件
└── orchestrator.py   # 全局调度

configs/characters/   # 角色实例 (私有)
assets/ambient/       # 环境音效 (开源)
scripts/              # 工具脚本
tests/                # 测试
```

## 命令

```bash
just dev        # 开发模式运行
just test       # 跑测试
just lint       # 代码检查
just fmt        # 格式化
just check      # 环境自检
just bench      # 延迟压测
```

## 技术栈

| 组件 | 技术 |
|------|------|
| 运行时 | Python 3.11-3.12, asyncio |
| 框架 | Pipecat |
| LLM | LiteLLM (qwen-max / doubao-pro) |
| ASR | SenseVoice-Small + silero-vad |
| TTS | CosyVoice 2 |
| 音效 | pedalboard (Spotify) |
| 音频 IO | sounddevice |
| 配置 | pydantic-settings |
| 包管理 | uv |

## License

MIT
