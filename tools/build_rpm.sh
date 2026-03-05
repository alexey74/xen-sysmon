#!/bin/sh

set -xe

python3 -m build
pyp2spec -a xen_sysmon --path ./dist
python3 tools/tweak_spec.py *.spec
cp *.spec /root/rpmbuild/SPECS
cp dist/*.tar.gz /root/rpmbuild/SOURCES
rpmbuild -bb *.spec
