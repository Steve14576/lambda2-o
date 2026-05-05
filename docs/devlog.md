# Lambda² · 开发日志 (devlog)

> 这是一份**流水账**,不是 CHANGELOG,不是 release notes。
> 作用:记录每天做了什么、遇到什么、决定什么,防止"昨天的自己"和"明天的自己"失联。
>
> 格式:倒序时间线(最新在上),每条 ≤ 100 字,不追求完整文字。
> 重大决策 → 另开 ADR;代码变更 → git log 自有;本文档只记**过程 / 心路 / 待办 / 坑**。

---

## 写作约定

每条格式:
```markdown
## YYYY-MM-DD
- 🎯 今日目标:
- ✅ 完成:
- 🐛 遇到:
- 💡 决定:(重大改动 → 另开 ADR 链接过来)
- ⏭️ 下次:
```

标签约定(方便搜):
- `#phase0` / `#phase1` ... :对应开发路线阶段
- `#hardware` / `#llm` / `#tts` / `#asr` / `#audio` / `#docs` :模块
- `#bug` / `#decision` / `#note` / `#todo` :类型
- `#adr-XXXX`:关联到具体 ADR

---

## 2026-05-04

- 🎯 今日目标:建立完整文档体系,让未来的自己不混乱 `#docs`
- ✅ 完成:
  - `docs/DEVELOPMENT.md`(架构主文档,802 行)
  - `docs/hardware.md`(采购详单)
  - `docs/characters.md`(5 个角色完整 prompt)
  - `docs/compliance.md`(合规规范)
  - `docs/runbook.md`(展位日手册)
  - `docs/adr.md`(架构决策记录 × 9 条)
  - `docs/product.md`(轻量 PRD)
  - `docs/devlog.md`(本文档)
  - `docs/glossary.md`(术语表)
- 💡 决定:
  - `#adr-0001` 放弃 Godot,主干用纯 Python
  - `#adr-0002` LLM 走 SaaS 不微调
  - `#adr-0003` TTS 主力在学长 4090
  - `#adr-0004` 硬件 = USB 有线耳机 × 1 位
  - `#adr-0005` 4 个独立 LLM session
  - `#adr-0006` 主进程/ASR/VAD 必须本地
  - `#adr-0007` MOSS 不用刘琮声纹
  - `#adr-0008` 本地 uv + 远程 Docker
  - `#adr-0009` 观众语音不录制
- ⏭️ 下次:
  - 硬件下单(本周内,详见 `hardware.md §8`)
  - Phase 0 骨架:`pyproject.toml` + `lambda2/` 目录 + `.env.example` + `Justfile`
  - 问学长:服务器公网暴露方式 + 可用时段
  - 选 LLM 厂商做小 ping 测:qwen-max vs doubao-pro

---

## (空模板,下一天追加时复制)

## YYYY-MM-DD

- 🎯 今日目标:
- ✅ 完成:
- 🐛 遇到:
- 💡 决定:
- ⏭️ 下次:

---

## 特殊事件日志

### 展位日 Post-Mortem(展位后补)
预留空节。展位日当天结束 24 小时内必写:
- 观众人数 / 完整率 / 故障次数
- 哪个降级启动过?
- 最高兴 / 最尴尬的瞬间
- 硬件坏了什么?
- 反馈关键词 TOP 10

### 开源 Release Post-Mortem(开源后补)
预留空节:
- 第一天 clone / star / issue 数
- 部署卡点(别人 issue 里反馈的)
- 后续维护承诺

---

## 维护约定
- **每个工作日结束** 5 分钟写一条,不追求完整
- 偷懒时可写一行 `摸鱼,没进展`,也比空白强
- 每周末回看 7 天日志,提炼一条 **"本周学到"** 加到文末 `#note`
- 月末看月度日志,决定是否需要更新 PRD 或 ADR

---

## 本周学到(周总结区)

*(暂空)*
