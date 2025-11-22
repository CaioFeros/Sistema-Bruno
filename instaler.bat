@echo off
echo ========================================
echo Build do Executavel - Sistema Bruno
echo ========================================
echo.

REM Verificar se PyInstaller esta instalado
python -m pip show pyinstaller >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo PyInstaller nao encontrado. Instalando...
    python -m pip install pyinstaller
    if %ERRORLEVEL% NEQ 0 (
        echo ERRO: Nao foi possivel instalar PyInstaller
        pause
        exit /b 1
    )
)

echo.
echo Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

echo.
echo Criando executavel STANDALONE completo...
echo (Inclui Python embutido - nao precisa Python instalado)
echo.

REM Criar executavel standalone completo com todas as dependencias embutidas
python -m PyInstaller ^
    --name="setup" ^
    --onefile ^
    --windowed ^
    --icon=NONE ^
    --hidden-import=pdfplumber ^
    --hidden-import=pandas ^
    --hidden-import=openpyxl ^
    --hidden-import=tkinter ^
    --hidden-import=tkinterdnd2 ^
    --collect-all=pdfplumber ^
    --collect-all=openpyxl ^
    --collect-all=pandas ^
    --collect-all=tkinter ^
    --noconfirm ^
    iniciar_sistema.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCESSO! Executavel criado!
    echo ========================================
    echo.
    echo O executavel esta em: dist\setup.exe
    echo.
    echo Pronto para distribuir!
    echo.
) else (
    echo.
    echo ERRO: Falha ao criar o executavel
    echo.
)

pause

