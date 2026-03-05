#!/usr/bin/env python
"""
Tweak .spec file
"""

import sys

from specfile import Specfile
from specfile.tags import Comments
from specfile.tags import Tag


REQUIRES = "python3 python3-pystray python3-pillow python3-pyxdg"

with Specfile(sys.argv[1]) as specfile:
    specfile.bump_release()

    with specfile.tags() as tags:
        tags.insert(1, Tag("Requires", REQUIRES, ": ", Comments()))
        tags.buildrequires.value += " " + REQUIRES

    with specfile.sections() as sections:
        files = sections.get_or_create("files -n python3-xen-sysmon -f %{pyproject_files}")
        files += [
            "%doc README.*",
            "%license LICENSE",
            "%{_datadir}/applications/xen-sysmon.desktop",
        ]
        sections.install += [
            "mkdir -p %{buildroot}/%{_datadir}/applications",
            "install -o root -g root -m 0644 "
            "./src/xen_sysmon/data/xen-sysmon.desktop %{buildroot}/%{_datadir}/applications/",
        ]
        sections.check = ["export NO_PYXEN=1", "%pytest --cache-clear tests/"]
