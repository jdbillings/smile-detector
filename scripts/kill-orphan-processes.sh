#!/bin/bash -e

for service_str in "gunicorn" "react" "npm" "sqlite"; do
    # Check if the service is running
    if pgrep -if "$service_str" > /dev/null; then
        # Kill the process
        pkill -f "$service_str"
        echo "Killed orphan process: $service_str"
    else
        echo "No orphan process found for: $service_str"
    fi
done
