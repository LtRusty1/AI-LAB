#!/bin/bash
set -e

# Function to check if a service is ready
wait_for_service() {
    local host="$1"
    local port="$2"
    local timeout="${3:-30}"
    
    echo "Waiting for $host:$port..."
    for i in $(seq 1 $timeout); do
        if nc -z "$host" "$port" >/dev/null 2>&1; then
            echo "$host:$port is ready!"
            return 0
        fi
        echo "Waiting for $host:$port... ($i/$timeout)"
        sleep 1
    done
    echo "Timeout waiting for $host:$port"
    return 1
}

# Check for required services
if [ "$1" = "python" ]; then
    # Wait for Redis
    wait_for_service "redis" "6379"
    
    # Wait for Ollama
    wait_for_service "ollama" "11434"
fi

# Execute the command
exec "$@" 