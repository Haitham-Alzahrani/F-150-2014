@echo off
REM One-shot Windows setup.  Run from the repository root:  setup.cmd
REM Verifies as it goes and stops at the first real failure.
setlocal

echo.
echo [1/4] Creating virtual environment...
if not exist .venv (
    py -3 -m venv .venv || python -m venv .venv
)
if not exist .venv\Scripts\python.exe (
    echo FAILED: no .venv\Scripts\python.exe. Is Python 3 installed and on PATH?
    exit /b 1
)

echo [2/4] Installing (this pulls numpy, pyserial and python-obd)...
.venv\Scripts\python.exe -m pip install --quiet --upgrade pip
.venv\Scripts\python.exe -m pip install --quiet -e .
if errorlevel 1 (
    echo FAILED: pip install did not complete.
    exit /b 1
)

echo [3/4] Self-test, no vehicle needed...
.venv\Scripts\python.exe -m f150diag.cli selftest
if errorlevel 1 (
    echo FAILED: selftest did not pass.
    exit /b 1
)

echo [4/4] Exercising the car link against a SIMULATED adapter...
REM cmd has no '&' backgrounding - '&' is a command separator. Use start /B.
start /B "" .venv\Scripts\python.exe data\f150_agent.py --listen 51599 serve --sim > .venv\simcheck.log 2>&1
REM no 'sleep' in cmd either; ping to itself is the standard idiom.
ping -n 3 127.0.0.1 > nul
.venv\Scripts\python.exe data\f150_agent.py --listen 51599 status
.venv\Scripts\python.exe data\f150_agent.py --listen 51599 stop > nul 2>&1

echo.
echo ================================================================
echo  READY.
echo.
echo  Serial ports on this machine:
.venv\Scripts\python.exe data\f150_agent.py ports
echo.
echo  At the truck, ignition ON, then start the link:
echo     .venv\Scripts\python.exe data\f150_agent.py serve --port COM5
echo.
echo  Leave that window open. In ANOTHER window, or from Claude:
echo     .venv\Scripts\python.exe data\f150_agent.py status
echo     .venv\Scripts\python.exe data\f150_agent.py log start park-idle
echo.
echo  Read docs\START-HERE.md
echo ================================================================
endlocal
