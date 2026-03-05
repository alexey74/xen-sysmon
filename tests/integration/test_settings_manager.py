import os

from pytest_mock import MockerFixture

from xen_sysmon.settings import Settings
from xen_sysmon.settings_manager import SettingsManager


def test_save_load_cycle_keeps_same_values(mocker: MockerFixture, tmp_path, monkeypatch) -> None:
    mocker.patch.object(SettingsManager, "_resource", "foo")
    monkeypatch.setattr('xdg.BaseDirectory.xdg_config_home', str(tmp_path))
    monkeypatch.setattr('xdg.BaseDirectory.xdg_config_dirs', [str(tmp_path)])
    sm = SettingsManager()
    s = Settings(update_interval=42.0)
    sm.store(s)

    sm1 = SettingsManager().load()

    assert sm1.update_interval == 42.
    assert os.path.isfile(tmp_path / 'foo/settings.json')
