#!/bin/bash
echo "Starting Motion Controller..."
echo
python3 src/main.py
if [ $? -ne 0 ]; then
    echo
    echo "Error: Failed to start application."
    echo "Make sure all dependencies are installed: pip install -r requirements.txt"
fi

