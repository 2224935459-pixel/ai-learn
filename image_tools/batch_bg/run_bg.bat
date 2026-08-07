@echo off
chcp 65001 >nul
setlocal
set LOG=C:/Users/22249/Desktop/batch_bg/run_result.log
cls
echo ============================================
echo   Batch BG - auto cutout + bg swap
echo ============================================
echo.
echo  [NOTE] ComfyUI Desktop must be OPEN first!
echo.
echo  Running... log -> run_result.log
echo.
echo [%date% %time%] ===== START ===== > "%LOG%"
C:/Users/22249/AppData/Roaming/uv/python/cpython-3.11-windows-x86_64-none/python.exe C:/Users/22249/Desktop/batch_bg/batch_bg_swap.py >> "%LOG%" 2>&1
echo [%date% %time%] ===== END (exit %errorlevel%) ===== >> "%LOG%"
echo.
echo ============================================
echo  DONE. Results in output folder.
echo  Log saved to run_result.log
echo  Press any key to close.
echo ============================================
pause >nul
