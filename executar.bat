@echo off
echo ========================================
echo Sistema de Extração de Recibos PDF
echo ========================================
echo.
echo Iniciando o sistema...
echo.

python main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERRO: O programa nao pode ser executado.
    echo Verifique se o Python esta instalado e se todas as dependencias estao instaladas.
    echo.
    echo Para instalar as dependencias, execute:
    echo pip install -r requirements.txt
    echo.
    pause
)
