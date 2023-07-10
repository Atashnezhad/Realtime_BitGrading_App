#!/bin/bash

run-app() {
    uvicorn app.main:app --reload --port 8080
}

stop-port() {
    sudo lsof -t -i tcp:8080 | xargs kill -9
}

# Run the FastAPI application
if [ "$1" = "run-app" ]; then
    run-app
# Stop the process running on port 8080
elif [ "$1" = "stop-port" ]; then
    stop-port
else
    echo "Invalid command. Usage: ./script.sh [run-app|stop-port]"
fi
