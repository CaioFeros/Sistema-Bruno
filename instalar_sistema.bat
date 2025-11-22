@echo off
echo ========================================
echo INSTALADOR - Sistema de Extracao de Recibos PDF
echo ========================================
echo.

REM Verificar se Python esta instalado
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo Por favor, instale Python 3.8 ou superior de:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Marque a opcao "Add Python to PATH" durante a instalacao!
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version
echo.

REM Verificar versao do Python
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Versao do Python: %PYTHON_VERSION%
echo.

REM Instalar/atualizar dependencias
echo Instalando dependencias...
echo.
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Falha ao instalar dependencias
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Dependencias instaladas com sucesso!
echo.

REM Criar atalho na area de trabalho
echo Criando atalho na area de trabalho...
set SCRIPT_DIR=%~dp0
set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT=%DESKTOP%\Sistema Bruno.lnk

REM Usar PowerShell para criar atalho (usar iniciar_sistema.py para verificacoes automaticas)
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = 'python'; $Shortcut.Arguments = '\"%~dp0iniciar_sistema.py\"'; $Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; $Shortcut.IconLocation = 'python.exe,0'; $Shortcut.Description = 'Sistema de Extracao de Recibos PDF'; $Shortcut.Save()"

if %ERRORLEVEL% EQU 0 (
    echo [OK] Atalho criado na area de trabalho
) else (
    echo [AVISO] Nao foi possivel criar atalho automaticamente
)

echo.
echo ========================================
echo INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo O sistema esta pronto para uso!
echo.
echo Voce pode executar de tres formas:
echo   1. Clique duas vezes no atalho "Sistema Bruno" na area de trabalho
echo   2. Execute: python iniciar_sistema.py (recomendado - faz verificacoes automaticas)
echo   3. Execute: python main.py
echo.
pause

