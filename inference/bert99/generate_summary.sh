#!/bin/bash
#MOVE SCRIPT TO HOME DIRECTORY
#MOVE SCRIPT TO HOME DIRECTORY
#MOVE SCRIPT TO HOME DIRECTORY

PROFILING_DIR=$1

# setup python environment to ensure profiling summary operates as intended
python3 -m venv gbln-py3

./gbln-py3/bin/python -m pip install --upgrade pip
./gbln-py3/bin/python -m pip install pandas==1.5.3 --upgrade --upgrade-strategy only-if-needed
./gbln-py3/bin/python -m pip install numpy==1.24.3 --upgrade --upgrade-strategy only-if-needed

./gbln-py3/bin/python generate_summary.py "$PROFILING_DIR"