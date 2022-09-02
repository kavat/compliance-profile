#!/bin/bash

python3 app.py > ./logs/app.log 2>&1

tail -f /dev/null
