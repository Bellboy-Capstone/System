#! /bin/sh

# Script to start the Bellboy system at boot.

echo "Check credentials file"
touch bellboy-credentials.obj

echo "Starting Bellboy"
python3 bellboy/main.py -l DEBUG
