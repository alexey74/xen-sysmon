import logging
import time
import typing as t
from functools import cached_property


log = logging.getLogger(__name__)

try:
    from xen.lowlevel import xc  # pylint: disable=import-error
    from xen.lowlevel import xs  # pylint: disable=import-error
except (ImportError, ModuleNotFoundError) as exc:
    log.critical("Lowlevel Xen modules import error: %s", exc)
    import os

    if "NO_PYXEN" not in os.environ:
        raise SystemExit(-1) from exc


class SysInfoError(Exception):
    pass


class SysInfo:
    MAX_PCPUS = 128

    def __init__(self) -> None:
        self._xs_xact_id = None
        try:
            self.xc_conn = xc.xc()
            self.xs_conn = xs.xs()
        except (NameError, xc.Error, xs.Error) as err:
            log.error("xen conn error: %s", err)
            raise SysInfoError from err

    def __enter__(self):
        self._xs_xact_id = self.xs_conn.transaction_start()
        return self

    def __exit__(self, *_args):
        if self._xs_xact_id:
            self.xs_conn.transaction_end(self._xs_xact_id)

    @cached_property
    def total_mem(self):
        try:
            return int(self.xc_conn.physinfo()["total_memory"])
        except (xc.Error, KeyError, ValueError) as err:
            log.error("physinfo error: %s", err)
            raise SysInfoError from err

    @cached_property
    def dom_stats(self) -> tuple[dict[int, dict[str, t.Any]], float]:
        ts = time.time()

        try:
            dom_info = self.xc_conn.domain_getinfo()
            log.debug("dom info: %s", dom_info)
            return {int(di["domid"]): di for di in dom_info}, ts
        except (xc.Error, KeyError, ValueError) as err:
            log.error("dom stats error: %s", err)
            return {}, ts

    def _get_dom_path(self, dom_id: int) -> str:
        return self.xs_conn.get_domain_path(dom_id)

    def get_domain_name(self, dom_id: int) -> bytes:
        name = None
        try:
            name = self.xs_conn.read(self._xs_xact_id, f"{self._get_dom_path(dom_id)}/name")
        except xc.Error as err:
            log.error("dom name error: %s", err)
        if name is None:
            name = b"Unknown"
        return name

    @cached_property
    def dom_stats_vram(self) -> dict[int, dict[str, int]]:
        _stats: dict[int, dict[str, int]] = {}

        for dom_id in self.dom_stats[0]:
            if dom_id not in _stats:
                _stats[dom_id] = {}
            for param in ("target", "meminfo", "static-max", "hotplug-max"):
                try:
                    path = self._get_dom_path(dom_id)
                    val = self.xs_conn.read(self._xs_xact_id, f"{path}/memory/{param}")
                    if val is not None:
                        _stats[dom_id][param] = int(val)
                except (xs.Error, TypeError, ValueError) as err:
                    log.warning("xs read (%s): %s", path, err)

        log.debug("mem: dom stats: %s", _stats)
        return _stats

    @property
    def pcpu_stats(self) -> tuple[list[dict[str, int]] | None, float]:
        ts = time.time()

        try:
            return self.xc_conn.getcpuinfo(self.MAX_PCPUS), ts
        except xc.Error as err:
            log.warning("xc get PCPU info: %s", err)
            return None, ts

    def general_info(self):
        info = {}
        try:
            info |= self.xc_conn.physinfo()
            info |= self.xc_conn.xeninfo()
        except xc.Error as err:
            log.warning("xc gen info read: %s", err)
        return info

    def reset(self):
        try:
            del self.dom_stats, self.dom_stats_vram
        except AttributeError:
            pass

    def domain_action(self, action, dom_id, *_args, **_kwargs) -> int | None:
        log.info("domain action: %s on ID %s", action, dom_id)

        match action:
            case "shutdown":
                xtra = [0]  # reason
            case "resume":
                xtra = [1]  # fast
            case _:
                xtra = []

        try:
            return getattr(self.xc_conn, f"domain_{action}")(dom_id, *xtra)
        except xc.Error as err:
            log.warning("xc gen info read: %s", err)
        return None
