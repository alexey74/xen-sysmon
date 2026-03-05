import functools
import logging
import subprocess
import time
import typing as t
from collections.abc import Iterator
from threading import Condition

from PIL import Image
from PIL import ImageDraw
from pystray import Icon as BaseIcon
from pystray import Menu
from pystray import MenuItem

from .common import Bunch
from .feed import FeedMixin
from .protocols import PApplication
from .sysinfo import SysInfo
from .sysinfo import SysInfoError


log = logging.getLogger(__name__)


class Icon(FeedMixin, BaseIcon):  # pylint: disable=abstract-method
    """
    Xen System Monitor Tray Icon
    """

    DOMAIN_ACTIONS = (
        ("Pause", "pause"),
        ("Unpause", "unpause"),
        ("Shutdown", "shutdown"),
        ("Destroy", "destroy"),
    )

    def __init__(self, app: PApplication):
        self.app = app
        self.config = app.config
        self.dom_stats: dict[str, t.Any] = {}
        self.si: SysInfo = None
        self.is_alive = False

        self._updates_enabled_cond = Condition()
        self._updates_enabled = True

        super().__init__(
            name=self.config.name,
            title=self.config.title,
            icon=self.create_image(),
            menu=Menu(self.main_menu_gen),
        )

    def exit(self, *_args):
        self.is_alive = False
        self.stop()

    def run(self, *_args):
        self.is_alive = True
        return super().run(setup=self.update_loop)

    def main_menu_gen(self):
        log.debug("Generating menu...")
        return (
            MenuItem("Domains Monitor", self.main_action, default=True),
            Menu.SEPARATOR,
            *(item for item in self.domains_menu_gen()),
            Menu.SEPARATOR,
            MenuItem("Toggle Updates", lambda _: self.toggle_updates()),
            MenuItem(
                "Settings",
                Menu(
                    MenuItem("Edit", self.app.edit_settings),
                    MenuItem("Save", self.app.save_settings),
                ),
            ),
            # XXX: check menu item broken
            MenuItem(
                "Autostart",
                # self.app.toggle_auto_start,
                # checked=self.app.is_auto_start_enabled,
                Menu(
                    MenuItem(
                        "Enable",
                        lambda: self.app.toggle_auto_start(True),
                        enabled=not self.app.is_auto_start_enabled(),
                    ),
                    MenuItem(
                        "Disable",
                        lambda: self.app.toggle_auto_start(False),
                        enabled=self.app.is_auto_start_enabled(),
                    ),
                ),
            ),
            MenuItem("Exit", self.exit),
        )

    def is_update_enabled(self):
        return self._updates_enabled

    def toggle_updates(self, flag: bool | None = None) -> None:
        log.debug("toggle updates: %s enabled=%s", flag, self._updates_enabled)
        if flag is None:
            self.toggle_updates(not self._updates_enabled)
        else:
            self._updates_enabled = flag
            self.notify(f"Updates {'en' if flag else 'dis'}abled")
            with self._updates_enabled_cond:
                self._updates_enabled_cond.notify_all()

    def domain_menu_gen(self, dom_id: int) -> Iterator[MenuItem]:
        for action in self.DOMAIN_ACTIONS:
            yield MenuItem(action[0], functools.partial(self.domain_action, action[1], dom_id))

    def domain_action(self, action, dom_id, *_args, **_kwargs):
        if not self.si:
            return
        return_code = self.si.domain_action(action, dom_id)
        if return_code != 0:
            log.warning("action %s failed on dom id %s", action, dom_id)
            self.notify(f"Action '{action}' failed on domain ID {dom_id}")

    def domains_menu_gen(self) -> Iterator[str]:
        log.debug("dom stats gen: %s si=%s", self.dom_stats, self.si)
        if self.si is None:
            return
        vcpu = self.dom_stats.get("vcpu", {})
        vram = self.dom_stats.get("vram", {})
        dom_ids = {int(dom_id) for dom_id in list(vcpu.keys()) + list(vram.keys())}
        dom_names = {dom_id: self.si.get_domain_name(dom_id).decode() for dom_id in dom_ids}
        max_name_len = max(len(name) for name in dom_names.values()) + 1

        yield MenuItem(
            f"{'ID':>2}\t{'CPU':>3}\t{'RAM':>3}\t\t{'Domain':<{max_name_len}}", lambda: True
        )

        for dom_id in sorted(dom_ids)[:100]:
            text = f"{dom_id:02}\t"
            if (val := vcpu.get(dom_id)) is not None:
                text += f"{val * 100:02.0f}%\t"
            else:
                text += "????\t"
            if (val := vram.get(dom_id)) is not None:
                text += f"{val * 100:02.0f}%\t"
            else:
                text += "????\t"

            text += f"\t{dom_names[dom_id]:<{max_name_len}}"
            log.debug("dom stats item: %s", text)
            yield MenuItem(text, Menu(*self.domain_menu_gen(dom_id)))

    def main_action(self, icon, item):
        log.debug("main action:%s %s", icon, item)
        self.remove_notification()
        if action := self.config.main_action:
            try:
                with subprocess.Popen(action.split()):
                    pass
            except OSError as err:
                log.warning("Failed to launch default app: %s", err)

    def notify(self, *args, **kw):
        self.remove_notification()
        if self.config.notification:
            super().notify(*args, **kw)

    def header(self, info: dict) -> str:
        b = Bunch(info)

        return (
            f"Xen {b.xen_major}.{b.xen_minor}{b.xen_extra}\n"  # type: ignore[attr-defined]
            f"{b.nr_cpus} CPUs {b.cpu_khz / 1024**2:.1f} GHz\n"  # type: ignore[attr-defined]
            f"{b.free_memory / 1024**2:.1f} of {b.total_memory / 1024**2:.0f} GB free\n"  # type: ignore[attr-defined]
        )

    def update_loop(self, _icon: "Icon") -> None:
        log.debug("loop start")
        while self.is_alive:
            with self._updates_enabled_cond:
                self._updates_enabled_cond.wait_for(self.is_update_enabled)

            with SysInfo() as si:
                self.si = si
                self.remove_notification()
                image = self.create_image()
                barw = self.config.width - 4
                barh = self.config.height // len(self.config.bars) - 2 if self.config.bars else 1
                y = 1
                title = ""
                title += self.header(si.general_info())
                self.dom_stats = {}
                for bar in self.config.bars:  # pylint: disable=disallowed-name
                    log.debug("bar: %s", bar)
                    try:
                        if (result := getattr(self, f"feed_{bar.kind}")(si)) is None:
                            log.debug("skip bar %s draw: no data", bar.kind)
                            y += barh + 1
                            result = 0, "???", {}
                    except (ValueError, AttributeError, SysInfoError) as err:
                        log.warning("Failed to get %s stats: %s", bar.kind, err)
                        self.notify(f"{bar.title}: %s", err)
                        continue

                    fraction, details, self.dom_stats[bar.kind] = result

                    self.draw_progress_bar(
                        image, 1, y, barw - 1, barh, fraction, bg=bar.background, fg=bar.foreground
                    )
                    y += barh + 1
                    title += f"{bar.title}: {fraction * 100:.0f}% {details}\n"

                    if (
                        bar.kind == "vram"
                        and self.config.notification
                        and fraction > self.config.memory_threshold
                    ):
                        self.notify(f"High RAM usage: {fraction * 100:.1f}%")

                self.icon = image.rotate(self.config.rotation_angle)
                self.title = title
                self.update_menu()
                self.visible = True

                si.reset()
                time.sleep(self.config.update_interval)

    def create_image(self) -> t.Any:
        """
        Generate an image
        """
        image = Image.new("RGB", (self.config.width, self.config.height), self.config.background)
        return image

    @staticmethod
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def draw_progress_bar(im, x, y, w, h, percent, bg="black", fg="#faa") -> None:
        draw = ImageDraw.Draw(im, "RGBA")
        draw.rectangle((x, y, x + w, y + h), fill=bg)
        w1 = w * min(percent, 1.0)
        w1 = int(max(w1, 2))
        draw.rectangle((x + 1, y + 1, x + w1 - 1, y + h - 1), fill=fg)
        for i in range(10):
            draw.line((x + i * w // 10, y, x + i * w // 10, y + h), fill=bg, width=1)
