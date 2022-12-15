#!/bin/bash

cat > VolControl.service << EOF
[Unit]
Description=Wuba Volume Controle Script by Aron
After=multi-user.target

[Service]
Type=simple
User=$(whoami)

Environment="XDG_RUNTIME_DIR="/run/user/1000""
Environment="DBUS_SESSION_BUS_ADDRESS="unix:path=${XDG_RUNTIME_DIR}/bus""

ExecStart=/usr/bin/python3 /usr/local/bin/VolControl.py

[Install]
WantedBy=multi-user.target
EOF


sudo cp ./VolControl.py /usr/local/bin/VolControl.py
sudo cp ./VolControl.service /etc/systemd/system/VolControl.service



