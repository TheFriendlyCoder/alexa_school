#!/bin/zsh -e
pushd docker
docker build -t alexa_test .
popd
docker run -it --rm -w /workspace -v "$PWD":/workspace -v "$PWD/ask_config":/root/.ask -v "$PWD/ask_config":/root/.aws alexa_test /bin/bash