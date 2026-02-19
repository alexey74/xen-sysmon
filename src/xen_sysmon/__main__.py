import logging
import sys

from .icon import Icon
from .settings_manager import SettingsManager


log = logging.getLogger(__name__)


def main():
    if "-d" in sys.argv:
        logging.basicConfig(level=logging.DEBUG)

    config = SettingsManager.from_yaml()
    log.info("Starting...")
    icon = Icon(config)
    icon.run()


if __name__ == "__main__":
    sys.exit(main())
