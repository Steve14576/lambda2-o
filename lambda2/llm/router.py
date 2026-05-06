"""LiteLLM 调用封装 + DM 路由逻辑."""

from __future__ import annotations

# TODO: 实现 LLMRouter
# - LiteLLM.acompletion 封装
# - model 通过 Settings 配置
# - 路由规则: DM 做判定 → route_to 字段指定下一角色
# - 三层校验: prompt层 / pydantic层 / 引擎层
