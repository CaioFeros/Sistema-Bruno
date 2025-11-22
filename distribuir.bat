@echo off
echo ========================================
echo Preparar Distribuicao do Sistema
echo ========================================
echo.

REM Criar pasta de distribuicao
if exist Sistema-Bruno-Distribuicao rmdir /s /q Sistema-Bruno-Distribuicao
mkdir Sistema-Bruno-Distribuicao

echo Copiando arquivos necessarios...

REM Copiar executavel
if exist dist\setup.exe (
    copy dist\setup.exe Sistema-Bruno-Distribuicao\
    echo [OK] Executavel copiado
) else (
    echo [ERRO] Executavel nao encontrado! Execute build_executavel.bat primeiro.
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
    echo   - setup.exe (executavel standalone)
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

