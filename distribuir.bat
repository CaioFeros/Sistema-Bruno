@echo off
echo ========================================
echo Preparar Distribuicao do Sistema
echo ========================================
echo.

REM Criar pasta de distribuicao
if exist Sistema-Bruno-Distribuicao rmdir /s /q Sistema-Bruno-Distribuicao
mkdir Sistema-Bruno-Distribuicao

echo Copiando arquivos necessarios...

REM Copiar arquivos do sistema
copy main.py Sistema-Bruno-Distribuicao\
copy pdf_extractor.py Sistema-Bruno-Distribuicao\
copy data_processor.py Sistema-Bruno-Distribuicao\
copy excel_exporter.py Sistema-Bruno-Distribuicao\
copy iniciar_sistema.py Sistema-Bruno-Distribuicao\
copy requirements.txt Sistema-Bruno-Distribuicao\
copy instalar_sistema.bat Sistema-Bruno-Distribuicao\
copy INSTRUCOES_INSTALACAO.txt Sistema-Bruno-Distribuicao\
echo [OK] Arquivos do sistema copiados

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
    echo   - instalar_sistema.bat (instalador - execute este arquivo)
    echo   - INSTRUCOES_INSTALACAO.txt (instrucoes completas)
    echo   - Arquivos .py do sistema
    echo   - requirements.txt (dependencias)
    echo.
    echo O usuario deve executar instalar_sistema.bat para instalar!
    echo O instalador configura tudo automaticamente.
    echo.
) else (
    echo [ERRO] Falha ao criar ZIP
    echo.
)

pause

