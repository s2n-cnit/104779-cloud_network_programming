#!/bin/bash

rm fa.db
./init_data.py
poetry run pytest -vvvv -x
