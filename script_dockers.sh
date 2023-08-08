#!/bin/bash

# Configurable variables
IMAGE_NAME="rtbg-app"
CONTAINER_NAME="fastapi-container"

build_image() {
    docker build -t "$IMAGE_NAME" .
}

run_container_fastapi() {
    docker run --name "$CONTAINER_NAME" -p 80:80 -d "$IMAGE_NAME"
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

# Function to remove all Docker images
remove_all_images() {
    docker image rm $(docker image ls -aq)
}

# Check if an argument is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 [build|run|remove|remove-all]"
    exit 1
fi

# Determine which function to call based on the argument
if [ "$1" == "build" ]; then
    build_image
elif [ "$1" == "run" ]; then
    run_container_fastapi
elif [ "$1" == "remove-container" ]; then
    remove_container
elif [ "$1" == "remove-all-imgs" ]; then
    remove_all_images
else
    echo "Invalid argument. Usage: $0 [build|run|remove|remove-all]"
    exit 1
fi

