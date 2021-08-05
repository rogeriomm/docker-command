#!/bin/bash

set -e

TAG=$(git rev-parse --abbrev-ref HEAD)
USER=$USERNAME

build() {
    NAME=$1
    PREFIX=$2

    if [ "$PREFIX" = "" ]; then
      IMAGE=$USER/$NAME:$TAG
    else
      IMAGE=$USER/$PREFIX-$NAME:$TAG
    fi
    cd $([ -z "$4" ] && echo "./$NAME" || echo "$4")
    echo '--------------------------' building $IMAGE in $(pwd)
    echo "docker build -t $IMAGE --build-arg USERNAME=$1 --build-arg TAG=$TAG ."
    docker build -t $IMAGE --build-arg USERNAME=$1 --build-arg TAG=$TAG .
    cd -
}

while getopts u:a:f: flag
do
    case "${flag}" in
        u) USER=${OPTARG};;
        *);;
    esac
done

build command
build tinyproxy

