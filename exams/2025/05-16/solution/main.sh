#!/bin/bash

rm fa.db
poetry run python ./init_data.py
poetry run python main.py
