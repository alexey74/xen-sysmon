import pydantic


class BaseSettings(pydantic.BaseSettings):
    class Settings:
        use_attribute_docstrings = True


class BarSettings(BaseSettings):
    title: str
    foreground: str
    background: str = "black"


class Bars(BaseSettings):
    cpu: BarSettings = BarSettings("CPU", foreground="green")
    ram: BarSettings = BarSettings("RAM", foreground="red")


class Settings(BaseSettings):
    name = "Xen System Monitor"
    title = "Xen System Monitor"
    update_interval: float = 2.0
    notification: bool = True
    """Enable desktop notifications from this app"""
    icon_size: int = 32
    rotation_angle: float = 90
    main_action: str = "/usr/bin/xfce4-terminal -e xentop -T XenTop"
    background: str = "#1c1c1c"
    memory_threshold: float = 0.8

    bars: dict[str, BarSettings] = Bars().dict()
