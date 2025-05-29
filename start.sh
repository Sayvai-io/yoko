#!/bin/bash

# Create cron log file if it doesn't exist
touch /var/log/cron.log

# Ensure permissions are correct for the cron job file
chmod 0644 /etc/cron.d/db-backup-cron

# Apply the cron job
crontab /etc/cron.d/db-backup-cron

# Start cron service in the background
service cron start

# Optional: Small delay to ensure cron starts properly
sleep 2

# Change to the GarmentCode directory
cd /GarmentCode

# Start the main application using the virtual environment's Python
/venv/bin/python gui.py
