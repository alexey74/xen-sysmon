# Xen System Monitor

GUI system resources monitor for Xen-based systems residing in the system tray.

Designed to run in dom0 as a system tray icon using `pystray` for cross-GUI compatibility.

Tested on Qubes OS 4.2 but should work in other environments as well.

## Installation

### Fedora-based dom0

If dom0 is based on Fedora, you can build an RPM on any system with working `podman`:

 * Install `podman` and `podman-compose`
 * Clone this repo and `cd` to it
 * Run `make rpm FEDORA_VER=${YOUR_DOM0_FEDORA_VERSION}`
 * Copy resulting `.rpmbuild/RPMS/noarch/python3-xen-sysmon-*.noarch.rpm` to your dom0 
 * Install it with `sudo dnf install python3-xen-sysmon-*.noarch.rpm`

### Other dom0 (networked)

You can install this app as a regular python app using e.g. `pipx install .`

### Other dom0 (non-networked)

The app can be installed from wheels:

 * Install `podman` and `podman-compose`
 * Clone this repo and `cd` to it
 * Run `make wheel`
 * Copy resulting `dist/*` to your dom0
 * Install it there with `pipx`:
    `pipx install --system-site-packages --pip-args='--no-index --find-links=.'  xen-sysmon`
