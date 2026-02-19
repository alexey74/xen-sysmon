FROM fedora:37

# Add RPM Fusion
RUN dnf install -y \
  https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-"$(rpm -E %fedora)".noarch.rpm \
  https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-"$(rpm -E %fedora)".noarch.rpm \
  && dnf clean all

# Update
RUN dnf update -y && dnf clean all

# Install build dependencies
RUN dnf install -y fedpkg fedora-packager rpmdevtools ncurses-devel pesign \
  bpftool bc bison dwarves elfutils-devel flex gcc gcc-c++ gcc-plugin-devel \
  glibc-static hostname m4 make net-tools curl wget \
  perl-generators python3-devel which \
  openssl openssl-devel perl-devel \
  python3-pyxs python3-pillow-devel python3-pystray python3-wheel

# RUN dnf clean all

# Setup build directory
RUN rpmdev-setuptree

RUN pip install pyp2spec build
