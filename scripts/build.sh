#!/bin/bash

pyinstaller \
  --onefile \
  --hidden-import=loguru \
  --hidden-import=sql.sql_manager \
  --collect-all cryptography \
  main.py
