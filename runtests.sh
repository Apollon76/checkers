#!/bin/bash

python3-coverage erase
python3-coverage run ./test.py
python3-coverage report -m
