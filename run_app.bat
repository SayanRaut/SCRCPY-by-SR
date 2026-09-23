@echo off
title SCRCPY by Sneak
echo Launching SCRCPY by Sneak Controller...
python app.py
if %errorlevel% neq 0 (
    echo.
    echo Application exited with error code %errorlevel%.
    pause
)
