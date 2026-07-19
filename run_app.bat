@echo off
setlocal EnableExtensions EnableDelayedExpansion

title FloodMind AI - Streamlit App

pushd "%~dp0"

echo ============================================
echo Starting FloodMind AI Streamlit App
echo Project folder: !CD!
echo ============================================
echo.

set "VENV_PY=!CD!\.venv\Scripts\python.exe"

if not exist "!VENV_PY!" (
    echo ERROR: .venv Python was not found.
    echo Expected:
    echo !VENV_PY!
    echo.
    echo Please create or fix your virtual environment first.
    pause
    popd
    exit /b 1
)

echo Using Python:
"!VENV_PY!" -c "import sys; print(sys.executable)"
echo.

echo Checking PyTorch...
"!VENV_PY!" -c "import torch; print('PyTorch:', torch.__version__)"
if errorlevel 1 (
    echo.
    echo ERROR: PyTorch is not installed in this .venv.
    echo Install it with:
    echo python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
    echo.
    pause
    popd
    exit /b 1
)

echo.
echo Checking Streamlit...
"!VENV_PY!" -c "import streamlit; print('Streamlit:', streamlit.__version__)"
if errorlevel 1 (
    echo.
    echo ERROR: Streamlit is not installed in this .venv.
    echo Install it with:
    echo python -m pip install streamlit
    echo.
    pause
    popd
    exit /b 1
)

echo.
echo Launching FloodMind AI...
echo.

set "PYTHONPATH=!CD!"

"!VENV_PY!" -m streamlit run app.py --server.port 8501 --server.address localhost --server.fileWatcherType none

echo.
echo FloodMind app has stopped.
pause

popd
endlocal