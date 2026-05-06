"""测试 LLM 输出 schema 校验."""

from lambda2.llm.schema import ActionIntent, LLMOutput, WorldDelta


def test_valid_output():
    """正常输出应通过校验."""
    output = LLMOutput(
        speaker="tuhengyu",
        text="我记得这里……",
        emotion="uneasy",
        intensity=0.6,
    )
    assert output.speaker == "tuhengyu"
    assert output.emotion == "uneasy"


def test_default_values():
    """缺省值应合理."""
    output = LLMOutput(speaker="dm")
    assert output.text == ""
    assert output.emotion == "calm"
    assert output.intensity == 0.3
    assert output.world_delta.erosion == 0


def test_world_delta_bounds():
    """WorldDelta 应在范围内."""
    delta = WorldDelta(erosion=15, ambient_hum=0.2)
    assert -10 <= delta.erosion <= 20
    assert -0.3 <= delta.ambient_hum <= 0.3


def test_action_intent():
    """ActionIntent 应仅允许枚举值."""
    intent = ActionIntent(action="insert_udisk", target="moss")
    assert intent.action == "insert_udisk"
