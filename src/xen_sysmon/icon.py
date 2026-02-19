import logging
import subprocess
import time

import pystray
from PIL import Image
from PIL import ImageDraw

from .settings import Settings
from .sysinfo import SysInfo


log = logging.getLogger(__name__)


class Icon(pystray.Icon):  # pylint: disable=abstract-method
    """
    Xen System Monitor Tray Icon
    """

    def __init__(self, config: Settings):
        self.config = config

        self.alive = False
        self.last_ts = time.time()
        self.last_cpu_time: dict[int, int] = {}

        super().__init__(
            name=self.config.name,
            title=self.config,
            icon=self.create_image(),
            menu=pystray.Menu(
                pystray.MenuItem(self.config.name, self.main_action, default=True),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit", self.exit),
            ),
        )
        self.visible = True

    def exit(self, *args):
        self.alive = False
        self.stop()

    def run(self, *args):
        self.alive = True
        return super().run(setup=self.update_loop)

    def main_action(self, icon, item):
        log.debug("main action")
        self.remove_notification()
        if action := self.config.main_action:
            try:
                subprocess.Popen(action)
            except OSError as err:
                log.warning("Failed to launch default app: %s", err)

    def notify(self, *args, **kw):
        self.remove_notification()
        if self.config.notification:
            return super().notify(*args, **kw)

    @staticmethod
    def _get_dom_name(stats, dom_id):
        try:
            return stats[dom_id]["name"]
        except KeyError:
            return "Unknown"

    def _feed_cpu(self, si: SysInfo) -> tuple[float, str] | None:
        stats = si.dom_stats
        cpu_time = {}
        cpu_time_max = 0
        cpu_top_dom_id = None

        if not self.last_cpu_time:
            return None

        for dom_id, dom in stats.items():
            cpu_time[dom_id] = dom.get("cpu_time", 0)
            last_cpu_time_ = cpu_time[dom_id]
            cpu_time[dom_id] -= self.last_cpu_time.get(dom_id, 0)
            self.last_cpu_time[dom_id] = last_cpu_time_
            cpu_time[dom_id] /= int(dom.get("online_vcpus", 1)) or 1

            if cpu_time[dom_id] > cpu_time_max:
                cpu_time_max = cpu_time[dom_id]
                cpu_top_dom_id = dom_id

        cpu_max_share = cpu_time_max / (si.ts - self.last_ts) / 10e9
        cpu_top_dom_name = self._get_dom_name(stats, cpu_top_dom_id)

        log.debug("cpu: max: share:%s dom:%s", cpu_max_share, cpu_top_dom_name)
        return cpu_max_share, f"[{cpu_top_dom_name}]"

    def _feed_ram(self, si: SysInfo) -> tuple[float, str] | None:
        stats = si.dom_stats
        mem_max = 0
        mem_top_dom_id = None
        act = 0
        for _dom_id, dom in stats.items():
            act += dom.get("meminfo", dom.get("target", 0))
            if act > mem_max:
                mem_max = act
                mem_top_dom_id = _dom_id

        if act == 0 or not (total_mem := si.total_mem):
            raise ValueError("Error getting info")
        mem_top_dom_name = self._get_dom_name(stats, mem_top_dom_id)
        log.debug("mem: act=%s tot=%s share=%s", act, total_mem, act / total_mem)

        if self.config.notification and act / total_mem > self.config.memory_threshold:
            self.notify(f"High RAM usage: {act / total_mem * 100:.1f}%")

        return (
            act / total_mem,
            f"{act / total_mem * 100:.1f}% {act / 1024**2:.1f}"
            f" of {total_mem / 1024**2:.1f} GB [{mem_top_dom_name}]",
        )

    def update_loop(self, _icon):
        si = SysInfo()
        self.last_ts = time.time()

        log.debug("loop start")
        while self.alive:
            time.sleep(self.config["interval"])
            self.remove_notification()
            image = self.create_image()
            barw = self.config.width - 4
            barh = self.config.height // len(self.config.bars) - 2
            y = 1
            title = ""
            for bar_type, bar_conf in self.config.bars.items():
                try:
                    if (result := getattr(self, f"_feed_{bar_type}")(si)) is None:
                        continue
                except ValueError as err:
                    log.warning("Failed to get %s stats: %s", bar_type, err)
                    self.notify(f"{bar_conf.title}: %s", err)
                    continue

                fraction, details = result
                self.draw_progress_bar(
                    image,
                    1,
                    y,
                    barw - 1,
                    barh,
                    fraction,
                    bg=bar_conf.background,
                    fg=bar_conf.foreground,
                )
                y += barh + 1
                title += f"{bar_conf.title}: {fraction * 100:.0f}% {details}\n"

            self.last_ts = si.ts
            self.icon = image
            self.title = title

            si.reset()

    def create_image(self):
        """
        Generate an image
        """
        image = Image.new("RGB", (self.width, self.height), self.colors["bg"]).rotate(
            self.config["rot_angle"]
        )
        return image

    @staticmethod
    def draw_progress_bar(im, x, y, w, h, percent, bg="black", fg="#faa"):
        draw = ImageDraw.Draw(im, "RGBA")
        draw.rectangle((x, y, x + w, y + h), fill=bg)
        w *= percent
        w = int(max(w, 2))
        draw.rectangle((x + 1, y + 1, x + w - 1, y + h - 1), fill=fg)
