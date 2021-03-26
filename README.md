# WTStats

## Build Container
```sh
docker build -t falseteam/wtstats .
docker run --name wtstats-instance -v PATH/TO/FOLDER:/opt/wtstats/data falseteam/wtstats
```

## Configuring
After first run container data folder and config file will be created by root. `config.ini` fields:

Section|Name|Description
---|---|---
Miner|id|Etherium ID
Telegram|token|Telegram Bot Token
Telegram|chat_id|Telegram Chat ID

## Systemd
All configs there: `/etc/systemd/system`

### wtstats.service
```editorconfig
[Unit]
Description=Update WTStats

[Service]
Type=oneshot
ExecStart=docker start -a wtstats-instance
```

### wtstats.timer
```editorconfig
[Unit]
Description=Minutely Update WTStats

[Timer]
OnCalendar=minutely
Persistent=true

[Install]
WantedBy=timers.target
```

### Enable & Start
```sh
systemctl enable wtstats.timer
systemctl start wtstats.timer
```
