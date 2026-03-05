import copy
from dataclasses import dataclass
from dataclasses import field


def default_field(obj):
    # pylint: disable=invalid-field-call
    # ruff: noqa: RUF009
    return field(default_factory=lambda: copy.deepcopy(obj))


@dataclass
class Bar:
    kind: str
    title: str
    foreground: str
    background: str = "#494949"


@dataclass
class Settings:
    name: str = "Xen System Monitor"
    title: str = "Xen System Monitor"
    update_interval: float = 2.0
    notification: bool = True
    """Enable desktop notifications from this app"""
    width: int = 32
    height: int = 32
    rotation_angle: float = 90
    main_action: str = "/usr/bin/xfce4-terminal -e xentop -T XenTop"
    background: str = "#1c1c1c"
    memory_threshold: float = 0.8

    bars: list[Bar] = default_field(
        [
            Bar(kind="vcpu", title="VCPU", foreground="#00FF00"),
            Bar(kind="pcpu", title="PCPU", foreground="#00AAAA"),
            Bar(kind="vram", title="RAM", foreground="#FF0000"),
        ]
    )
