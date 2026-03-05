import sys
from unittest.mock import MagicMock


try:
    from xen.lowlevel import xc  # pylint: disable=import-error
    from xen.lowlevel import xs  # pylint: disable=import-error
except (ImportError, ModuleNotFoundError) as exc:
    print("Faking Xen modules: %s" % exc)
    Module = type(sys)

    xen = Module("xen")
    xen.lowlevel = Module("lowlevel")
    xen.lowlevel.xc = Module("xc")
    xen.lowlevel.xs = Module("xs")

    xen.lowlevel.xc.xc = MagicMock()
    xen.lowlevel.xc.Error = Exception

    xen.lowlevel.xs.xs = MagicMock()
    xen.lowlevel.xs.Error = Exception

    sys.modules["xen"] = xen
    sys.modules["xen.lowlevel"] = xen.lowlevel
    sys.modules["xen.lowlevel.xc"] = xen.lowlevel.xc
    sys.modules["xen.lowlevel.xs"] = xen.lowlevel.xs
