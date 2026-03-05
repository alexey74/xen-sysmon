import json
import logging
from dataclasses import asdict
from pathlib import Path

from xdg.BaseDirectory import load_first_config
from xdg.BaseDirectory import save_config_path

from .settings import Bar
from .settings import Settings


log = logging.getLogger(__name__)


class SettingsManager:
    _filename = "settings.json"
    _resource = __package__ or "xen_sysmon"

    @staticmethod
    def custom_decoder(obj):
        if "kind" in obj:
            return Bar(**obj)
        return obj  # fallback for other objects

    def load(self):
        sdict = {}
        path = load_first_config(Path(self._resource) / self._filename)
        try:
            with open(path, "r", encoding="utf-8") as fp:
                sdict = json.load(fp, object_hook=self.custom_decoder)

            log.info("Settings loaded from %s", path)
            log.debug("settings: %s", sdict)
            return Settings(**sdict)

        except (TypeError, IOError) as err:
            log.error("Unable to load %s: %s", path, err)
            settings = Settings()
            self.store(settings)
            return settings

    @property
    def save_config_path(self):
        return Path(save_config_path(self._resource)) / self._filename

    def store(self, settings) -> None:
        path = self.save_config_path
        try:
            with open(path, "w", encoding="utf-8") as fp:
                json.dump(asdict(settings), fp, indent=2)
            log.info("Settings saved to %s", path)
        except IOError as err:
            log.error("Unable to write to %s: %s", path, err)
