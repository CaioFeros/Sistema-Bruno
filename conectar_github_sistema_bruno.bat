@echo off
echo ========================================
echo Conectar Sistema-Bruno ao GitHub
echo ========================================
echo.
echo Conectando ao repositorio: https://github.com/CaioFeros/Sistema-Bruno.git
echo.

REM Verificar se o repositorio remoto ja existe
git remote get-url origin >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo O repositorio remoto ja esta configurado.
    echo Atualizando URL...
    git remote set-url origin https://github.com/CaioFeros/Sistema-Bruno.git
) else (
    echo Adicionando repositorio remoto...
    git remote add origin https://github.com/CaioFeros/Sistema-Bruno.git
)

echo.
echo Verificando branch atual...
git branch

echo.
echo Renomeando branch para main...
git branch -M main

echo.
echo ========================================
echo IMPORTANTE:
echo ========================================
echo Antes de continuar, certifique-se de que:
echo 1. Voce criou o repositorio no GitHub com o nome "Sistema-Bruno"
echo 2. O repositorio esta VAZIO (sem README, .gitignore, etc)
echo 3. Voce esta autenticado no GitHub
echo.
set /p CONFIRMA="Tudo certo? Pressione ENTER para continuar ou Ctrl+C para cancelar: "

echo.
echo Fazendo push para o GitHub...
echo.

git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCESSO! Codigo enviado para o GitHub
    echo ========================================
    echo.
    echo Seu repositorio esta disponivel em:
    echo https://github.com/CaioFeros/Sistema-Bruno
    echo.
) else (
    echo.
    echo ========================================
    echo ERRO: Nao foi possivel fazer push
    echo ========================================
    echo.
    echo POSSIVEIS SOLUCOES:
    echo.
    echo 1. Verifique se criou o repositorio no GitHub:
    echo    https://github.com/new
    echo.
    echo 2. Verifique sua autenticacao:
    echo    - Use um Personal Access Token como senha
    echo    - Ou configure SSH keys
    echo.
    echo 3. Tente fazer o push manualmente:
    echo    git push -u origin main
    echo.
    echo 4. Se o repositorio ja existe e tem arquivos:
    echo    git pull origin main --allow-unrelated-histories
    echo    git push -u origin main
    echo.
)

pause

