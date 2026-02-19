import os

from pytest_mock import MockerFixture

from xen_sysmon.settings_manager import SettingsManager


def test_save_load_cycle_keeps_same_values(mocker: MockerFixture, tmp_path, monkeypatch) -> None:
    mocker.patch.object(SettingsManager, "_resource", "foo")
    monkeypatch.setattr('xdg.BaseDirectory.xdg_config_home', str(tmp_path))
    monkeypatch.setattr('xdg.BaseDirectory.xdg_config_dirs', [str(tmp_path)])
    sm = SettingsManager(update_interval=42.0)
    sm.to_yaml()

    sm1 = SettingsManager.from_yaml()

    assert sm1.update_interval == 42.
    assert sm.dict() == sm1.dict()
    assert os.path.isfile(tmp_path / 'foo/settings.yaml')
