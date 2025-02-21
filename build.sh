#!/usr/bin/env bash

python3 -m pip install -r requirements.txt --target src
python3 -m zipapp -p "interpreter" gen-autorestic-locations
