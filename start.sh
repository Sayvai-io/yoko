#!/bin/bash

# Start cron service
service cron start

# start the python-cron app, if using python interval
# /GarmentCode/venv/bin/python /GarmentCode/db-backup-cron-app/db-cron.py

# Start the main application using the virtual environment's Python
/GarmentCode/venv/bin/python /GarmentCode/gui.py

# Keep the container running by tailing the cron log
tail -f /var/log/cron.log
