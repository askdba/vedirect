#!/bin/bash

# Path to the scripts
script1="/home/pi/vedirect/vedirect_mppt.sh"
script2="/home/pi/vedirect/vedirect.sh"

# Make sure the scripts are executable
chmod +x "$script1"
chmod +x "$script2"

# Infinite loop
while true
do
    # Execute script 1 (vedirect_mppt.sh)
    echo "Running vedirect_mppt.sh"
    "$script1"
    echo "Finished running vedirect_mppt.sh"

    # Wait for 5 minutes
    echo "Waiting for 5 minutes before running next script..."
    sleep 30

    # Execute script 2 (vedirect.sh)
    echo "Running vedirect.sh"
    "$script2"
    echo "Finished running vedirect.sh"

    # Wait for 5 minutes
    echo "Waiting for 5 minutes before restarting the cycle..."
    sleep 300
done
