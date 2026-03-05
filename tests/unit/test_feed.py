from unittest.mock import Mock
from unittest.mock import patch

import pytest

from xen_sysmon.feed import FeedMixin
from xen_sysmon.sysinfo import SysInfo  # noqa: F401


class XenSysmonFeed(FeedMixin):
    pass


@pytest.fixture
def feed():
    return XenSysmonFeed()


class TestFeedMixin:
    @patch("xen_sysmon.feed.SysInfo")
    def test_feed_vcpu(self, mock_si):
        feed = XenSysmonFeed()
        mock_stats = {1: {"cpu_time": 100}}
        ts = 424242
        mock_si.return_value.dom_stats = (mock_stats, ts)
        feed._last_ts['vcpu'] = 424241
        feed.last_cpu_time[1] = 90
        result = feed.feed_vcpu(mock_si())
        assert result is not None

    @patch("xen_sysmon.feed.SysInfo")
    def test_feed_pcpu(self, mock_si):
        feed = XenSysmonFeed()
        mock_stats = [{"idletime": 100}]
        ts = 424242
        feed._last_ts['pcpu'] = 424241
        mock_si.return_value.pcpu_stats = (mock_stats, ts)
        result = feed.feed_pcpu(mock_si())
        assert result is not None

    @patch("xen_sysmon.feed.SysInfo")
    def test_feed_vram(self, mock_si):
        feed = XenSysmonFeed()
        mock_stats = {11: {"meminfo": 100}}
        total_mem = 1024
        mock_si.return_value.dom_stats_vram = mock_stats
        mock_si.return_value.total_mem = total_mem
        result = feed.feed_vram(mock_si())
        assert result is not None
