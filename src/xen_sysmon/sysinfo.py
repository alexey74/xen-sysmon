import logging
import time
from functools import cached_property

import pyxs


log = logging.getLogger(__name__)

try:
    from xen.lowlevel import xc  # pylint: disable=import-error
except (ImportError, ModuleNotFoundError) as exc:
    log.critical("No lowlevel Xen module found: %s", exc)


class SysInfo:
    def __init__(self) -> None:
        self.xen_conn = None
        try:
            self.xen_conn = xc.xc()
        except xc.Error as err:
            log.error("xen conn error: %s", err)
        self.ts = None

    @cached_property
    def total_mem(self):
        if self.xen_conn:
            try:
                total_mem = int(self.xen_conn.physinfo()["total_memory"])
                return total_mem
            except (xc.Error, KeyError, ValueError) as err:
                log.error("mem stats error: %s", err)
        return None

    @cached_property
    def dom_stats(self):
        _dom_stats = {}

        try:
            self.ts = time.time()
            dom_info = self.xen_conn.domain_getinfo()
            log.debug("dom info: %s", dom_info)
            _dom_stats.update({di["domid"]: {"cpu_time": di["cpu_time"]} for di in dom_info})
        except (xc.Error, KeyError, ValueError) as err:
            log.error("dom stats error: %s", err)
        log.debug("dom stats: %s", _dom_stats)

        try:
            with pyxs.Client() as xs_client:
                for dom_id in xs_client.list(b"/local/domain"):
                    dom_id = int(dom_id)
                    if dom_id not in _dom_stats:
                        log.warning("xs domain missing in xc: %s", dom_id)
                        _dom_stats[dom_id] = {}

                    try:
                        _dom_id_xs = xs_client.read(f"/local/domain/{dom_id}/domid".encode())
                        _dom_stats[dom_id]["name"] = xs_client.read(
                            f"/local/domain/{dom_id}/name".encode()
                        ).decode("utf-8")
                    except pyxs.exceptions.PyXSError as err:
                        log.debug("skipped dom %s: read id/name: %s", dom_id, err)
                        continue

                    for param in ("target", "meminfo", "static-max", "hotplug-max"):
                        path = f"/local/domain/{dom_id}/memory/{param}"
                        try:
                            val = xs_client.read(path.encode())
                        except pyxs.exceptions.PyXSError as err:
                            if "No such file" not in str(err):
                                log.warning("xs read (%s): %s", path, err)
                        if val:
                            _dom_stats[dom_id][param] = int(val.decode())

        except pyxs.exceptions.ConnectionError as err:
            log.error("fatal XS error: %s", err)
        log.debug("mem: dom stats: %s", _dom_stats)

        return _dom_stats

    def reset(self):
        try:
            del self.dom_stats
        except AttributeError:
            pass
