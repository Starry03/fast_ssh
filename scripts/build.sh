#!/bin/bash

pyinstaller \
  -n "fast_ssh" \
  --clean \
  --optimize=2 \
  --onefile \
  --hidden-import=loguru \
  --hidden-import=sql.sql_manager \
  --collect-all cryptography \
  main.py
