@echo off
chcp 65001 >nul

if "%~1"=="" goto usage

python "%~dp0nano_batch.py" %*
if errorlevel 1 goto fail
goto end

:usage
echo.
echo   Usage:  nano_batch.bat your_slides.json [options]
echo.
echo   Options:
echo     --output-dir DIR    Output folder (default: output)
echo     --dry-run           Preview commands without generating
echo     --flash             Use faster gemini-2.0-flash model
echo     --model NAME        Specify a model
echo     --prefix NAME       Filename prefix (default: slide)
echo     --start-from N      Skip slides before N
echo.
echo   Example:
echo     nano_batch.bat slides.json --dry-run
echo     nano_batch.bat slides.json --flash --output-dir my_images
echo.
pause
goto end

:fail
echo.
echo [ERROR] Script failed. Make sure Python and nano-banana are installed.
pause

:end
