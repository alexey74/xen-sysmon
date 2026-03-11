ARG FEDORA_VER=37
FROM fedora:${FEDORA_VER}

WORKDIR /

# Add RPM Fusion
RUN --mount=type=cache,target=/var/cache/dnf\
  dnf install -y \
    https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-"$(rpm -E %fedora)".noarch.rpm \
    && dnf clean all

# Update
RUN dnf update -y && dnf clean all

# Install build dependencies
# hadolint ignore=DL3040,DL3041
RUN --mount=type=cache,target=/var/cache/dnf \
  dnf install -y fedpkg fedora-packager rpmdevtools \
    bison flex gcc gcc-c++ gcc-plugin-devel \
    glibc-static hostname m4 make net-tools curl wget \
    perl-generators python3-devel which \
    openssl openssl-devel perl-devel \
    python3-pillow-devel python3-pystray \
    python3-wheel python3-setuptools_scm \
    python3-pyxdg python3-pytest python3-pytest-cov python3-pytest-mock

# Setup build directory
RUN rpmdev-setuptree
# hadolint ignore=DL3013,DL3059
RUN pip install --no-cache-dir build specfile pyp2spec uv

COPY . /src

WORKDIR /src

CMD [ "/bin/sh", "/src/tools/build_rpm.sh"]
