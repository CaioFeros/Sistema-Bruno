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
if exist dist\Sistema-Bruno.exe (
    copy dist\Sistema-Bruno.exe Sistema-Bruno-Distribuicao\
    echo [OK] Executavel copiado
) else (
    echo [ERRO] Executavel nao encontrado! Execute build_executavel.bat primeiro.
    pause
    exit /b 1
)

REM Copiar requirements.txt (para instalacao manual se necessario)
copy requirements.txt Sistema-Bruno-Distribuicao\
echo [OK] requirements.txt copiado

REM Copiar README
copy README.md Sistema-Bruno-Distribuicao\
echo [OK] README.md copiado

REM Copiar INSTALACAO.md
copy INSTALACAO.md Sistema-Bruno-Distribuicao\
echo [OK] INSTALACAO.md copiado

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
    echo   - Sistema-Bruno.exe (executavel principal)
    echo   - requirements.txt (para instalacao manual)
    echo   - README.md (documentacao completa)
    echo   - INSTALACAO.md (guia de instalacao)
    echo   - README_EXECUTAVEL.md (guia do executavel)
    echo   - LER_PRIMEIRO.txt (guia rapido)
    echo   - Arquivos .py (caso o executavel nao funcione)
    echo.
    echo Pronto para enviar para o GitHub Release ou distribuir!
    echo.
) else (
    echo [ERRO] Falha ao criar ZIP
    echo.
)

pause

