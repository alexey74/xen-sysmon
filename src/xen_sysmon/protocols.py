from typing import Protocol

from .settings import Settings


class PApplication(Protocol):
    config: Settings

    def run(self):
        ...

    def toggle_auto_start(self, flag: bool):
        ...

    def is_auto_start_enabled(self) -> bool:
        ...

    def edit_settings(self):
        ...

    def save_settings(self):
        ...
