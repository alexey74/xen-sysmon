import logging
from pathlib import Path

from pydantic_yaml import parse_yaml_file_as
from pydantic_yaml import to_yaml_file
from xdg.BaseDirectory import load_config_paths
from xdg.BaseDirectory import save_config_path

from .settings import Settings


log = logging.getLogger(__name__)


class SettingsManager(Settings):
    _filename = "settings.yaml"
    _resource = __package__

    @classmethod
    def from_yaml(cls) -> "SettingsManager":
        for path in load_config_paths(cls._resource):
            try:
                return parse_yaml_file_as(SettingsManager, Path(path) / cls._filename)
            except IOError as err:
                log.debug("Failed to read %s: %s", path, err)

        # If no files exist, return a Settings instance with default values
        log.warning("None of the settings files found. Initializing with default values.")
        _settings = cls()
        _settings.to_yaml()
        return _settings

    def to_yaml(self) -> None:
        path = Path(save_config_path(self._resource)) / self._filename

        try:
            to_yaml_file(path, self, add_comments=True)
            log.info("Settings saved to %s", path)
        except IOError as err:
            log.error("Unable to write to %s: %s", path, err)
