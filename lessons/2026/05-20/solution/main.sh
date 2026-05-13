#!/bin/bash

rm wr.db
poetry run python ./init_data.py
poetry run python main.py
