import logging

from .sysinfo import SysInfo


log = logging.getLogger(__name__)


class FeedMixin:
    def __init__(self, *args, **kw) -> None:
        self._last_ts: dict[str, float] = {}
        self.last_cpu_time: dict[int, int] = {}
        self.last_idle_time: dict[int, float] = {}

        super().__init__(*args, **kw)

    def feed_vcpu(self, si: SysInfo) -> tuple[float, str, dict[int, float]] | None:
        stats, ts = si.dom_stats
        cpu_max_time = 0
        cpu_top_dom_id = None
        cpu_time = {}

        for dom_id, dom in stats.items():
            cpu_time[dom_id] = dom.get("cpu_time", 0)
            current_cpu_time = cpu_time[dom_id]

            if dom_id in self.last_cpu_time:
                cpu_time[dom_id] -= self.last_cpu_time[dom_id]
                # XXX: why is this needed?
                cpu_time[dom_id] /= int(dom.get("online_vcpus", 1)) or 1

                if cpu_time[dom_id] > cpu_max_time:
                    cpu_max_time = cpu_time[dom_id]
                    cpu_top_dom_id = dom_id

            self.last_cpu_time[dom_id] = current_cpu_time

        log.debug(
            "VCPU time: last: %s max: %s top dom: %s ts: %s last ts: %s",
            self.last_cpu_time,
            cpu_max_time,
            cpu_top_dom_id,
            ts,
            self._last_ts,
        )
        self._last_ts["vcpu"], last_ts = ts, self._last_ts.get("vcpu")

        if last_ts is None or cpu_top_dom_id is None:  # First time: no data
            return None

        cpu_share = {dom_id: tm / (ts - last_ts) / 1e9 for dom_id, tm in cpu_time.items()}
        cpu_max_share = max(cpu_share.values())
        cpu_top_dom_name = si.get_domain_name(cpu_top_dom_id).decode()

        log.debug("vcpu: max: share:%s dom:%s", cpu_max_share, cpu_top_dom_name)
        return cpu_max_share, f"[{cpu_top_dom_name}]", cpu_share

    def feed_pcpu(self, si: SysInfo) -> tuple[float, str, dict] | None:
        idletime: dict[int, float] = {}
        stats, ts = si.pcpu_stats

        for cpu_no, pcpu_times in enumerate(stats):
            idletime[cpu_no] = pcpu_times.get("idletime", 0)

            self.last_idle_time[cpu_no], idletime[cpu_no] = (
                idletime[cpu_no],
                idletime[cpu_no] - self.last_idle_time.get(cpu_no, idletime[cpu_no]),
            )

        self._last_ts["pcpu"], last_ts = ts, self._last_ts.get("pcpu")

        log.debug("pcpu: idle: %s ts: %s last ts: %s", idletime, ts, last_ts)
        if last_ts is None:  # First time: no data
            return None

        cpu_share = {
            cpu_no: 1.0 - tm / (ts - last_ts) / 1e9 for cpu_no, tm in idletime.items() if tm
        }

        # FIXME: detect fully busy system
        if cpu_share:
            max_share = max(cpu_share.values())
            avg_share = sum(cpu_share.values()) / len(cpu_share)
        else:
            max_share = avg_share = 1.0
        log.debug("pcpu: share: %s avg: %s", cpu_share, avg_share)
        return max_share, f"AVG: {avg_share * 100:.0f}%", cpu_share

    def feed_vram(self, si: SysInfo) -> tuple[float, str, dict[int, float]] | None:
        stats = si.dom_stats_vram
        mem_max = 0
        mem_top_dom_id = None
        active_mem = 0
        dom_mem = {}
        for dom_id, dom in stats.items():
            try:
                dom_mem[dom_id] = int(
                    next((dom[key] for key in ("meminfo", "target") if key in dom), 0)
                )
            except (ValueError, TypeError) as err:
                log.warning("Failed to get VRAM for dom ID=%s [%s]: %s", dom_id, dom, err)
                continue
            active_mem += dom_mem[dom_id]
            if dom_mem[dom_id] > mem_max:
                mem_max = dom_mem[dom_id]
                mem_top_dom_id = dom_id

        if (active_mem == 0) or not (total_mem := si.total_mem):
            log.warning("Error getting mem info")
            return None
        mem_top_dom_name = si.get_domain_name(mem_top_dom_id).decode()
        log.debug("mem: act=%s tot=%s share=%s", active_mem, total_mem, active_mem / total_mem)

        return (
            active_mem / total_mem,
            (
                f"{active_mem / 1024**2:.1f}"
                f" of {total_mem / 1024**2:.1f} GB [{mem_top_dom_name}]"
            ),
            {dom_id: mem / total_mem for dom_id, mem in dom_mem.items()},
        )
