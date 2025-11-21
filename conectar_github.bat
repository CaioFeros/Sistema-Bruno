@echo off
echo ========================================
echo Conectar Repositorio ao GitHub
echo ========================================
echo.
echo Este script vai ajudar voce a conectar seu repositorio local ao GitHub.
echo.
echo ANTES DE CONTINUAR:
echo 1. Crie um repositorio vazio no GitHub com o nome desejado
echo 2. Nao marque "Initialize this repository with a README"
echo 3. Copie a URL do repositorio (ex: https://github.com/USUARIO/NOME-REPO.git)
echo.
set /p GITHUB_URL="Cole a URL do seu repositorio GitHub aqui: "

if "%GITHUB_URL%"=="" (
    echo.
    echo ERRO: URL nao fornecida!
    pause
    exit /b 1
)

echo.
echo Conectando ao repositorio remoto...
git remote add origin %GITHUB_URL%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo AVISO: O repositorio remoto pode ja estar configurado.
    echo Tentando atualizar a URL...
    git remote set-url origin %GITHUB_URL%
)

echo.
echo Verificando branch atual...
git branch

echo.
echo Fazendo push para o GitHub...
git branch -M main
git push -u origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERRO: Nao foi possivel fazer push.
    echo.
    echo POSSIVEIS SOLUCOES:
    echo 1. Verifique se criou o repositorio no GitHub
    echo 2. Verifique sua autenticacao (token de acesso ou credenciais)
    echo 3. Tente fazer o push manualmente:
    echo    git push -u origin main
    echo.
) else (
    echo.
    echo ========================================
    echo SUCESSO! Repositorio conectado ao GitHub
    echo ========================================
    echo.
)

pause

