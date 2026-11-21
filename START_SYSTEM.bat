@echo off
title NEXTRAFFX - Intelligent Traffic Management System
color 0B
echo =====================================================================
echo                NEXTRAFFX - INTELLIGENT TRAFFIC OS
echo              Multi-City Production Architecture (Python 3.13)
echo =====================================================================
echo.
cd /d "%~dp0"

echo [1/2] Checking Python virtual environment...
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at .venv\Scripts\python.exe
    pause
    exit /b 1
)

echo [2/2] Discovering available network port and launching application...
echo.
".venv\Scripts\python.exe" launcher.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo Server stopped or encountered an issue.
    pause
)
