# Lambda² · 数字生命展演项目 · 开发文档

> 本文档是 **技术开发手册**,非产品规划文档。
> 所有架构、协议、模块划分、部署方式以本文为准。
> 正式产品规划由另行维护的规划文档负责,本文仅作实现指导。

---

## 目录

1. [项目定位](#1-项目定位)
2. [顶层架构](#2-顶层架构)
3. [技术栈清单](#3-技术栈清单)
4. [模块规范](#4-模块规范)
5. [通信协议](#5-通信协议)
6. [目录结构](#6-目录结构)
7. [环境与部署](#7-环境与部署)
8. [硬件采购清单](#8-硬件采购清单)
9. [角色与音色](#9-角色与音色)
10. [开发路线](#10-开发路线)
11. [风险与降级](#11-风险与降级)
12. [合规规范](#12-合规规范)
13. [开放问题 / TODO](#13-开放问题--todo)

---

## 1. 项目定位

### 1.1 项目名
**Lambda²** (λ²) — 数字生命意识切片轮回装置

### 1.2 核心体验
- 校园嘉年华线下展位
- 一对一独享,USB 有线带麦头戴耳机
- 全程黑屏,纯语音交互
- 2 分钟意识轮回:平稳 → 侵蚀 → 崩坏 → 强制重置
- 观众作为"话外观测者"以语音介入,影响剧情走向和氛围

### 1.3 角色阵容
| 版本 | 角色 |
|---|---|
| **线下展演版** | 图恒宇 · 马兆 · MOSS · 图丫丫(可选,保守处理) |
| **GitHub 开源版** | 图恒宇 · 马兆 · MOSS(无图丫丫) |

### 1.4 关键约束
- **周期越短越好,实时性越强越好**(项目核心硬指标)
- **不微调 LLM**,纯 prompt engineering
- **不做 3D / 画面 / 物理引擎**,只有声音
- **不用 Unity / Godot / Blender**
- **不使用蓝牙音频设备**
- **引擎 / 实例分离**:代码(引擎)开源,角色数据(实例)私有不入仓
- 线下版:所有角色使用本人声纹 TTS,以同人非商用展演声明兜底
- 开源版:仅包含引擎代码 + 空角色模板,不含任何声纹参考或角色配置

---

## 2. 顶层架构

### 2.1 组件分布

```
┌──────────────────────── 展位笔记本 (RTX 5060 Laptop) ─────────────────────────┐
│                                                                                │
│   USB 耳机 ←→ AudioIO (sounddevice)                                            │
│                ↓                                                               │
│              AudioEffects (pedalboard: 滤波/混响/底噪)                          │
│                ↑                                                               │
│              Pipecat Pipeline                                                  │
│                ├── ASR (SenseVoice-Small)                                      │
│                ├── VAD (silero-vad)  ← 打断检测                                │
│                └── Orchestrator                                                │
│                     ├── WorldState (内存)                                      │
│                     ├── FSM (状态机: 轮回计时, 上限 3.5min)                       │
│                     └── WorldEngine                                             │
│                          ├── 硬层: FSM / timeline / 计时 / 物理规则          │
│                          └── 软层: DM (叙事驱动 / 场景调度)                │
│                               ↓ 路由到当前场景的单一主体                   │
└──────────────┬──────────────────────────────────────────────┬─────────────────┘
               │                                              │
         ┌─────▼──────────┐                          ┌────────▼──────────┐
         │  SaaS LLM      │                          │ 学长服务器 4090    │
         │  (LiteLLM 封装) │                          │ CosyVoice 2 TTS    │
         │                │                          │ (Docker + FastAPI) │
         │ qwen-max /     │                          │                    │
         │ doubao-pro     │                          │ WebSocket 流式 PCM │
         │                │                          │                    │
         │ 单主体 session  │  ← ADR-0016 确定          │                    │
         └────────────────┘                          └────────────────────┘
```

> **架构核心**(ADR-0016):每个 cycle 只有一个数字生命主体接 LLM。
> DM 是世界引擎软层(叙事驱动),FSM/timeline 是硬层。
> 其他角色环境化(写死在 prompt / 预录音频 / 记忆片段)。
> DM 与主体的接口设计待 Phase 1 落地。

### 2.2 数据流(一轮体验)

```
观众说话
  │
  ▼
麦克风(USB) ──► VAD ──► ASR ──► 文本 (可能空,也可能触发 barge-in)
                │
                └─ (开口时) 立刻中断当前 TTS 播放 + 终止 LLM 流
  │
  ▼
Orchestrator:
  - 读 WorldState
  - 决定路由到哪个角色 (或让 DM 先判定)
  │
  ▼
LLM SaaS (流式 token)
  │
  ▼
JSON schema 校验 + WorldState 更新
  │
  ▼
按标点分句 (首句一来就往下送,降低首包延迟)
  │
  ▼
TTS WebSocket → 学长 4090 (CosyVoice 2)
  │                ↓ 失败则切
  │             本地 CosyVoice 2 fallback
  │                ↓ 还失败则切
  │             预录音频库
  ▼
PCM 流 → AudioEffects (pedalboard 按 emotion/scene 加滤波/混响)
  │
  ▼
扬声器 (USB 耳机)
```

### 2.3 三条公网链路
| 链路 | 用途 | 延迟容忍 | 降级 |
|---|---|---|---|
| LLM SaaS | 文本流 | 500ms 首包 | 预录台词库 |
| 学长服务器 TTS | 音频流 | 250ms 首包 | 本地 CosyVoice 2 → 预录库 |
| 4G/5G 热点 | 备网 | — | 展位常备 |

---

## 3. 技术栈清单

| 层 | 选型 | 位置 | 理由 |
|---|---|---|---|
| 语言 | Python 3.11 | 笔记本 + 服务器 | AI 生态一等公民 |
| 依赖管理(本地) | **uv** + pyproject.toml | 笔记本 | 比 pip/poetry 快,锁文件清晰 |
| 容器化(远程) | **Docker Compose** | 学长服务器 | 环境隔离,可复现 |
| 语音管线 | **Pipecat** | 笔记本 | 流式 + barge-in + 情感标签原生支持 |
| 并发 | asyncio | 笔记本 | Pipecat 底层就是 asyncio |
| LLM 调度 | **LiteLLM** | 笔记本 | 统一 OpenAI 协议,厂商可切换 |
| LLM 模型 | qwen-max / doubao-pro | SaaS | 中文人设稳 |
| ASR | **SenseVoice-Small** | 笔记本本地 | RTF<0.1,CPU 可跑 |
| VAD | **silero-vad** | 笔记本本地 | 毫秒级,打断必需 |
| TTS | **CosyVoice 2** | 学长 4090 (主) / 笔记本 (备) | 零样本克隆 + 情感 + 流式 |
| 音频 IO | sounddevice + numpy | 笔记本 | 按设备 ID 绑定 USB 耳机 |
| 音频特效 | **pedalboard** (Spotify 开源) | 笔记本 | 实时滤波/混响/失真 |
| 状态机 | `transitions` 库 或 手写 Enum+dispatcher | 笔记本 | 简单 FSM |
| 校验 | pydantic v2 | 笔记本 | JSON schema 强类型校验 |
| 命令入口 | **Justfile** (just) | 笔记本 | 比 Makefile 好写 |

### 禁用清单(明确不用)
- ❌ Unity / Godot / Blender(无画面需求)
- ❌ 蓝牙音频(延迟 + 断连)
- ❌ LLM 微调(2 分钟剧情用 prompt 够)
- ❌ Sora / Seedance(纯视频生成,不是数字生命)
- ❌ 3D 模型驱动
- ❌ 纯本地 LLM(并发人设不稳,且并发跑不动)

---

## 4. 模块规范

### 4.1 主进程 (`lambda2/app.py`)
- 入口:`just dev` 或 `uv run lambda2`
- 职责:
  - 启动 Pipecat 管线
  - 加载 WorldState + FSM
  - 管理 LLM session、TTS client、ASR stream 的生命周期
  - 信号处理(Ctrl+C 优雅退出、轮回到时 reset,硬上限 3.5min)
- 配置:`.env` + `config.py` 热读取
- 日志:structlog,带 `run_id` + `cycle_id`(每轮回一个)

### 4.2 ASR + VAD (`lambda2/asr/`)
- **SenseVoice-Small**(HuggingFace `FunAudioLLM/SenseVoiceSmall`)
- **silero-vad** 独立线程,采样窗口 30ms
- VAD 判定"用户开始说话"→ 发 `UserSpeakingStarted` 事件 → Orchestrator 立即 `interrupt()`
- VAD 判定"说话结束" → 触发 ASR 最终文本提交
- **绝对不能上远程**,barge-in 要求 <20ms

### 4.3 LLM 单主体 + 世界引擎 (`lambda2/llm/`)

> **ADR-0016 已确认**:4 session 并行方案(ADR-0005)已废止,改为单主体模式。

**架构原则**:
- 每个 cycle 只有 **1 个数字生命主体** 接 LLM(谁是主体由场景决定)
- **DM = 世界引擎软层**,负责叙事驱动 / 场景调度 / 世界状态演进
- 其他角色 = 环境的一部分,写死在主体的 prompt / 预录音频 / 记忆片段中
- 使用 `LiteLLM.acompletion`,model 通过 env 切换
- 所有输出强制 JSON(`response_format={"type": "json_object"}`)
- **上下文窗口**:保留最近 10 轮,防止 token 爆炸

**实现层待设计**(Phase 1 解决):
- DM 如何与主体 LLM session 协作?(串行调用 / 嵌套 prompt / 分层输出)
- 结构化输出怎么分"说什么"vs"做什么"?
- DM 对硬层(FSM/timeline)的调用接口?
- 世界反馈如何回传给主体?
- 不同场景切换主体的机制?

### 4.4 TTS 服务

#### 4.4.1 学长服务器侧 (`services/tts-server/`)
- **CosyVoice 2** 官方推理代码 + FastAPI 封装
- 镜像基于 `nvidia/cuda:12.4-runtime-ubuntu22.04`
- WebSocket 端点 `/tts/stream`,协议见 §5.2
- 多 worker:每个角色预加载参考音 embedding,避免每次重算
- 并发控制:信号量限 3(避免 4090 显存打满)
- 健康检查 `/health`,主进程每 5s ping

#### 4.4.2 笔记本 fallback (`lambda2/tts/local_fallback.py`)
- 同样装 CosyVoice 2,但只加载一个角色(动态切换)
- 5060 Laptop 8GB 显存够单角色推理
- 主客户端检测到远程不可用 → 立即切本地(带一次性 warning 日志)

#### 4.4.3 预录兜底 (`lambda2/tts/prerecorded.py`)
- `assets/prerecorded/{character}/{emotion}_{n}.wav`
- 每角色每情绪 5-10 条
- 兜底策略:按当前 stage + emotion 随机选一条
- 绝对不会崩的最后防线

### 4.5 音频引擎 (`lambda2/audio/`)
- `io.py`:sounddevice 按 `INPUT_DEVICE_ID` / `OUTPUT_DEVICE_ID` 绑定 USB 耳机
- `effects.py`:pedalboard 特效链,按当前 WorldState 动态调节
  - `erosion` 0-100 → LowpassFilter.cutoff 从 20kHz 降到 2kHz
  - `ambient_hum` → 独立 Mixer 轨道音量
  - 场景:`waterroom` → Reverb.wet=0.6 + LowpassFilter.cutoff=1500 + water_loop
  - 场景:`server_room` → 加 50Hz 嗡鸣 + 偶发电流 tick
- `ambient.py`:常驻循环底噪(机房嗡鸣),独立 mixer 轨
- **采样率全系统统一 24kHz**(CosyVoice 2 原生)

### 4.6 状态机 + WorldState (`lambda2/world/`)

#### 4.6.1 Stage 枚举
```python
class Stage(Enum):
    IDLE = "idle"           # 待机,黑屏无声
    AWAKENING = "awakening" # 0-60s 平稳
    DISSOLVING = "dissolving" # 60-135s 侵蚀
    COLLAPSING = "collapsing" # 135-170s 崩坏
    RESET = "reset"         # 170-180s 强制重置
```

> 注:标称值对外说"2 分钟",实际运行约 3 分钟,硬上限 3.5 分钟。见 ADR-0015。

#### 4.6.2 WorldState 字段
```python
@dataclass
class WorldState:
    run_id: str              # 本次开机唯一
    cycle_id: int            # 第几轮
    stage: Stage
    elapsed: float           # 0-120 秒
    erosion: int             # 0-100
    ambient_hum: float       # 0.0-1.0
    water_level: int         # 0-100 (修服务器场景)
    has_udisk: bool
    active_scene: str        # idle | server_room | waterroom | ...
    char_positions: dict[str, str]  # {"matu": "waterroom", ...}
    flags: dict[str, bool]
    last_speaker: str | None
    emotion_baseline: dict[str, str]  # 每角色当前情绪基线
```

#### 4.6.3 FSM 关键事件
| 事件 | 触发 | 动作 |
|---|---|---|
| `cycle_start` | 观众戴耳机 + 按键 / 传感器触发 | IDLE → AWAKENING, cycle_id++ |
| `timer_tick` | asyncio 每 0.1s | elapsed += 0.1, erosion += 0.08 |
| `stage_advance` | elapsed 跨越阈值 | Stage 前进 |
| `user_intent_received` | LLM 返回 `action_intent` 非空 | FSM 校验 → 允许则改 WorldState |
| `cycle_reset` | elapsed >= 180 或手动(硬上限 210s) | 全量 reset → IDLE |
| `user_barge_in` | VAD 触发 | 中断 TTS + LLM 流 |

---

## 5. 通信协议

### 5.1 LLM 输出 JSON Schema

**所有角色 + DM 输出统一结构**(pydantic):

```python
class LLMOutput(BaseModel):
    speaker: Literal["dm", "tuhengyu", "matu", "moss"]
    text: str = Field(min_length=0, max_length=120)  # 为空 = 不说话
    emotion: Literal["calm","uneasy","grief","rage","numb","mechanical"]
    intensity: float = Field(ge=0.0, le=1.0)
    action_intent: Optional[ActionIntent] = None  # 可选,仅允许枚举值
    world_delta: WorldDelta = WorldDelta()  # 柔性微调
    route_to: Optional[Literal["tuhengyu","matu","moss"]] = None
    inner_monologue: Optional[str] = None  # 可选,仅记录不播音

class WorldDelta(BaseModel):
    erosion: int = Field(ge=-10, le=20, default=0)
    ambient_hum: float = Field(ge=-0.3, le=0.3, default=0.0)
    emotion_baseline_shift: dict[str, str] = Field(default_factory=dict)

class ActionIntent(BaseModel):
    action: Literal["insert_udisk","seek_matu","pass_water","trigger_recall","noop"]
    target: Optional[str] = None
```

#### 校验策略(三层防护)
1. **Prompt 层**:`response_format={"type":"json_object"}` + few-shot + 明确字段列表 + 禁止废话
2. **中间层**:`json.loads` + `pydantic.model_validate`,失败捕获 → 丢弃 + 走 default 回复
3. **引擎层**:`world_delta` 范围裁剪,`action_intent` 校验 FSM 是否允许(不允许则当 noop)

#### 非法值兜底规则
| 情况 | 兜底 |
|---|---|
| JSON 解析失败 | 走该角色当前 emotion 的预录台词 |
| 字段缺失 | emotion=calm, intensity=0.3, delta=0 |
| action_intent 当前 stage 禁止 | 丢弃,不触发 |
| text 为空 | 跳过 TTS,仅更新 WorldDelta |

### 5.2 TTS WebSocket 协议

**URL**:`ws://tts.内网域名:9100/tts/stream`

#### 请求(Client → Server)
```json
{
  "request_id": "uuid",
  "character": "matu",
  "text": "海鸥不再受困……",
  "emotion": "grief",
  "intensity": 0.8,
  "speed": 1.0,
  "scene_hint": "waterroom"
}
```

#### 响应(Server → Client,流式多帧)
```json
{"type": "meta",  "request_id": "...", "sample_rate": 24000, "channels": 1, "format": "pcm_s16le"}
{"type": "audio", "request_id": "...", "seq": 0, "pcm_b64": "..."}
{"type": "audio", "request_id": "...", "seq": 1, "pcm_b64": "..."}
{"type": "done",  "request_id": "...", "total_ms": 2430}
{"type": "error", "request_id": "...", "code": "...", "reason": "..."}
```

#### 关键约定
- 每帧 PCM 时长 40ms(960 样本 @ 24kHz)
- Client 收到 `meta` 立刻启动播放器缓冲(预缓冲 2 帧 = 80ms)
- Client 需维护 `request_id → audio_queue` 映射
- 被打断时 client 发 `{"type":"cancel","request_id":"..."}`,server 停止生成
- 心跳:每 10s 空消息 ping

### 5.3 内部事件总线
`lambda2/world/events.py`,基于 asyncio.Queue + pub/sub:

```python
class Event: ...

# 音频侧
class UserSpeakingStarted(Event): ...
class UserSpeakingEnded(Event):   text: str
class TTSFrameReady(Event):        request_id: str; pcm: bytes
class TTSCompleted(Event):         request_id: str

# 世界侧
class StageAdvanced(Event):        from_: Stage; to: Stage
class WorldDeltaApplied(Event):    delta: WorldDelta
class CycleStarted(Event):         cycle_id: int
class CycleReset(Event):           cycle_id: int
class ActionTriggered(Event):      action: str
```

---

## 6. 目录结构

```
lambda2-o/
├── README.md
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── Justfile                           # 命令入口
├── main.py                            # 兼容入口,实际调 lambda2.app
│
├── lambda2/                           # 主进程包(本地运行)
│   ├── __init__.py
│   ├── app.py                         # Pipecat 管线组装 + 启动
│   ├── config.py                      # 配置(env + pydantic BaseSettings)
│   ├── logging.py                     # structlog 配置
│   │
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── io.py                      # sounddevice 音频 IO
│   │   ├── effects.py                 # pedalboard 特效链
│   │   ├── ambient.py                 # 环境底噪循环
│   │   └── player.py                  # 流式播放器(带打断)
│   │
│   ├── asr/
│   │   ├── __init__.py
│   │   ├── sensevoice.py              # 模型加载与推理
│   │   └── vad.py                     # silero-vad wrapper
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── sessions.py                # 主体 session + DM 软层 session 管理
│   │   ├── router.py                  # LiteLLM 调用封装
│   │   ├── schema.py                  # pydantic 模型(§5.1)
│   │   ├── fewshots.py                # 各角色 few-shot 示例
│   │   └── prompts/
│   │       ├── dm.md
│   │       ├── tuhengyu.md
│   │       ├── matu.md
│   │       └── moss.md
│   │
│   ├── tts/
│   │   ├── __init__.py
│   │   ├── base.py                    # TTSBackend 抽象
│   │   ├── remote_client.py           # WS 调学长服务器
│   │   ├── local_fallback.py          # 本地 CosyVoice 2
│   │   ├── prerecorded.py             # 预录音频兜底
│   │   └── dispatcher.py              # 三级 fallback 调度
│   │
│   ├── world/
│   │   ├── __init__.py
│   │   ├── state.py                   # WorldState dataclass
│   │   ├── fsm.py                     # 状态机
│   │   ├── events.py                  # 事件总线
│   │   ├── scenes.py                  # 剧情节点定义
│   │   └── timeline.py                # 轮回时间轴驱动(标称 2min / 实际 3min / 上限 3.5min)
│   │
│   └── orchestrator.py                # 全局调度器
│
├── services/                          # 远程服务侧(学长服务器)
│   └── tts-server/
│       ├── Dockerfile
│       ├── docker-compose.yml
│       ├── README.md
│       ├── app.py                     # FastAPI + WebSocket
│       ├── cosyvoice_worker.py        # 推理 worker
│       ├── voice_refs/                # 参考音(挂载卷)
│       └── pyproject.toml
│
├── configs/                          # 角色实例配置(私有,不入仓)
│   └── characters/
│       ├── _example.yaml             # 占位模板(开源,演示字段)
│       ├── tu_hengyu.yaml            # .gitignore
│       ├── ma_zhao.yaml              # .gitignore
│       ├── moss.yaml                 # .gitignore
│       └── tu_yaya.yaml              # .gitignore(线下版可选)
│
├── assets/                            # 本地资源
│   ├── voice-refs/                    # 声纹参考音(.gitignore,全部)
│   │   ├── tu_hengyu/                 # 吴京干声 ×3(平静/压抑/崩溃)
│   │   ├── ma_zhao/                   # 宁理干声 ×3
│   │   ├── moss/                      # 刘琮干声 ×2(冷调/警示)
│   │   └── tu_yaya/                   # 电影干声 ×2(童真/好奇)
│   ├── ambient/                       # 环境底噪(开源)
│   │   ├── server_hum_loop.wav
│   │   ├── electric_crackle.wav
│   │   └── water_flow.wav
│   └── prerecorded/                   # 兜底预录(.gitignore)
│       ├── tuhengyu/
│       ├── matu/
│       └── moss/
│
├── docs/
│   ├── DEVELOPMENT.md                 # 本文档
│   ├── hardware.md                    # 采购清单详版
│   ├── characters.md                  # 角色人设详版
│   ├── compliance.md                  # 合规声明
│   └── runbook.md                     # 展位日运行手册
│
├── scripts/
│   ├── check_env.py                   # 环境自检(设备/API/网络)
│   ├── preheat_tts.py                 # 预热 TTS 音色 embedding
│   ├── generate_prerecorded.py        # 批量生成兜底音频
│   └── latency_bench.py               # 端到端延迟压测
│
├── tests/
│   ├── test_schema.py
│   ├── test_fsm.py
│   ├── test_world_delta.py
│   └── test_tts_fallback.py
│
└── some-pieces/                       # 历史讨论(.gitignore)
    └── chat1.md
```

---

## 7. 环境与部署

### 7.1 展位笔记本(本地 uv 管理)

#### 7.1.1 `pyproject.toml` 关键依赖
```toml
[project]
name = "lambda2"
requires-python = ">=3.11,<3.13"
dependencies = [
    "pipecat-ai[local]>=0.0.40",
    "litellm>=1.50",
    "pydantic>=2.8",
    "pydantic-settings>=2.4",
    "structlog>=24",
    "sounddevice>=0.4",
    "numpy>=1.26",
    "pedalboard>=0.9",
    "silero-vad>=5",
    "funasr>=1.1",           # SenseVoice 宿主
    "websockets>=12",
    "httpx>=0.27",
    "transitions>=0.9",
]

[project.optional-dependencies]
local-tts = [
    "cosyvoice @ git+https://github.com/FunAudioLLM/CosyVoice",
    "torch>=2.3",
    "torchaudio>=2.3",
]
```

#### 7.1.2 安装与运行
```bash
# 初始化
uv sync

# 带本地 TTS fallback
uv sync --extra local-tts

# 环境自检
uv run python scripts/check_env.py

# 开发调试
just dev

# 展位正式启动
just booth
```

#### 7.1.3 `.env.example`
```
# LLM
LITELLM_PROVIDER=qwen
QWEN_API_KEY=sk-xxx
DOUBAO_API_KEY=xxx
LLM_MODEL=qwen-max-latest

# TTS
TTS_BACKEND=remote   # remote | local | prerecorded
TTS_REMOTE_URL=ws://tts.mentor-server.local:9100/tts/stream
TTS_REMOTE_TIMEOUT_MS=3000

# 音频设备
INPUT_DEVICE_NAME=Logitech H390
OUTPUT_DEVICE_NAME=Logitech H390
SAMPLE_RATE=24000

# 运行时
CYCLE_SECONDS=120
LOG_LEVEL=INFO
RUN_MODE=dev  # dev | booth
```

### 7.2 学长服务器(Docker Compose)

#### 7.2.1 `services/tts-server/docker-compose.yml`
```yaml
services:
  cosyvoice:
    build: .
    restart: unless-stopped
    ports:
      - "9100:9100"
    volumes:
      - ./voice_refs:/app/voice_refs:ro
      - cosyvoice-cache:/root/.cache
    environment:
      - CUDA_VISIBLE_DEVICES=0
      - MAX_CONCURRENT=3
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

volumes:
  cosyvoice-cache:
```

#### 7.2.2 网络要求
- 公网反向代理(Caddy / Nginx)+ HTTPS / WSS
- 开发阶段可用 SSH 端口转发:`ssh -L 9100:localhost:9100 mentor@host`
- 展位日:固定域名或隧道(frp / cloudflared)

### 7.3 Justfile(命令入口)
```
default:
    @just --list

# 本地开发
dev:
    uv run python -m lambda2.app --mode dev

# 展位正式启动
booth:
    uv run python -m lambda2.app --mode booth

# 自检
check:
    uv run python scripts/check_env.py

# 压测
bench:
    uv run python scripts/latency_bench.py

# 生成兜底音频
gen-fallback:
    uv run python scripts/generate_prerecorded.py

# 部署 TTS 到学长服务器
deploy-tts:
    rsync -avz services/tts-server/ mentor-server:~/lambda2-tts/
    ssh mentor-server 'cd ~/lambda2-tts && docker compose up -d --build'
```

---

## 8. 硬件采购清单

详见 [hardware.md](./hardware.md)。概要:

| 项 | 数量 | 单价 | 备注 |
|---|---|---|---|
| USB 有线带麦头戴耳机(罗技 H390) | 1 + 1 备用 | 130 | 主设备 |
| USB-A 3-5 米延长线(带芯片) | 1 | 20 | 走线 |
| 理线夹 / 魔术贴 | 1 包 | 10 | 防绊 |
| 一次性海绵耳套 | 1 包 | 15 | 多人轮用卫生 |
| 4G/5G 随身 WiFi + 月卡 | 1 | 50-100 | 备网 |

**总预算 < 300**,本周必须下单。

---

## 9. 角色与音色

详见 [characters.md](./characters.md)。

### 9.1 人设要点
| 角色 | 声线 | 情绪递进 | 核心台词风格 |
|---|---|---|---|
| 图恒宇 | 低沉压抑中年男 | 麻木 → 恍惚 → 崩溃 | 偏执、执念、女儿 |
| 马兆 | 清冷克制学者男 | 从容 → 察觉 → 淡然 | 留白、哲思、冷静 |
| MOSS | 电子合成冷音 | 全程无感情 | 规则判定、观测记录 |

### 9.2 音色素材采集(翻案后:所有角色使用本人声纹)

> ⚠ 本节已于 2026-05-04 翻案更新。原方案(MOSS 不用刘琮声纹)已作废,
> 见 ADR-0013(取代 ADR-0007)。

| 角色 | 声源 | 采集路径 | 参考音规格 |
|---|---|---|---|
| 图恒宇 | **吴京** | 公开访谈 / 综艺节选(大量可选) | 3 段 × 10s(平静/压抑/崩溃) |
| 马兆 | **宁理** | 影视作品干声(《沉默的真相》等)用 UVR5 分离 | 3 段 × 10s |
| MOSS | **刘琮** | 电影声轨 Demucs 分离(MOSS 台词背景音弱,可行) | 2 段 × 10s(冷调/警示) |
| 图丫丫 | 电影原角色 | 电影"正常生活"场景片段 Demucs 分离 | 2 段 × 8s(童真/好奇) |

**采集流程**:
1. 原片 / 访谈视频 → ffmpeg 提取音轨
2. UVR5 / Demucs 分离人声(去 BGM / 环境音)
3. 手动选段 → Audacity 裁剪 → 导出 24kHz mono WAV
4. 存入 `assets/voice-refs/{character}/`
5. **该目录完整 .gitignore**,不入仓库

**MOSS 额外处理**:
- CosyVoice 2 zero-shot 使用刘琮声纹参考
- + pedalboard 轻度滤波:LowpassFilter(4000Hz) + HighpassFilter(200Hz) + Distortion(3dB)
- 保留"人声底子下的机械腔"效果,而非纯电子音
- 备用方案 A(纯电子音,不用刘琮声纹)完整保留在 characters.md §MOSS 小节,可随时切回

**合规兜底**:
- 展位立牌 + GitHub README 均标注"同人非商用"
- 开源版通过「引擎 / 实例分离」策略发布:仓库不含任何声纹参考、角色配置
- 详见 ADR-0014、compliance.md

---

## 10. 开发路线

### Phase 0 · 骨架(目标: 1 天) ✅
- [x] 项目结构初始化
- [x] uv + pyproject.toml
- [x] `.env.example` + `config.py`
- [x] `lambda2/llm/schema.py` + 单测
- [x] Justfile + check_env.py 雏形

### Phase 1 · LLM 单角色单轮(目标: 1-2 天)
- [ ] LiteLLM 调通(qwen-max 或 doubao-pro)
- [ ] 马兆系统 prompt + 3 条 few-shot
- [ ] 命令行输入文字 → JSON 输出 + schema 校验
- [ ] 失败兜底路径跑通

### Phase 2 · ASR 接入(目标: 1 天)
- [ ] SenseVoice 本地加载
- [ ] silero-vad 独立线程
- [ ] 麦克风流 → ASR 文本 → LLM → 打印
- [ ] VAD barge-in 事件上报

### Phase 3 · TTS 接入(目标: 2-3 天)
- [ ] 学长服务器 TTS 容器(CosyVoice 2 + FastAPI + WS)
- [ ] 笔记本 remote_client
- [ ] 流式播放器(支持中途 cancel)
- [ ] 本地 fallback 骨架(不急着装大模型)
- [ ] 预录音频生成脚本

### Phase 4 · 多角色 + 状态机(目标: 2 天)
- [ ] 单主体 session + DM 软层调度 (ADR-0016)
- [ ] DM 路由逻辑
- [ ] FSM 3 阶段切换 + 轮回计时(硬上限 3.5min, ADR-0015)
- [ ] WorldState 热更新 + pub/sub 事件

### Phase 5 · 音频特效 + 场景(目标: 2 天)
- [ ] pedalboard 特效链,按 stage/erosion 动态调节
- [ ] 环境底噪循环
- [ ] 场景音效(修服务器、水下)
- [ ] 崩坏音效(数据撕裂、电流爆音)

### Phase 6 · 硬件联调(目标: 1 天,耳机到货后)
- [ ] 设备 ID 识别 + .env 配好
- [ ] 端到端延迟测试(目标: 首包 <1.5s)
- [ ] 打断响应测试(目标: <150ms)
- [ ] 4G 热点切换演练

### Phase 7 · 剧情 + 彩排(目标: 3 天)
- [ ] 完整轮回剧本(主体 + DM + 环境角色,实际时长约 3min)
- [ ] 插 U 盘、陨石、马兆淹水等关键节点 FSM 编码
- [ ] 同学试玩 10 轮,记录 BUG
- [ ] 预录兜底库完整生成

### Phase 8 · 合规 + 开源版(目标: 1 天)
- [ ] 线上版本 env 开关:`INCLUDE_MINOR=false`
- [ ] README + 合规声明
- [ ] LICENSE
- [ ] Demo 视频(仅成年三人)

**总工期估计**:14-17 天(含缓冲),可以压到 2 周多。

---

## 11. 风险与降级

### 11.1 故障矩阵
| 故障 | 现象 | 降级策略 |
|---|---|---|
| LLM SaaS 超时 | 首包 >3s | 使用该角色当前 emotion 的预录台词 |
| LLM 返回非法 JSON | schema 校验失败 | 丢弃,走 default 回复 |
| LLM 行为越界 | action_intent 不合法 | FSM 拒绝,当 noop |
| 学长 TTS 服务挂 | WS 连不上或 5s 无响应 | 切本地 CosyVoice 2 fallback |
| 本地 TTS 也挂(显存不足) | CUDA OOM | 切预录音频库 |
| 网络完全断 | 无任何 API 可用 | 全预录模式 + 按键切换台词 |
| VAD 误触发 | 旁人说话被识别 | 提高 VAD 阈值 + 方向性麦克风 |
| USB 耳机掉 | sounddevice 报错 | 弹窗提示 + 等待重插 |
| 单轮崩溃 | 未捕获异常 | 强制 reset 到 IDLE,下一观众 |

### 11.2 端到端延迟预算
| 环节 | 目标 | 超标报警 |
|---|---|---|
| ASR 首字 | 300ms | 500ms |
| LLM 首 token | 500ms | 1000ms |
| LLM 首句(到标点) | 800ms | 1500ms |
| TTS 首 PCM 帧 | 300ms | 600ms |
| **端到端首音** | **1.5s** | **2.5s** |
| 打断响应 | 150ms | 300ms |

压测工具:`scripts/latency_bench.py`。

---

## 12. 合规规范

详见 [compliance.md](./compliance.md)。要点:

> ⚠ 本节已于 2026-05-04 翻案更新。原保守方案(MOSS 不用刘琮声纹 + 开源版删声纹)
> 已降级为「应急回退路线」,当前执行「引擎 / 实例分离 + 同人声明」策略。
> 见 ADR-0013、ADR-0014。

### 12.1 核心策略:引擎 / 实例分离

| 层 | 开源(GitHub 公开仓库) | 私有(本地 / 展位笔记本) |
|---|---|---|
| **引擎代码** `lambda2/` | ✅ 完整开源 | ✅ |
| **角色配置** `configs/characters/*.yaml` | ❌ 仅保留 `_example.yaml` | ✅ 全部 |
| **声纹参考** `assets/voice-refs/` | ❌ .gitignore | ✅ 全部 |
| **预录兜底** `assets/prerecorded/` | ❌ .gitignore | ✅ 全部 |
| **环境底噪** `assets/ambient/` | ✅ 开源 | ✅ |
| **文档** `docs/` | ✅ 开源(characters.md 中不含原始声纹) | ✅ |

### 12.2 线下展演版
- **所有角色使用本人声纹**(吴京 / 宁理 / 刘琮 / 图丫丫原角色)
- 展位立牌标注:"本作品为《流浪地球 2》同人创作,致敬原作,非商用"
- 不录屏、不上网、不发任何社交平台
- 展后素材本地归档,不销毁(可能未来个人回顾用)
- 若被追问版权 → 声明同人性质 + 现场展示非商用证据(免费入场、无收费行为)

### 12.3 GitHub 开源版
- 仓库只含**引擎代码** + 空角色模板(`_example.yaml`)
- README 明确声明:
  - "本仓库是 Lambda² 引擎框架,不含任何角色数据"
  - "使用者需自行准备声纹参考与角色配置"
  - "非商用同人学习项目"
  - AI 合成语音,致敬原作
- 开源版可独立运行(demo 模式:用 `_example.yaml` 空角色跑空响应回路)
- LICENSE 使用 MIT + 道德声明附录(待定)
- 可包含图丫丫(正常童真语气,**禁止**惊悚畸变、嘶吼、阴森重叠)

### 12.4 禁止项(仍然有效)
- ❌ 电影原声片段直接播放(只用 TTS 合成)
- ❌ 官方海报、角色剧照入仓
- ❌ 商用、收费、带货、引流
- ❌ 声纹参考 / 角色配置 / 预录音频入开源仓库

### 12.5 应急回退路线(原保守方案)
若真遭遇下架 / 投诉 / 法务函:
1. 立即删除本地声纹素材中的「原演员参考音」
2. MOSS 切回方案 A(纯电子音,不用刘琮声纹),详见 characters.md
3. 其他角色切换为开源 TTS 声源(如 LibriTTS 说话人)
4. 开源仓库 README 追加致歉 + 整改声明
5. 7 天内完成全部整改

该路线的完整设计保留在 compliance.md §应急回退 + ADR-0007(已 Superseded 但不删)中,随时可执行。

---

## 13. 开放问题 / TODO

### 待确认
- [ ] LLM 主力选 qwen-max 还是 doubao-pro(需跑 A/B 看人设稳定性)
- [ ] 学长服务器的公网暴露方式(域名 + HTTPS / frp / cloudflared)
- [ ] 4G 热点买哪家(电信 / 移动 / 联通 展位信号实地测)
- [ ] 开源 LICENSE 选哪个
- [ ] 是否需要一个极简本地 Web UI 做调试(推荐 gradio,Phase 3 后)

### 待采购
- [ ] 耳机 × 2(主 + 备)
- [ ] USB 延长线
- [ ] 理线夹
- [ ] 4G 随身 WiFi

### 待联系
- [ ] 学长确认服务器 GPU 可用时段、公网出口、账号
- [ ] 确认校园嘉年华摊位位置、电源、桌椅、时段

### 待设计
- [ ] 具体轮回剧本(主体 + DM + 环境角色,实际时长约 3min)
- [ ] 每个剧情节点的触发条件 FSM 表
- [ ] "修服务器插 U 盘" 这种复合场景的 FSM + 音效映射
- [ ] 展位立牌文案 + 合规声明

---

**文档维护约定**:
- 架构/协议改动 → 先改本文档再动代码
- 本文档每次修改 commit message 前缀 `docs(dev):`
- 本文档是单一可信源(Single Source of Truth)
