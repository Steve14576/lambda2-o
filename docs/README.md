# Lambda² · 文档索引

> 所有文档都在本目录。按**用途**分类查阅,不按字母序。

---

## 🎯 入门 / 对齐

| 文档 | 回答什么 | 何时读 |
|---|---|---|
| [product.md](./product.md) | **做什么、给谁、怎么算成功** | 新人入场 / 讨论需求变更 |
| [glossary.md](./glossary.md) | **我们说的 XX 是什么意思** | 任何时候有名词疑问 |

## 🛠 工程实现

| 文档 | 回答什么 | 何时读 |
|---|---|---|
| [DEVELOPMENT.md](./DEVELOPMENT.md) | **整体架构 + 模块 + 协议 + 路线图**(主文档) | 动手前 / 架构讨论 |
| [characters.md](./characters.md) | **5 个角色的完整 prompt + 音色规范** | 改角色行为 / 加新角色 |
| [hardware.md](./hardware.md) | **买什么 / 多少钱 / 怎么验收** | 下单前 / 硬件坏时 |

## 📋 运维 / 操作

| 文档 | 回答什么 | 何时读 |
|---|---|---|
| [runbook.md](./runbook.md) | **展位日怎么操作 / 故障怎么救** | 展位日(打印版带现场) |
| [compliance.md](./compliance.md) | **合规边界 / 声明模板 / 下架预案** | 开源发布前 / 有人投诉时 |

## 📜 历史 / 追溯

| 文档 | 回答什么 | 何时读 |
|---|---|---|
| [adr.md](./adr.md) | **为什么当时这么选**(架构决策记录) | 要推翻某个决策前 |
| [devlog.md](./devlog.md) | **每天做了什么 / 心路** | 回忆昨天 / 找某个坑怎么填的 |

---

## 文档维护约定

1. **架构/协议改动 → 先改文档再动代码**
2. **ADR 永不删,推翻就加新的标记 Supersedes**
3. **prompt 改动 → 同步改 `characters.md` + bump 版本**
4. **新术语 → 加 `glossary.md`**
5. **每日收工 5 分钟写 `devlog.md`**
6. 合规相关改动 → 必须更新 `compliance.md` 和 README

## 目录快速浏览

```
docs/
├── README.md          ← 你在这里
├── product.md         ← PRD(做什么)
├── DEVELOPMENT.md     ← 技术主文档(怎么做)
├── characters.md      ← 角色 prompt
├── hardware.md        ← 硬件采购
├── compliance.md      ← 合规规范
├── runbook.md         ← 展位手册
├── adr.md             ← 架构决策记录
├── devlog.md          ← 开发日志
└── glossary.md        ← 术语表
```
