import pytest

from xen_sysmon.sysinfo import SysInfo


def test_total_mem():
    sys_info = SysInfo()
    assert isinstance(sys_info.total_mem, int)

def test_dom_stats(mocker):
    sys_info = SysInfo()
    sys_info.xc_conn = mocker.MagicMock()
    sys_info.xc_conn.domain_getinfo.return_value = [{'domid': 42, 'foo': 11}]
    stats, _ = sys_info.dom_stats
    assert isinstance(stats, dict)
    assert len(stats) > 0

def test_vram():
    sys_info = SysInfo()
    vram = sys_info.dom_stats_vram
    assert isinstance(vram, dict)

def test_pcpu_stats(mocker):
    sys_info = SysInfo()
    sys_info.xc_conn = mocker.MagicMock()
    sys_info.xc_conn.getcpuinfo.return_value = [{'idletime': 2342342}]
    stats, _ = sys_info.pcpu_stats
    assert isinstance(stats, list) or stats is None

def test_general_info():
    sys_info = SysInfo()
    info = sys_info.general_info()
    assert isinstance(info, dict)
