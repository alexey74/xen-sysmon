import logging
import os
import sys

from .app import Application


def main():
    if "-d" in sys.argv:
        logging.basicConfig(level=getattr(logging, os.getenv("LOGLEV", "DEBUG")))

    Application().run()


if __name__ == "__main__":
    sys.exit(main())
