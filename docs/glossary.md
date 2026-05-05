# Lambda² · 术语表 (Glossary)

> 项目涉及 4 个领域的术语(电影世界观 / 语音 AI / 音频工程 / 软件工程),
> 名词冲突和歧义风险高(比如"state"在 FSM / PyTorch / Redux 各有含义)。
> 本术语表是**统一口径**,代码注释 / prompt / 文档中出现任何术语冲突以本表为准。
>
> 条目按**类别**分组,组内按首字母排序。

---

## 0. 项目专属术语

#### WorldState
项目内部的"世界状态",一个 Python dataclass,包含 `stage`、`elapsed`、`erosion`、`has_udisk` 等字段。**单一可信源**,所有模块读这一份。参考 [DEVELOPMENT.md §4.6.2](./DEVELOPMENT.md#462-worldstate-字段)。

#### Stage(阶段)
2 分钟轮回的四个大段:`IDLE / AWAKENING / DISSOLVING / COLLAPSING / RESET`。由 FSM 驱动,按 elapsed 阈值推进。不同 Stage 影响情绪基线、音频滤波、MOSS 发言频率。

#### Cycle(轮回)
**一次完整的 2 分钟体验**,从 `cycle_start` 到 `cycle_reset`。每位观众 = 一个 cycle。`cycle_id` 单调递增,展位当天的编号。

#### Run
**一次主进程启动**,从开机到关机。`run_id` 为 uuid,一个 run 包含多个 cycle。日志以 `run_id` + `cycle_id` 双索引。

#### Erosion(侵蚀率)
0-100 的整数,表示当前数字意识的"数据侵蚀程度"。由 FSM 按时间自然增长,也可被 LLM 的 `world_delta.erosion` 微调。直接映射到音频滤波强度和 MOSS 警告频率。

#### Ambient Hum(环境嗡鸣)
机房底噪的音量系数 0.0-1.0。WorldState 字段,驱动 `ambient.py` 的 mixer 轨音量。LLM 可通过 `world_delta.ambient_hum` 在 ±0.3 内微调。

#### DM(Dungeon Master)
**非玩家调度器 session**。一个独立的 LLM session,**不出声**,只负责:路由下一轮谁说话、下发情绪基线、微调 world_delta。参考 [characters.md §7](./characters.md#7-dm非玩家调度器)。

#### Route(路由)
DM 决定下一轮由谁开口。具体通过返回 JSON 的 `route_to` 字段实现,枚举值 `tuhengyu / matu / moss / null`。

#### Action Intent(动作意图)
LLM 输出的结构化意图,如 `insert_udisk`、`pass_water`、`trigger_recall`。必须经过 FSM 校验后才会真正改变 WorldState,**不允许 LLM 直接改状态**。

#### World Delta(世界增量)
LLM 输出的"柔性参数微调",包含 `erosion`、`ambient_hum`、`emotion_baseline_shift`。LLM 能通过它影响世界观感,但不能直接触发硬节点(U 盘/陨石/重置)。

#### Barge-in
用户在 TTS 播放时开口说话 → 系统立即打断当前 TTS 和 LLM 流,转去识别用户输入。**本项目的核心交互体验**,决定沉浸感。

#### Degradation Ladder(降级梯)
TTS 三级降级链:远程(学长服务器)→ 本地 fallback(CosyVoice 2 本地)→ 预录音频库。由 `tts/dispatcher.py` 自动调度。

---

## 1. 电影世界观术语

#### 550W
电影《流浪地球 2》中出现的量子计算机,数字生命存储载体。项目里沿用此名作为"场景背景",不做正式产品命名。

#### MOSS
550W 的人工智能守护者,电影中由刘琮配音。本项目里作为**观测者/判定者**,语气绝对机械。**不使用刘琮原声**(见 ADR-0007)。

#### UEG
United Earth Government,联合政府。仅作为世界观提及,不出现在对话。

#### 数字生命(Digital Life)
电影核心概念 —— 将人类意识数字化保存。本项目就围绕这一设定展开。

#### 意识切片
项目原创概念,不是电影原作用词。指"2 分钟的意识片段",是本项目的基本单位。

#### 图恒宇 / 马兆 / 图丫丫
电影角色,参考 [characters.md](./characters.md)。

---

## 2. 语音 AI 术语

#### ASR (Automatic Speech Recognition)
自动语音识别,麦克风波形 → 文本。本项目使用 **SenseVoice-Small**(阿里开源)。

#### TTS (Text-to-Speech)
文本到语音合成,文本 → 音频波形。本项目使用 **CosyVoice 2**(阿里开源)。

#### VAD (Voice Activity Detection)
语音活动检测,判断"当前帧是否有人说话"。本项目使用 **silero-vad**。barge-in 的前置条件。

#### LLM (Large Language Model)
大语言模型。本项目使用 qwen-max / doubao-pro 等 SaaS API。

#### SaaS (Software as a Service)
软件即服务,这里特指"按 API 调用付费的云端模型服务"。

#### Pipecat
专注**实时语音 agent** 的 Python 框架,原生支持 ASR → LLM → TTS 流式管线 + VAD barge-in。主进程核心骨架。

#### LiteLLM
LLM 调用统一层,用 OpenAI 协议封装所有主流厂商(OpenAI / Anthropic / Qwen / Doubao / DeepSeek 等)。本项目用它做厂商切换。

#### CosyVoice 2
阿里开源 TTS 模型,支持零样本音色克隆 + 7 档情绪 + 流式生成。是本项目 TTS 方案。

#### SenseVoice-Small
阿里开源 ASR 模型,极轻量(CPU 可跑),RTF < 0.1,支持多语种。本项目 ASR 方案。

#### silero-vad
开源 VAD 模型,基于小型神经网络,毫秒级响应。本项目 VAD 方案。

#### Zero-shot Voice Cloning
零样本音色克隆:给 TTS 模型一段 5-15 秒参考音,就能用该音色合成任意文本。CosyVoice 2 的核心能力。

#### Prompt Engineering
提示词工程。通过精心设计系统提示 + few-shot 示例 + 格式约束来**不微调地**控制 LLM 行为。本项目的 LLM 方法论(见 ADR-0002)。

#### Few-shot
在 prompt 中给 LLM 几个(通常 2-5 个)输入输出示例,让它按例子格式生成。比起零样本,大幅提升一致性。

#### System Prompt / User Prompt / Assistant Prompt
LLM messages 结构中的三种角色:
- system:人设/规则
- user:对话输入
- assistant:模型回复(或 few-shot 例子中的"应该回什么")

#### JSON Mode / Structured Output
LLM 厂商提供的"强制输出 JSON"模式。本项目所有角色输出强制 JSON schema。

#### RTF (Real Time Factor)
实时因子,`处理音频的耗时 / 音频时长`。RTF < 1 表示能实时处理,越小越快。SenseVoice-Small RTF ~0.1 意味着处理 10 秒音频只要 1 秒。

#### TTFB (Time To First Byte / First Audio)
**首包延迟**,从请求发出到收到第一帧音频的时间。本项目目标 < 300ms(TTS)/ < 500ms(LLM)。

#### Token
LLM 计费和窗口的最小单位,中文约 1.5 字/token,英文约 0.75 词/token。

#### Context Window
LLM 一次调用能处理的最大 token 数。qwen-max ~128K。本项目每 session 只保留最近 10 轮,token 数可控。

---

## 3. 音频工程术语

#### PCM (Pulse-Code Modulation)
数字音频最原始的编码格式,不压缩。本项目内部音频流统一用 `pcm_s16le`(16bit signed little-endian)。

#### WAV
PCM + 头信息的容器格式。参考音 / 预录音频用 `.wav`。

#### Sample Rate(采样率)
每秒采样点数。本项目**全系统统一 24kHz**(CosyVoice 2 原生)。

#### Mono / Stereo(单/立体声)
单声道 / 双声道。本项目 TTS 输出为 mono,音频特效阶段可临时扩展为 stereo 做声像。

#### Lowpass Filter(低通滤波器)
滤掉高频,保留低频。听感:"闷"、"从水里传来"、"电话里"。本项目用它模拟数据侵蚀。

#### Highpass Filter(高通滤波器)
滤掉低频,保留高频。听感:"薄"、"金属感"。用于 MOSS 合成音的后处理。

#### Reverb(混响)
模拟空间反射。wet 越大越像在大空间。本项目用 `wet=0.6` 模拟水下 / 大机房。

#### Distortion(失真)
非线性处理,听感"破"、"电流"、"崩坏"。本项目在 COLLAPSING 期加入。

#### Pan / Panning(声像)
左右声道的音量差,决定声源在立体声空间中的位置。本项目可通过 pan 实现"马兆在左边、图恒宇在右边"。

#### Mixer(混音器)
多轨音频叠加模块。本项目的 AudioEngine 用 mixer 叠加:主人声轨 + 环境底噪轨 + 偶发音效轨。

#### pedalboard
Spotify 开源的实时音频特效 Python 库,本项目音频引擎核心。

#### Buffer / Frame / Chunk
音频处理的单位:
- **sample**:一个采样点(单个 int16)
- **frame**:某时刻所有声道的一组 sample(mono = 1 sample,stereo = 2 sample)
- **chunk/buffer**:多个 frame 组成的块,本项目通常 40ms = 960 frames @ 24kHz

#### Latency(延迟)
从声源触发到听到的时间。音频项目命脉指标。

---

## 4. 软件工程术语

#### FSM (Finite State Machine)
有限状态机。本项目用来管 Stage 推进和硬节点触发。使用 `transitions` 库或手写。

#### Pub/Sub
发布订阅模式。本项目内部用 `asyncio.Queue` 实现的事件总线(`lambda2/world/events.py`)。

#### asyncio
Python 内置异步框架。Pipecat 底层就是 asyncio。本项目所有 IO 操作走 async。

#### WebSocket
全双工网络协议,本项目用它连笔记本与学长 TTS 服务,流式传输音频帧。

#### FastAPI
Python Web 框架,学长服务器 TTS 服务用它暴露 WebSocket 端点。

#### pydantic
Python 数据校验库 v2。本项目用它定义 LLM 输出 JSON schema 并强校验。

#### structlog
Python 结构化日志库,支持 key-value 日志便于后续索引。

#### Docker / Docker Compose
容器化技术。本项目学长服务器端用 Docker Compose 管理 TTS 服务(见 ADR-0008)。

#### uv
Rust 写的 Python 包管理器,比 pip/poetry 快 10-100 倍。本项目展位笔记本端用它(见 ADR-0008)。

#### Justfile / just
Makefile 的现代替代品,比 Makefile 简洁。本项目命令入口。

#### ADR (Architecture Decision Record)
架构决策记录,见 [adr.md](./adr.md)。

#### Post-Mortem
复盘报告,通常在重大事件(如展位日、线上事故)后写。

#### RTF / TTFB / Latency
见 §2 语音 AI 术语。

---

## 5. 合规 / 法律术语

#### 同人创作 (Fan Work / Derivative Work)
基于已有作品(电影/小说/游戏)创作的衍生作品。国内外对非商用同人创作多采取默许态度,但**不等于"合法授权"**。

#### 非商用 (Non-commercial)
不以盈利为目的,不收费、不接广告、不带货。本项目严格非商用。

#### DMCA (Digital Millennium Copyright Act)
美国数字千年版权法,GitHub 响应版权投诉的法律基础。收到 DMCA takedown 必须在时限内响应。

#### LICENSE
开源项目的法律许可协议。常见:MIT、Apache 2.0、GPL、AGPL、CC BY-NC。参考 [compliance.md §3.3](./compliance.md#33-license-选型讨论)。

#### 声纹 (Voiceprint)
一个人声音的独特特征,类似指纹。AI 克隆声纹有肖像权 / 表演者权争议。

#### 零样本克隆风险
即使 "zero-shot" 合成看起来不需要训练数据,但参考音仍然是真人声纹,合成结果依然可能侵权。本项目对 MOSS 专门规避(ADR-0007)。

---

## 6. 常见缩写速查

| 缩写 | 全称 | 中文 |
|---|---|---|
| ADR | Architecture Decision Record | 架构决策记录 |
| ASR | Automatic Speech Recognition | 语音识别 |
| DM | Dungeon Master | 调度器(借用) |
| FSM | Finite State Machine | 有限状态机 |
| LLM | Large Language Model | 大语言模型 |
| PCM | Pulse-Code Modulation | 脉冲编码调制 |
| PRD | Product Requirements Doc | 产品需求文档 |
| p95 | 95th Percentile | 95 百分位(延迟指标) |
| RTF | Real Time Factor | 实时因子 |
| SaaS | Software as a Service | 软件即服务 |
| TTS | Text-to-Speech | 语音合成 |
| TTFB | Time To First Byte | 首字节/包延迟 |
| UEG | United Earth Government | 联合政府(电影) |
| VAD | Voice Activity Detection | 语音活动检测 |
| WS | WebSocket | — |

---

## 7. 本项目不使用的术语(避免混淆)

| 看似相关但本项目不用 | 原因 |
|---|---|
| Agent / Multi-agent | 容易和 AutoGen/LangGraph 的"agent 框架"混淆,本项目用"session"替代 |
| RAG | 本项目不做检索增强,剧情全在 prompt/FSM 里 |
| Fine-tune / SFT / LoRA | 见 ADR-0002,明确禁用 |
| Embedding / Vector DB | 本项目无需语义检索 |
| Diarization(说话人分离) | 只有一个观众,无需分离 |
| Tool Calling / Function Calling | 本项目不让 LLM 调工具,改为 JSON 输出 + 引擎解析 |
| Streaming LLM 的 "thinking" / reasoning token | 一般模型即可,不依赖 reasoning |

---

## 更新约定

- 新增术语 → 写入对应类别 + 更新本表
- 改动术语定义 → 先在 PR / commit message 标注 `glossary:`
- 术语冲突 → 本表为权威,代码注释对齐本表
