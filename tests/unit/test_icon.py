import pytest
from PIL import Image
from pytest_mock import MockerFixture

from xen_sysmon import icon


def test_create_icon():
    pass

class TestIcon:
    @pytest.fixture
    def app(self):
        from xen_sysmon.app import Application

        return Application()

    @pytest.fixture
    def icon_obj(self, app):
        return icon.Icon(app)

    def test_create_image(self, icon_obj):
        image = icon_obj.create_image()
        assert image.size == (icon_obj.config.width, icon_obj.config.height)
        assert image.mode == "RGB"

    def test_draw_progress_bar(self, icon_obj):
        image = Image.new(
            "RGB", (icon_obj.config.width, icon_obj.config.height), icon_obj.config.background
        )
        icon_obj.draw_progress_bar(image, 1, 2, 10, 20, 0.5, bg="#fff", fg="#000")

    def test_feed_vcpu(self, icon_obj):
        # Note: This test requires a Xen host with running VMs
        si = icon.SysInfo()
        icon_obj.last_cpu_time = {222: 123134124}
        si.dom_stats = {222: {"cpu_time": 123344556}}, 34444
        result = icon_obj.feed_vcpu(si)
        assert result is None

    def test_feed_vram(self, icon_obj, mocker):
        # Note: This test requires a Xen host with running VMs
        si = icon.SysInfo()
        si.dom_stats_vram = {42: {"meminfo": 4343}}
        si.total_mem = 4242424
        si.xs_conn.read = mocker.MagicMock()
        result = icon_obj.feed_vram(si)
        assert isinstance(result, tuple)

    def test_update_loop(self, icon_obj, mocker):
        icon_obj.alive = False
        icon_obj.update_loop(icon_obj)


    def test_main_action(self, icon_obj, mocker: MockerFixture):
        # Note: This test requires a main action to be configured
        m = mocker.patch("subprocess.Popen")
        icon_obj.remove_notification = mocker.MagicMock()
        icon_obj.main_action(mocker.MagicMock(), mocker.MagicMock())

        m.assert_called_once()
