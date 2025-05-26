#!/bin/bash

# Start cron service
service cron start

# Start the main application using the virtual environment's Python
/GarmentCode/venv/bin/python /GarmentCode/gui.py
