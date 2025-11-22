@echo off
echo ========================================
echo Testar Executavel - Sistema Bruno
echo ========================================
echo.

REM Verificar se o executavel foi criado
if not exist dist\setup\setup.exe (
    echo [ERRO] Executavel nao encontrado!
    echo Execute instaler.bat primeiro para criar o executavel.
    echo.
    pause
    exit /b 1
)

echo Verificando estrutura do executavel...
echo.

REM Verificar se a pasta _internal existe
if exist dist\setup\_internal (
    echo [OK] Pasta _internal encontrada
    echo.
    echo Verificando dependencias na pasta _internal...
    echo.
    
    REM Verificar numpy
    if exist dist\setup\_internal\numpy (
        echo [OK] numpy encontrado
    ) else (
        echo [ERRO] numpy NAO encontrado em _internal!
    )
    
    REM Verificar pandas
    if exist dist\setup\_internal\pandas (
        echo [OK] pandas encontrado
    ) else (
        echo [ERRO] pandas NAO encontrado em _internal!
    )
    
    REM Verificar pdfplumber
    if exist dist\setup\_internal\pdfplumber (
        echo [OK] pdfplumber encontrado
    ) else (
        echo [ERRO] pdfplumber NAO encontrado em _internal!
    )
    
    REM Verificar openpyxl
    if exist dist\setup\_internal\openpyxl (
        echo [OK] openpyxl encontrado
    ) else (
        echo [AVISO] openpyxl nao encontrado (pode ser opcional)
    )
    
    echo.
    echo Listando conteudo da pasta _internal (primeiros 20 itens):
    echo ----------------------------------------
    dir /b dist\setup\_internal | head -n 20
    echo.
    
) else (
    echo [ERRO] Pasta _internal NAO encontrada!
    echo O executavel pode estar incompleto.
    echo.
)

echo.
echo ========================================
echo Testando execucao do programa...
echo ========================================
echo.
echo IMPORTANTE: O programa sera aberto agora.
echo Feche o programa normalmente para finalizar o teste.
echo.
pause

REM Executar o programa
cd dist\setup
start setup.exe
cd ..\..

echo.
echo ========================================
echo Teste concluido!
echo ========================================
echo.
echo Se o programa abriu e funcionou corretamente, esta pronto para distribuir.
echo Se houver erros, verifique as mensagens acima.
echo.
pause

