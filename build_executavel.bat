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
echo Criando o executavel...
echo.

REM Criar o executavel com PyInstaller
REM Opcao 1: Executavel standalone (inclui Python embutido - arquivo grande ~150MB)
REM Opcao 2: Executavel que requer Python instalado (arquivo menor ~20MB)

echo.
echo Escolha o tipo de executavel:
echo   1 - Standalone (nao precisa Python instalado, arquivo grande ~150MB)
echo   2 - Requer Python (precisa Python instalado, arquivo menor ~20MB)
echo.
set /p TIPO="Digite 1 ou 2 (padrao: 2): "

if "%TIPO%"=="1" (
    echo Criando executavel STANDALONE...
    python -m PyInstaller ^
        --name="Sistema-Bruno" ^
        --onefile ^
        --windowed ^
        --icon=NONE ^
        --add-data "requirements.txt;." ^
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
) else (
    echo Criando executavel que requer Python...
    python -m PyInstaller ^
        --name="Sistema-Bruno" ^
        --onefile ^
        --windowed ^
        --icon=NONE ^
        --add-data "requirements.txt;." ^
        --hidden-import=pdfplumber ^
        --hidden-import=pandas ^
        --hidden-import=openpyxl ^
        --hidden-import=tkinter ^
        --hidden-import=tkinterdnd2 ^
        --noconfirm ^
        iniciar_sistema.py
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCESSO! Executavel criado!
    echo ========================================
    echo.
    echo O executavel esta em: dist\Sistema-Bruno.exe
    echo.
    echo Pronto para distribuir!
    echo.
) else (
    echo.
    echo ERRO: Falha ao criar o executavel
    echo.
)

pause

