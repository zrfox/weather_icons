@echo off
set VENV_PY=..\..\venv\Scripts\python.exe

"%VENV_PY%" -m watchdog.watchmedo auto-restart --patterns="*.py" --ignore-patterns="*.pyc;__pycache__/*" -- "%VENV_PY%" weather_icons.py
