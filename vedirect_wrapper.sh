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
    # Execute script 1 (vedirect_mppt.sh) for 1 minutes
    echo "Running vedirect_mppt.sh"
    timeout 60 "$script1"
    echo "Finished running vedirect_mppt.sh"

    # Wait for 30 seconds
    echo "Waiting for  5 seconds before running the next script..."
    sleep 5

    # Execute script 2 (vedirect.sh) for 2 minutes
    echo "Running vedirect.sh"
    timeout 60 "$script2"
    echo "Finished running vedirect.sh"

    # Wait for 5 seconds
    echo "Waiting for 5 seconds before restarting the cycle..."
    sleep 5
done

