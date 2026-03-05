import logging
import shutil
import subprocess
from importlib.resources import files
from pathlib import Path

from xdg.BaseDirectory import load_first_config
from xdg.BaseDirectory import save_config_path

from .icon import Icon
from .settings_manager import SettingsManager


log = logging.getLogger(__name__)


class Application:
    desktop_filename = "xen-sysmon.desktop"

    def __init__(self):
        self.settings_manager = SettingsManager()
        self.config = self.settings_manager.load()
        self.icon = Icon(self)

    def run(self):
        self.icon.run()

    def toggle_auto_start(self, flag: bool | None = None) -> None:
        log.debug("toggle autostart: %s", flag)
        if flag is None:
            self.toggle_auto_start(not self.is_auto_start_enabled())
        else:
            dstpath = Path(save_config_path("autostart")) / self.desktop_filename
            if flag:
                with (
                    files(f"{__package__}.data").joinpath(self.desktop_filename).open("r") as src,
                    open(dstpath, "w", encoding="utf-8") as dst,
                ):
                    shutil.copyfileobj(src, dst)
            else:
                dstpath.unlink(missing_ok=True)

    def is_auto_start_enabled(self) -> bool:
        return load_first_config(Path("autostart") / self.desktop_filename) is not None

    def edit_settings(self) -> None:
        with subprocess.Popen(f"xdg-open {self.settings_manager.save_config_path}", shell=True):
            pass

    def save_settings(self) -> None:
        self.settings_manager.store(self.config)
