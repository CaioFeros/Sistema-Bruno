@echo off
echo ========================================
echo Preparar Distribuicao do Sistema
echo ========================================
echo.

REM Criar pasta de distribuicao
if exist Sistema-Bruno-Distribuicao rmdir /s /q Sistema-Bruno-Distribuicao
mkdir Sistema-Bruno-Distribuicao

echo Copiando arquivos necessarios...

REM Copiar pasta do executavel (nao e mais onefile)
if exist dist\setup (
    xcopy /E /I /Y dist\setup Sistema-Bruno-Distribuicao\setup
    echo [OK] Pasta do executavel copiada
) else (
    echo [ERRO] Pasta do executavel nao encontrada! Execute instaler.bat primeiro.
    pause
    exit /b 1
)

REM Copiar arquivo de instrucoes
if exist COMO_USAR.txt (
    copy COMO_USAR.txt Sistema-Bruno-Distribuicao\
    echo [OK] COMO_USAR.txt copiado
) else (
    echo [AVISO] COMO_USAR.txt nao encontrado
)

echo.
echo ========================================
echo Criando ZIP para distribuicao...
echo ========================================
echo.

REM Criar arquivo ZIP
powershell -Command "Compress-Archive -Path 'Sistema-Bruno-Distribuicao\*' -DestinationPath 'Sistema-Bruno-Distribuicao.zip' -Force"

if %ERRORLEVEL% EQU 0 (
    echo [OK] ZIP criado com sucesso: Sistema-Bruno-Distribuicao.zip
    echo.
    echo Pronto para distribuir!
    echo.
    echo Contem:
    echo   - setup\ (pasta com executavel e dependencias)
    echo     - setup.exe (executavel principal)
    echo   - COMO_USAR.txt (instrucoes de uso)
    echo.
    echo O executavel e standalone e funciona sozinho!
    echo Nao precisa instalar nada, apenas copiar e executar.
    echo.
) else (
    echo [ERRO] Falha ao criar ZIP
    echo.
)

pause

