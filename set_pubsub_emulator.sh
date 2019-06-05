#!/usr/bin/env bash

touch .env
emulator="export PUBSUB_EMULATOR_HOST=localhost:8538"
if grep -q "$emulator" .env;
  then
    exit 0;
  else
    echo $emulator >> .env;
fi
