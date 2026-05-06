# Lambda² · 架构决策记录 (ADR)

> ADR = Architecture Decision Record
>
> 本文档记录项目所有**重要且不可轻易回滚**的技术决策,
> 每个决策独立编号,按时间顺序追加,**过往决策不删不改**。
>
> 未来要推翻某个决策?新增一条 ADR,标记 `Supersedes: ADR-XXXX`。

---

## 格式约定

每个 ADR 使用以下模板:

```markdown
## ADR-XXXX · 决策标题
**Status**: Proposed | Accepted | Superseded by ADR-YYYY | Deprecated
**Date**: YYYY-MM-DD
**Context**: 为什么要做这个决策?面临什么问题?
**Decision**: 决定了什么?
**Consequences**: 这个决策的好处和代价。
**Alternatives considered**: 否决了什么方案,为什么否决。
```

单人项目,每条 30-60 行即可,不写过度。

---

## 索引

| # | 标题 | Status |
|---|---|---|
| 0001 | 放弃 Godot,主干使用纯 Python | Accepted |
| 0002 | LLM 全部走 SaaS,不做微调 | Accepted |
| 0003 | TTS 主力部署在学长 RTX 4090 服务器 | Accepted |
| 0004 | 硬件 = USB 有线带麦头戴耳机 × 1 位,弃座机弃蓝牙 | Accepted |
| 0005 | LLM 采用 4 个独立 session 架构 | **Superseded by ADR-0016** |
| 0006 | 主进程 + ASR + VAD 必须在展位笔记本本地 | Accepted |
| 0007 | MOSS 不使用刘琮声纹,纯电子合成 | **Superseded by ADR-0013** |
| 0008 | 本地用 uv 管依赖,远程服务用 Docker Compose | Accepted |
| 0009 | 观众语音不录制、不存储、不上传 | Accepted |
| 0010 | 角色引擎统一 + 实例化配置 | Accepted |
| 0011 | 特性插件化与 Feature Flag 约定 | Accepted |
| 0012 | 项目定位为非商业同人作品,沿用原片人物名 | Accepted |
| 0013 | 所有角色使用本人声纹 TTS + 同人声明兜底 | Accepted (Supersedes 0007) |
| 0014 | 开源发布采用引擎 / 实例分离策略 | Accepted |
| 0015 | 轮回时长参数三层定义:标称 2min / 实际 3min / 上限 3.5min | Accepted |
| 0016 | 世界引擎软硬分离 + 数字生命单主体模式 | Accepted (Supersedes 0005) |

---

## ADR-0001 · 放弃 Godot,主干使用纯 Python
**Status**: Accepted
**Date**: 项目初期

**Context**:
原本讨论过 Unity / Godot + Python 混合栈(Godot 跑"硬骨架",Python 跑 LLM/TTS)。
但随着项目形态收敛到 **全黑屏 + 纯语音 + 2 分钟切片**,Godot 的渲染/物理/UI/60 帧主循环**全用不上**,唯一剩的是 FSM 和事件调度 —— 这两个用 Python 原生实现反而更轻。
同时 AI 生态(Pipecat / LiteLLM / funasr / CosyVoice / pedalboard)**全部在 Python**,跨语言通信会多一层故障点。

**Decision**:
项目主干语言 = **Python 3.11+**,彻底不引入 Godot / Unity / Unreal / Blender。

**Consequences**:
- ✅ 依赖栈统一,开发/调试/部署都简单
- ✅ AI 生态一等公民,无 FFI / 跨进程损耗
- ✅ 单人可 hold 住的复杂度
- ⚠️ 如果未来想加可视化(调试面板/展位监控屏),需要用 Gradio/Streamlit/Web 额外加
- ⚠️ 失去引擎原生物理模拟(但本项目不需要真实物理)

**Alternatives considered**:
- **Godot + Python hybrid**:用 Godot FSM + GDScript 事件,再跨语言调 Python LLM。否决理由:多一层故障点,Godot 的 60Hz 主循环对黑屏项目是浪费
- **Unity + ML-Agents**:C# 学习成本 + AI 生态弱,直接否决
- **Rust + tokio**:性能最好但 AI 库生态远不如 Python,单人工期压力下不划算

---

## ADR-0002 · LLM 全部走 SaaS,不做微调
**Status**: Accepted
**Date**: 项目初期

**Context**:
项目角色数 4(DM + 图恒宇 + 马兆 + MOSS),每个角色在 2 分钟内最多说 10-20 句。
自部署开源 LLM(Qwen 14B/72B / DeepSeek)在学长 A100 上可行,但:
- 多 session 并发加显存压力
- 人设稳定性不如闭源大模型
- 需要运维(模型托管/OOM/版本)

微调可以进一步锁人设,但:
- 需要构造高质量 SFT 数据集(单人 2 周做不出来)
- 需要微调 + 托管 + 版本管理
- 2 分钟剧情的"跑偏"用 prompt + JSON schema + 引擎层兜底已经足够

**Decision**:
- LLM 使用 SaaS 厂商(**qwen-max-latest** 主 + **doubao-pro** 备)
- 通过 **LiteLLM** 统一调度,方便厂商切换
- **不做任何微调**,纯 prompt engineering + few-shot + JSON schema 强校验

**Consequences**:
- ✅ 运维成本几乎为零
- ✅ 模型能力随厂商迭代自动升级
- ✅ 一天成本估算 ¥10-20,可接受
- ⚠️ 依赖公网,需 4G 热点备网
- ⚠️ 厂商 API 留存条款不可控(但本项目观众语音在本地已 ASR 为脱敏文本)

**Alternatives considered**:
- **本地部署 Qwen 72B + LoRA 微调**:否决,工期不够 + 运维负担 + 效果不一定好
- **使用 ChatGPT-4o API**:否决,中文人设稳定性不如通义千问/豆包,且境外 API 合规不稳

---

## ADR-0003 · TTS 主力部署在学长 RTX 4090 服务器
**Status**: Accepted
**Date**: 项目初期

**Context**:
展位笔记本为 RTX 5060 Laptop(8GB 显存)。CosyVoice 2 单角色推理**刚好够**,但:
- 多角色并发时显存吃紧
- 主进程 + ASR 也占资源
- 首包延迟能压到 250-300ms,已达体验下限

学长服务器空闲资源丰富(2× 4090 + Pro 6000 + 2× A100),4090 跑 CosyVoice 2 首包可压到 80-150ms,多角色并发无压力。

**Decision**:
- TTS 主力 = **学长服务器 4090**,CosyVoice 2 + FastAPI + WebSocket 流式
- 展位笔记本保留**本地 fallback**(CosyVoice 2 单角色动态加载)
- 进一步保底 = **预录音频库**
- 三级降级:remote → local → prerecorded

**Consequences**:
- ✅ 首包延迟最低,体验最好
- ✅ 多角色并发不争显存
- ✅ 本地 fallback 保证断网也能演
- ⚠️ 新增一条公网依赖,需 WSS/frp 等公网暴露方案
- ⚠️ 学长侧可用性(重启/断电)是新风险点,靠 fallback 化解

**Alternatives considered**:
- **全本地 TTS**:否决,5060 显存不够多角色并发
- **SaaS TTS**(MiniMax/火山声音复刻):否决,需企业资质 + 音色克隆审核麻烦 + 价格波动
- **主力 SaaS TTS + 本地 fallback**:否决,反向,SaaS 延迟不如学长专属 4090

---

## ADR-0004 · 硬件 = USB 有线带麦头戴耳机 × 1 位,弃座机弃蓝牙
**Status**: Accepted
**Date**: 项目初期

**Context**:
早期考虑过 2010 款老式连体座机改装(沉浸感好)、多人耳机位、蓝牙方案。各自问题:
- **座机**:改装成本 + 小喇叭音质差 + 多人轮用卫生差 + 内置麦收音差
- **蓝牙耳机**:延迟 100-300ms 毁掉 barge-in 体验 + 配对麻烦 + 多设备串流地狱
- **多耳机位**:等于多路 ASR/LLM/TTS 并发,显存/工程复杂度翻倍;且破坏"孤独意识切片"主题

**Decision**:
- 硬件 = **USB 有线带麦头戴耳机 × 1 位**(罗技 H390 首选)
- USB-A 3-5 米延长线走线
- **1 个体验位**,不做多人
- **放弃**:蓝牙、座机、一分二分配器、多耳机位

**Consequences**:
- ✅ 工程最简(一路 ASR/LLM/TTS)
- ✅ 贴合"孤独意识切片"主题
- ✅ 预算 < ¥300
- ✅ USB 耳机系统识别为独立设备,sounddevice 按 ID 绑定不冲突
- ⚠️ 接待吞吐受限(约 20 人/小时),排队是必然
- ⚠️ 失去"多人共享沉浸"的可能性

**Alternatives considered**:
详见 [hardware.md §11 不买清单](./hardware.md#11-不买清单明确避坑)。

---

## ADR-0005 · LLM 采用 4 个独立 session 架构
**Status**: **Superseded by ADR-0016** (2026-05-05)
**Date**: 项目初期

**Context**:
多角色对话有 3 种常见架构:
1. **单 session 多角色标签**:一个 LLM context 里让它扮演多个角色,输出时标注 speaker
2. **多 session 隔离**:每个角色一个独立 context,DM 路由
3. **多 agent 框架**(AutoGen / LangGraph):多个 agent 带工具/协商

问题:
- 方案 1 人设互相串扰,"图恒宇的台词"容易带上马兆的克制感
- 方案 3 对 2 分钟短剧过度工程化,且额外延迟不可接受

**Decision**:
- **4 个独立 ChatSession 对象**:DM / 图恒宇 / 马兆 / MOSS
- 每个维护独立 messages 列表 + 独立系统 prompt
- 由**独立的 DM session** 做路由(decide route_to)
- 每 session 只保留最近 10 轮对话,防止 token 爆炸

**Consequences**:
- ✅ 人设互不污染
- ✅ 可独立 A/B 换模型(如 MOSS 用小模型也能演)
- ✅ 失败隔离(一个 session 挂不影响其他)
- ⚠️ 同一时刻最多 2-3 个 session 并发调用,LLM API 并发成本略高(但实际还是很便宜)

**Alternatives considered**:
- 方案 1:否决,人设串扰无解
- 方案 3(AutoGen):否决,编排延迟 + 调试复杂

---

## ADR-0006 · 主进程 + ASR + VAD 必须在展位笔记本本地
**Status**: Accepted
**Date**: 项目初期

**Context**:
用户一度提议"所有组件 Docker 化全部搬学长服务器,展位本子只做音频 IO 客户端"。
但 USB 耳机是物理设备,音频流双向过公网会导致:
- VAD 响应从 10ms 恶化到 100ms+,**barge-in 彻底失效**
- 音频流上行带宽 + 抖动成新故障点
- Windows Docker USB 音频透传极其脆弱

**Decision**:
以下组件**强制在展位笔记本本地**,不接受远程化讨论:
- 主进程(Pipecat 管线)
- ASR(SenseVoice-Small)
- VAD(silero-vad)
- 音频 IO(sounddevice)
- 音频特效(pedalboard)
- WorldState + FSM + 预录兜底

**Consequences**:
- ✅ 音频毫秒级响应,打断体验稳
- ✅ 断网降级路径顺畅
- ⚠️ 展位笔记本性能要求提升(5060 Laptop 满足)
- ⚠️ 仓库不得不"两边部署",依赖布局无法统一(见 ADR-0008)

**Alternatives considered**:
- **全部上学长服务器 Docker**:否决,物理约束不允许
- **主进程本地 + ASR 远程**:否决,VAD 必须本地,ASR 和 VAD 耦合紧,分开增加复杂度

---

## ADR-0007 · MOSS 不使用刘琮声纹,纯电子合成
**Status**: **Superseded by ADR-0013** (2026-05-04)
**Date**: 项目初期

**Context**:
MOSS 在原片中由刘琮配音,声纹辨识度极高。AI 克隆刘琮声线存在:
- 明显声演侵权风险
- 开源发布后可能被截取滥用
- 合规审查不可控

但 MOSS 的"机械感"又是体验不可或缺的部分。

**Decision**:
- **不使用**刘琮任何音频作为 TTS 参考音
- CosyVoice 2 **zero-shot 无参考音模式**合成基础电子音
- 再经 pedalboard 处理:`LowpassFilter(3000Hz) + HighpassFilter(200Hz) + Distortion(8dB)`,偶发叠加 50Hz 电流嗡鸣
- prompt 层禁止模仿刘琮节奏特征(不拖尾音 / 不特定断句)

**Consequences**:
- ✅ 合规风险最小化
- ✅ 机械感反而更纯粹(更像 iRobot 而非"人声假装 AI")
- ⚠️ 失去原片声纹辨识度,部分观众可能觉得"不是那个 MOSS"
- ⚠️ 需要在 README/立牌说明"使用电子合成音,非刘琮"

**Alternatives considered**:
- **克隆刘琮声线 + 机械处理**:否决,侵权风险
- **使用其他机器人 AI 开源音色**(如 Google WaveNet 电子音):备选,但 CosyVoice 2 zero-shot 质量已够

---

## ADR-0008 · 本地用 uv 管依赖,远程服务用 Docker Compose
**Status**: Accepted
**Date**: 项目初期

**Context**:
ADR-0006 已决定主进程本地,TTS 远程。两端依赖如何管理?
- **统一 Docker**:学长服务器合适,但 Windows 展位笔记本上 Docker USB 音频透传是地狱
- **统一 uv**:展位笔记本合适,但学长服务器上 uv 不如 Docker 的环境隔离强
- **两端分别用最合适的**:看起来"脏",但实际工程性最好

**Decision**:
- **展位笔记本**:**uv + pyproject.toml + uv.lock**,一行 `uv sync` 复现环境
- **学长服务器(services/tts-server)**:**Docker Compose**,`nvidia/cuda` 基础镜像,GPU passthrough
- 两端共享 `lambda2/protocol/*`(协议定义),单一可信源
- 一个 Justfile 统一开发入口(`just dev` / `just deploy-tts` 各自转发)

**Consequences**:
- ✅ 两端各自最顺畅
- ✅ 避免 Windows Docker 音频透传
- ⚠️ 新加贡献者需要理解两端布局
- ⚠️ 两份 lock 文件需要同步更新协议版本

**Alternatives considered**:
- **全 Docker**:Windows 音频透传否决
- **全 uv**:学长服务器 CUDA 驱动兼容性管理麻烦,否决

---

## ADR-0009 · 观众语音不录制、不存储、不上传
**Status**: Accepted
**Date**: 项目初期

**Context**:
展位立牌声明了"您的语音不会被录制、存储或上传",这是合规承诺。
工程上需要对应保证:
- ASR 结果仅保留内存
- 日志不包含观众原话
- LLM API 厂商侧虽有留存,但已是脱敏文本

**Decision**:
- 观众语音 PCM 流**不落盘**,从麦克风直接进 ASR,不写临时文件
- ASR 文本只保留当前 session 的 messages(最多 10 轮)
- 每轮 `cycle_reset` 立即清空 session messages
- 日志 `structlog` 只记录事件 + 延迟 + 异常,**不记录对话内容**
- 展位日**彻底关闭** LLM 完整对话的 DEBUG 日志
- `scripts/cleanup.py` 在收场时清除所有临时缓存

**Consequences**:
- ✅ 合规承诺可兑现
- ✅ 隐私风险最小化
- ⚠️ 线上无法"复盘某一轮到底说了什么",事故排查只能靠 trace + 时间戳
- ⚠️ LLM API 厂商侧文本留存不可控,但文本已脱敏(无声纹、无 ID)

**Alternatives considered**:
- **本地加密存储观众音频**:否决,承诺了"不录制"就不录制,加密也是存了
- **完全不发 LLM SaaS,本地推理**:相关但独立问题,见 ADR-0002

---

## ADR-0010 · 角色引擎统一 + 实例化配置
**Status**: Accepted
**Date**: 2026-05-05

**Context**:
Phase 0 即将开写角色层代码。同时项目已确认存在至少 4-5 个角色(DM/图恒宇/马兆/MOSS/可能 + 图丫丫),且后续 AU 设定(`WanderingEarth2_AU_DigitalBackups.md`)使角色候选扩到 7+ 个。
如果每个角色写专属 `class` / 专属代码分支,将产生两个问题:
- 新增/替换角色要改代码 + 走 PR,而角色调整在本项目中是**设定迭代行为**,频率高
- prompt / 音色 / 滤波链散落在代码中,`@prompt?` / `@audio?` 专项 agent 很难在不碰代码的情况下迭代

**Decision**:
角色层采用"**单一引擎 + 多实例配置**"架构:
- **单一引擎实现**:所有角色共用同一套运行时代码,实现一次
- **每角色一个实例包**:每个角色对应一个独立的声明式配置包,包含该角色所需的全部参数(元数据、prompt 文本、阶段行为、音频相关设定、兜底资源等)
- **引擎按名加载实例包**:引擎在启动或切换时按角色名加载对应实例包
- **禁止**:为任何具体角色编写专属代码分支或专属类
- **验收硬指标**:新增 / 替换一个角色 = 新增或替换一个实例包,**不改动引擎代码**

本 ADR **只定架构原则**。具体实例包 schema、目录命名约定、引擎技术栈选型(运行时语言、配置格式、加载机制等) → 留给 `docs/DEVELOPMENT.md` 在 Phase 0 启动时细化。 Python 代码改动**

**Consequences**:
- ✅ `@prompt?` / `@audio?` / `@settingser1` 都能在不碰代码的前提下迭代自己负责的层
- ✅ AU 与官方设定的切换 = 替换 `instances/` 子目录,主管线不动(为 ADR-0012 的同人风险退出提供工程兜底)
- ✅ 单测可对 dummy 角色实例跑通,不用模拟真角色
- ⚠️ 配置 schema 要提前设计,前期一次性工程成本略高于最简方案
- ⚠️ `stage_overrides.yaml` 和 FSM 实现之间有耦合,需在 DEVELOPMENT.md 写清模块约定

**Alternatives considered**:
- **每角色独立的 Python 类**(或 `if-elif` 路由):否决,为设定层迭代拖累程序员,违背项目多 agent 分工
- **模板引擎生成角色类**(Jinja2 生代码):否决,多一层构建阶段,引入生成物与源入库的治理问题
- **在 `characters.md` 里写配置,代码执行时解析 Markdown**:否决,Markdown 非结构化锁 schema 难,治理不住

---

## ADR-0011 · 特性插件化与 Feature Flag 约定
**Status**: Accepted
**Date**: 2026-05-05

**Context**:
MOSS 接管机制的讨论稿(`MovieSource/WanderingEarth2_AU_MOSSTakeover_DDD.md`)揭示了一个更广的问题:
- MOSS 接管"是否做 / 怎么做"当前未决,且可能压根不做
- 但 Phase 0 验收要求包含"不做接管时主管线干净"和"后续 Phase 新增接管时改动局部"这两条互斥需求
- 类似的不确定性未来还会出现(图丫丫线下版到底加不加 / 二维带耳声场要不要等)

需要一条通用的架构规矩,把所有"**未决 · 可选 · 不稳定**"的特性置于主管线外。

**Decision**:
- 所有非核心或未决特性一律放于 **`features/<feature_name>/`** 目录
- 每个 feature 实现明确的 **Plugin 协议**(如 MOSS 接管的 `InterventionPlugin`)
- 主管线只导入**协议**,不导入实现内部
- 统一配置入口 **`config/features.yaml`**,每个 feature 至少暴露 `enabled: bool` 开关
- **NoOp 实现合法**:feature 禁用时 → 空实现 plugin,主管线调用代码不变
- **删除性**:`rm -rf features/<name>/` + 注释一行配置 → 主管线仍可启动
- FSM 与 feature 解耦:不直接调用 feature,改为 event bus 广播 + feature 自行订阅
- **首个示范样例**:MOSS 接管(`features/moss_takeover/`) —— 即使最终选方案 A(不做),该目录作为 NoOp 保留 + 文档归档,不删

**Consequences**:
- ✅ Phase 0 可以直接启动,不等 B1(是否做接管) 决策 —— `moss_takeover.enabled: false` + NoOp 实现即可
- ✅ 五个接管方案 A/B/C/D/E 在同一接口下落到不同 yaml,换方案不改代码
- ✅ `@review?` 未来审查时有统一标准:"是不是 feature?在不在 `features/`?有没有 Plugin 协议?能不能一行关掉?"
- ⚠️ 引入了"协议设计"成本,每个 feature 开头要先定接口再实现
- ⚠️ event bus 本身的实现成本转移到主管线(需在 Phase 0 启动时建立)
- ⚠️ 配置文件 `config/features.yaml` 未来可能膨胀,需在 Phase 2+ 回收整理

**Alternatives considered**:
- **直接把接管逻辑写在 FSM / 主管线**:否决,一旦选方案 A(不做)或将来切方案,清理成本高
- **编译时宏 / 环境变量开关**:否决,Python 的运行时开关重要,且编译时开关不支持展位日热切
- **用独立微服务**封装 feature:过度工程,单人项目不必

---

## ADR-0012 · 项目定位为非商业同人作品,沿用原片人物名
**Status**: Accepted
**Date**: 2026-05-05

**Context**:
项目核心包含原片人物(图恒宇/马兆/MOSS/图丫丫等)的二次创作。曾考虑两条路:
- 全部原创化人物名("某部长"/改姓的图恒宇副本等) —— 合规更安全但丢失观众辨识度 + AU 文档全部要重写
- 沿用原片人物名 —— 设定锚点完整,但需明确合规定位

@user 拍板:采用第二条,**项目按同人(fan work)定位**。

**Decision**:
本项目(展位版 + 开源版)正式定位为 **"《流浪地球 2》非官方同人二次创作 · 非商业"**,遵守以下约定:

**同人边界**:
- 沿用原片人物名、组织名(UEG/550W/MOSS 等)、地名、关键设定
- 但 **不复制原片连续台词**;所有角色语言性格为二次归纳 + 原创编写
- AU(数字备份 if 线)明确标注为原创推演,不等同于原片人物命运

**非商业硬约定**:
- 不收门票 / 不接广告 / 不做付费订阅 / 不卖周边 / 不接受打赏
- 展位依托学校嘉年华(非商业场景);开源版遵守选定 LICENSE 的非商业线(例如 CC BY-NC-SA或自定义同人 LICENSE)

**明示说明义务**:
以下位置必须包含同人声明:
- 展位立牌(中文 + 英文)
- GitHub README 顶部横幅
- 开源仓库 `description` 字段
- `docs/compliance.md` 专节

声明文本框架(具体文案由 `@review?` 定稿):
> "本作品为《流浪地球 2》非官方同人创作,与中国电影集团、郭帆导演及其关联权利方无任何关联。Unofficial fan work, not affiliated with China Film Group or its licensees."

**必要时的撤退预案**(绑定 ADR-0010):
- 权利方任何正式投诉/下架要求 → 立即撤展 + 仓库 archive
- ADR-0010 的实例化配置保证"**改名只需改 `instances/{name}/config.yaml` 的 `display_name` 字段 + 重命名目录**",可紧急切到备用原创世界观

**Consequences**:
- ✅ AU 文档 / 角色设定 / 影视分析知识库均可直接使用原名,不用重写
- ✅ 观众辨识度最高,展位代入感最强
- ✅ 同人界通行礼仪 + 明示声明 → 在中国同人生态内有默许空间
- ⚠️ 中国同人法律地位未明确,依赖"非商业 + 不贬损"的行业默认;权利方有权随时打破这个默认
- ⚠️ 开源仓库被第三方 fork 后商业化 → 需在 LICENSE 写明"NonCommercial"线
- ⚠️ 未来如需商业化 / 官方合作 → 本 ADR 失效,需走重定稿或正式授权路径
- ⚠️ 音频资产(声纹参考/角色配置/预录音频)通过「引擎/实例分离」策略处理 —— 引擎开源,声纹素材私有不入仓,见 ADR-0013 / ADR-0014

**Alternatives considered**:
- **全部原创化人物名**:否决,AU 文档重写成本高 + 观众辨识度丢失 + 叙事锚点断裂
- **完全不用《流浪地球》设定**(纯原创世界观):否决,与项目主题"数字生命"起源的叙事火花直接冲突
- **申请官方授权**:否决,单人项目无渠道无精力,且学校展位时效紧

---

## ADR-0013 · 所有角色使用本人声纹 TTS + 同人声明兜底
**Status**: Accepted
**Date**: 2026-05-04
**Supersedes**: ADR-0007

**Context**:
ADR-0007 出于极度谨慎,定了 MOSS 不用刘琮声纹。但实际评估后发现:
- 学校嘉年华半天展演,管辖范围极其有限
- 同人创作在中国 ACG / 影视生态内有广泛默许空间(特别是非商用非分发)
- 展摊一次性,后续追责极不现实
- 开源版通过"引擎 / 实例分离"(ADR-0014)可以从根本上解决公开仓库含原演员声纹的问题
- MOSS 如果用刘琮真声加轻度滤波,观众体验远超纯电子音(“那个 MOSS”的感觉)

**Decision**:
- **所有角色**的 TTS 均使用对应演员本人声纹作为 CosyVoice 2 参考音:
  - 图恒宇 = 吴京
  - 马兆 = 宁理
  - MOSS = 刘琮
  - 图丫丫 = 电影原角色演员
- MOSS 额外加 pedalboard 轻度滤波:LowpassFilter(4000Hz) + HighpassFilter(200Hz) + Distortion(3dB)
- 同人声明兜底:
  - 展位立牌标注"同人非商用"
  - 若被追问 → 口头声明 + 展示免费入场证据
- **声纹参考音不入开源仓库**(ADR-0014 执行)
- **备用方案 A**(纯电子音,不用原演员声纹)保留在 characters.md + ADR-0007,随时可切回

**Consequences**:
- ✅ 观众体验大幅提升("真的是图恒宇在说话")
- ✅ MOSS 保留人声底子 + 机械腔,比纯电子音更有识别度
- ✅ 引擎/实例分离 + 同人声明双保险
- ⚠️ 同人声明不是法律护盾,权利方追究时仍需执行应急回退(ADR-0007 保留的方案 A)
- ⚠️ 声纹采集需要额外工作量(UVR5 / Demucs 分离)
- ⚠️ 图丫丫(未成年角色)满度最高,参考音只用"正常生活"场景片段

**Alternatives considered**:
- **维持 ADR-0007**(不用刘琮声纹):否决,体验损失远大于风险收益,且引擎/实例分离已解决开源合规
- **只 MOSS 用刘琮,其他不用原演员**:否决,既然已定同人 + 引擎分离,没理由只到 MOSS

---

## ADR-0014 · 开源发布采用引擎 / 实例分离策略
**Status**: Accepted
**Date**: 2026-05-04

**Context**:
ADR-0013 决定线下版使用原演员声纹,但 GitHub 开源仓库不能含这些素材。
同时 ADR-0010 已经定了「单一引擎 + 多实例配置」的架构,这为发布分离提供了工程基础。
需要一条明确的发布策略:哪些文件开源、哪些私有、如何确保引擎可独立运行。

**Decision**:
GitHub 仓库作为**引擎框架**发布,线下展演作为「引擎 + 流浪地球 2 实例」的一个具体部署。

开源(入仓):
- `lambda2/`：全部引擎代码
- `services/`：TTS 服务端代码
- `docs/`：文档(不含原始声纹文件)
- `assets/ambient/`：环境底噪(原创生成)
- `configs/characters/_example.yaml`：模板文件
- `scripts/`：工具脚本
- `tests/`：单测

私有(`.gitignore`):
- `configs/characters/*.yaml`(除 `_example.yaml`)
- `assets/voice-refs/`(全部)
- `assets/prerecorded/`(全部)
- `some-pieces/`

引擎自举能力:
- 开源版必须能独立启动(demo 模式)
- 缺失角色配置时给明确错误提示,不 crash
- `_example.yaml` + 空响应回路让别人能理解架构并自行创建角色

README 必须包含:
- "本仓库是 Lambda² 引擎框架,不含角色数据"
- "使用者需自行准备声纹参考与角色配置"
- 同人声明

**Consequences**:
- ✅ 开源仓库完全不含任何原演员声纹,合规开绿灯
- ✅ 别人可以 fork 后做自己的数字生命叙事(任何 IP)
- ✅ 被下架只需删本地素材,引擎仓库不受影响
- ✅ 项目可复用性大幅提升(从"同人项目" → "通用 voice agent 框架")
- ⚠️ 新用户需要自备声纹 + 配置,门槛略高
- ⚠️ `_example.yaml` 和文档要足够清晰,否则别人不知道怎么上手

**Alternatives considered**:
- **开源版内置一套“安全原创角色”**(LibriTTS 声源 + 原创人设):未排除,但工作量大,待引擎稳定后再评估
- **双仓库**(engine repo + instance repo,后者 private):否决,单人维护两个 repo 没必要,.gitignore 已够用
- **用 git-crypt 加密私有文件**:否决,增加复杂度且不透明,不如简单 .gitignore

---

## ADR-0015 · 轮回时长参数三层定义
**Status**: Accepted
**Date**: 2026-05-05

**Context**:
原先文档统一写“2 分钟轮回”,但实际运行时网络延迟、TTS 分句耗时、剧情兜底回放、FSM 阶段过渡等会不可避免地拉长实际体验时长。
如果硬卡 2 分钟强制 RESET,剧情将频繁被截断;如果不设上限,LLM 发散时无法收场。

**Decision**:
| 层级 | 时长 | 语义 |
|---|---|---|
| **标称值** | **2 分钟** | 对观众口径、叙事层“意识切片”的时间键、角色 prompt 内的时间感知 |
| **实际运行** | **≈3 分钟** | 含 TTS 延迟、剧情兜底、阶段过渡、缓冲冗余;正常 cycle 落在此区间 |
| **硬上限** | **3 分 30 秒** | FSM 强制 RESET 的不可突破天花板 |

- 角色 prompt / characters.md / compliance.md / 展位宣传 → 统一用“2 分钟”
- DEVELOPMENT.md / FSM 代码 / timeline → 用实际值 3min + 硬上限 3.5min

**Consequences**:
- ✅ 观众对外认知简单
- ✅ 工程层有冗余,剧情不会被截断
- ✅ 硬上限保证不会无限卡死
- ⚠️ 实际周转率按 ~4min/人 算 ≈ 15 人/小时,彩排时关注

**Alternatives considered**:
- **硬卡 2 分钟**:否决,延迟导致剧情截断
- **不设上限**:否决,周转率不可控
- **对外说 3 分钟**:否决,“两分钟”是叙事锚点

---

## ADR-0016 · 世界引擎软硬分离 + 数字生命单主体模式
**Status**: Accepted
**Date**: 2026-05-05
**Supersedes**: ADR-0005

**Context**:
ADR-0005 原定"4 个独立 ChatSession(DM / 图恒宇 / 马兆 / MOSS)并行"。但随着项目叙事模型清晰化,这个方案被认定为一个错误(过早由 agent 写入,未经 @user 审核):
- **"数字生命"不是多人聊天室**,而是"一个意识在一个世界里"
- 其他角色是世界的一部分(记忆/环境),不是独立主体
- DM 不是"第 5 个角色",而是世界引擎的叙事驱动层("软"部分)
- FSM / timeline / 计时 = 世界引擎的"硬"部分
- DM(软) + 框架(硬) 共同替代了当初被否决的 Unity/Godot 物理引擎的位置

例如:修服务器场景,马兆是主体(接 LLM),图恒宇作为他的记忆/环境写死 —— 这本身就是叙事震撼的一部分。

**Decision**:
- 每个 cycle 只有 **一个数字生命主体** 接 LLM
- DM = 世界引擎软层(叙事驱动),不是独立角色 session
- FSM / timeline / 硬规则 = 世界引擎硬层
- 其他角色按场景环境化(写死在 prompt / 音频资源 / 记忆片段)
- DM 与角色 LLM 的接口、结构化输出格式、DSL 调用机制 → **实现层待设计(Phase 1 解决)**

**实现层待设计问题**(明确要解决,非摸棱两可):
- DM 怎么接入角色 LLM?(调度方式 / 嵌套 / 串行)
- 角色 LLM 结构化输出怎么分("说什么" vs "做什么")?
- DM 对世界引擎硬部分的调用机制(DSL / 函数调用 / 事件)?
- 世界反馈路径:DM 直接充当世界逻辑? 还是先过硬部分解析再转发?
- 不同场景的"谁是主体"在剧本层面怎么定义?

**Consequences**:
- ✅ 叙事上更准确:"一个意识在世界里"而不是"多人聊天"
- ✅ LLM 调用成本大幅降低(从 4 session → 1 主体 + DM)
- ✅ 其他角色环境化后可以用预录音频替代 TTS,进一步降延迟
- ✅ 延迟链路变短:单路 LLM 调用,不用等多 session 协调
- ⚠️ DM 世界层的接口设计复杂度高
- ⚠️ DEVELOPMENT.md 架构图 / 模块规范需重写相关章节
- ⚠️ 不同场景的"谁是主体"需要在剧本层面设计

**Alternatives considered**:
- **维持 ADR-0005**(4 session 并行):否决,叙事模型不对 + 不必要的复杂度和延迟
- **DM 也接独立 LLM + 角色也各接独立 LLM**:否决,与"单主体"矛盾,延迟/成本高
