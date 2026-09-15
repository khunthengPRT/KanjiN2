@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

rem  Starts 語彙練習帳 on Windows. No Git Bash needed.
rem
rem    SETUP.cmd              start on the first free port from 8788
rem    SETUP.cmd --port 9000  start on a port you choose
rem    SETUP.cmd --phone      let your phone on the same wifi connect (https)
rem    SETUP.cmd --no-open    don't launch a browser
rem
rem  Close this window or press Ctrl-C to stop.

chcp 65001 >nul 2>&1

echo.
echo   Goi Renshucho -- N2 Vocabulary Practice
echo   Setting things up...
echo.

rem --- the app files must be next to this script ---------------
if not exist "index.html" goto :nofiles
if not exist "server.py"  goto :nofiles
echo   [ok] Found the app files

rem --- find a Python that is actually Python --------------------
rem  "python" on a clean Windows is often a Microsoft Store stub that opens
rem  the Store and exits, so test each candidate by running it.
set "PY="
for %%C in ("py -3" "python" "python3") do (
  if not defined PY (
    %%~C -c "import sys; sys.exit(0 if sys.version_info>=(3,8) else 1)" >nul 2>&1
    if !errorlevel! equ 0 set "PY=%%~C"
  )
)
if not defined PY goto :nopython

for /f "delims=" %%V in ('%PY% --version 2^>^&1') do set "PYVER=%%V"
echo   [ok] Using !PYVER!

rem --- pass our flags through, translating --phone --------------
set "ARGS=--auto-port --open"
set "PHONE="
:parse
if "%~1"=="" goto :run
if /i "%~1"=="--phone"    ( set "ARGS=!ARGS! --host 0.0.0.0" & set "PHONE=1" & shift & goto :parse )
if /i "%~1"=="--no-open"  ( set "ARGS=!ARGS:--open=!" & shift & goto :parse )
if /i "%~1"=="--no-https" ( set "ARGS=!ARGS! --no-https" & shift & goto :parse )
if /i "%~1"=="--port"     ( set "ARGS=!ARGS! --port %~2" & shift & shift & goto :parse )
if /i "%~1"=="--help"     goto :help
if /i "%~1"=="-h"         goto :help
echo.
echo   [x] Unknown option: %~1   ^(try SETUP.cmd --help^)
echo.
exit /b 1

:run
if not exist "data" mkdir "data"
echo   [ok] Your data will be saved in %CD%\data
if defined PHONE (
  echo.
  echo   Windows will ask whether to allow Python through the firewall.
  echo   Tick "Private networks" and allow it, or your phone cannot connect.
  echo   Anyone on this wifi can read and change your data -- trusted networks only.
)
echo.
echo   Press Ctrl-C in this window when you are done studying.
echo.

%PY% server.py !ARGS!
set "RC=%errorlevel%"
if not "%RC%"=="0" (
  echo.
  echo   The server stopped with exit code %RC%.
  echo   Scroll up for the reason, then close this window.
  pause >nul
)
exit /b %RC%

:help
echo.
echo   SETUP.cmd              start on the first free port from 8788
echo   SETUP.cmd --port 9000  start on a port you choose
echo   SETUP.cmd --phone      let your phone on the same wifi connect ^(https^)
echo   SETUP.cmd --no-open    don't launch a browser
echo.
exit /b 0

:nofiles
echo.
echo   [x] Can't find index.html and server.py next to this script.
echo       Keep SETUP.cmd in the same folder as the rest of the app.
echo.
pause >nul
exit /b 1

:nopython
echo.
echo   [x] Python 3.8 or newer is required, and I couldn't find it.
echo.
echo       Install it from https://www.python.org/downloads/
echo       During setup, tick "Add python.exe to PATH".
echo.
echo       If you typed "python" before and the Microsoft Store opened,
echo       that is a placeholder, not Python. Install from the link above,
echo       or turn the stub off in Settings ^> Apps ^> App execution aliases.
echo.
echo       Then run SETUP.cmd again.
echo.
pause >nul
exit /b 1
