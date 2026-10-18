@echo off
chcp 65001 >nul
rem Запуск IOPaint (LaMa) - убрать мусор с фото кистью. Откроется в браузере: http://localhost:8080
rem Модель и кэш лежат в D:\iopaint-data (латиница: с кириллицей в пути модель не открывается).
set TORCH_HOME=D:\iopaint-data\torch
set HF_HOME=D:\iopaint-data\hf
set HF_HUB_DISABLE_SYMLINKS_WARNING=1
echo Запускаю IOPaint... окно браузера откроется само. Закрыть: Ctrl+C в этом окне.
"%USERPROFILE%\tools\iopaint-env\Scripts\iopaint.exe" start --model=lama --device=cuda --model-dir=D:\iopaint-data --port=8080 --host=127.0.0.1
pause
