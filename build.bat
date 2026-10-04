@echo off
chcp 65001 >nul
title Occlusion Birlestirici - EXE olustur
where py >nul 2>nul
if %errorlevel%==0 (set PY=py) else (set PY=python)

echo [1/2] PyInstaller kuruluyor...
%PY% -m pip install --upgrade pyinstaller
if errorlevel 1 goto hata

echo.
echo [2/2] EXE olusturuluyor...
%PY% -m PyInstaller --onefile --windowed --name OcclusionMerger occlusion_merger_app.py
if errorlevel 1 goto hata

echo.
echo Bitti! Uygulaman burada: dist\OcclusionMerger.exe
pause
exit /b 0

:hata
echo.
echo Bir hata olustu. Yukaridaki mesaji kopyalayip gonder.
pause
exit /b 1
