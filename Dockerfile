FROM archlinux:base

RUN ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime
RUN pacman -Sy python-pip firefox geckodriver --noconfirm

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY main.py /opt/wtstats/main.py

CMD ["python", "/opt/wtstats/main.py"]
