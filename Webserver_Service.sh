#!/bin/bash

# Variables
SERVICE_PATH="/etc/systemd/system/Local_WebServer.service"
SCRIPT_PATH="/root/scripts/webserver.py"

# Create the service file
echo "[Unit]
Description=WebServer Python Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 $SCRIPT_PATH
User=root
Restart=on-failure
RestartSec=30s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target" > $SERVICE_PATH

# Reload the systemd daemon, enable and start the service
systemctl daemon-reload
systemctl enable Local_WebServer.service
systemctl start Local_WebServer.service

echo "Service created and started successfully."
