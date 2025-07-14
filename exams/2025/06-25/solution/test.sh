#!/bin/bash

rm wr.db
./init_data.py
poetry run pytest -vvvv -x
