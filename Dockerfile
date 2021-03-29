FROM archlinux:latest

# Work-around the issue with glibc 2.33 on old Docker engines
# See https://github.com/actions/virtual-environments/issues/2658
# Thanks to https://github.com/lxqt/lxqt-panel/pull/1562
# Extract files directly as pacman is also affected by the issue
RUN curl -sL https://repo.archlinuxcn.org/x86_64/glibc-linux4-2.33-5-x86_64.pkg.tar.zst | \
    tar --zstd -xp -C / --exclude .PKGINFO --exclude .INSTALL --exclude .MTREE --exclude .BUILDINFO

RUN pacman -Syuq --needed --noconfirm --noprogressbar python-pip geckodriver firefox

COPY requirements.txt /tmp/
RUN pip install -q --no-color --no-cache-dir -r /tmp/requirements.txt

RUN ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime

COPY main.py /opt/wtstats/main.py

CMD ["python", "/opt/wtstats/main.py"]
