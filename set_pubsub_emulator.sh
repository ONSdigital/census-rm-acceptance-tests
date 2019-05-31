#!/usr/bin/env bash

touch .env
emulator=`gcloud beta emulators pubsub env-init`
if grep -q "$emulator" .env;
  then
    exit 0;
  else
    echo $emulator >> .env;
fi
