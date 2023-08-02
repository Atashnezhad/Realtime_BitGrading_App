#!/bin/bash

# Configurable variables
IMAGE_NAME="rtbg-app"
CONTAINER_NAME="fastapi-container"

build_image() {
    docker build -t "$IMAGE_NAME" .
}

run_container_fastapi() {
    # Generate a random container name using 'date' and 'md5sum'
    container_name="${CONTAINER_NAME}-$(date | md5sum | head -c 10)"

    docker run --name "$container_name" -p 80:80 -d "$IMAGE_NAME"
}

remove_container() {
    # Check if the container is running before removing it
    if docker ps -a --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
        docker stop "$CONTAINER_NAME"
        docker rm "$CONTAINER_NAME"
    else
        echo "Container '$CONTAINER_NAME' not found or already removed."
    fi
}

# Check if an argument is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 [build|run|remove]"
    exit 1
fi

# Determine which function to call based on the argument
if [ "$1" == "build" ]; then
    build_image
elif [ "$1" == "run" ]; then
    run_container_fastapi
elif [ "$1" == "remove" ]; then
    remove_container
else
    echo "Invalid argument. Usage: $0 [build|run|remove]"
    exit 1
fi
