ARG FEDORA_VER
FROM fedora:${FEDORA_VER}

# Add RPM Fusion
RUN --mount=type=cache,target=/var/cache/dnf\
  dnf install -y \
    https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-"$(rpm -E %fedora)".noarch.rpm \
    && dnf clean all

# Update
RUN dnf update -y && dnf clean all

# Install build dependencies
RUN --mount=type=cache,target=/var/cache/dnf \
  dnf install -y fedpkg fedora-packager rpmdevtools \
    bison flex gcc gcc-c++ gcc-plugin-devel \
    glibc-static hostname m4 make net-tools curl wget \
    perl-generators python3-devel which \
    openssl openssl-devel perl-devel \
    python3-pillow-devel python3-pystray \
    python3-wheel python3-setuptools_scm \
    python3-pyxdg python3-pytest python3-pytest-cov python3-pytest-mock

#RUN dnf install ftp://ftp.icm.edu.pl/vol/rzm5/linux-qubes/repo/yum/r4.2/current-testing/host/fc37/rpm/python3-xen-4.17.6-2.fc37.x86_64.rpm

# RUN dnf repomanage https://yum.qubes-os.org/r$releasever/unstable/host/fc37
# RUN dnf install -y xen-devel

# RUN dnf clean all

# Setup build directory
RUN rpmdev-setuptree

RUN pip install build specfile pyp2spec

# WORKDIR /var/tmp
# COPY requirements*.txt .

# RUN pip install -r requirements.txt -r requirements-dev.txt
