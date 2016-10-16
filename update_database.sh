#!/bin/bash

if [ ${PWD##*/} != "MYTF1.bundle" ]; then
    echo "Please execute this script at the top level bundle directory"
    exit 1
fi

curl -o Contents/Resources/database.json 'http://api.mytf1.tf1.fr/mobile/init?device=ios-smartphone'

echo "Database updated!"
