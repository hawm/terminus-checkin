#!/usr/bin/env bash

set -e 

if [ "$1" == 'bash' ] 
then
    exec "$@"
fi

exec python ./checkin.py "$@"
