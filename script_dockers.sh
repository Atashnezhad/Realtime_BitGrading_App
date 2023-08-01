#!/bin/bash

build_image() {
    docker build -t rtbg-app .
}

run_container_fastapi() {
    docker run --name fastapi-container -p 80:80 -d rtbg-app
}


