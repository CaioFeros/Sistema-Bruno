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

echo.
echo Criando executavel STANDALONE completo...
echo (Inclui Python embutido - nao precisa Python instalado)
echo.

REM Criar executavel standalone completo com todas as dependencias embutidas
REM Usando --collect-all e --collect-submodules para garantir que tudo seja incluido
REM NAO usando --onefile para evitar problemas com bibliotecas C (numpy/pandas)

REM Atualizar PyInstaller e dependencias para versoes mais recentes
echo Atualizando PyInstaller e dependencias para versoes mais recentes...
python -m pip install --upgrade pyinstaller numpy pandas pdfplumber --quiet

python -m PyInstaller ^
    --name="setup" ^
    --windowed ^
    --icon=NONE ^
    --additional-hooks-dir=hooks ^
    --collect-binaries=openpyxl ^
    --hidden-import=pandas ^
    --hidden-import=numpy ^
    --hidden-import=numpy.core ^
    --hidden-import=numpy.core._multiarray_umath ^
    --hidden-import=numpy.core.multiarray ^
    --hidden-import=numpy.core.umath ^
    --hidden-import=numpy.linalg ^
    --hidden-import=numpy.linalg.lapack_lite ^
    --hidden-import=numpy.linalg._umath_linalg ^
    --hidden-import=numpy.random ^
    --hidden-import=numpy.random.mtrand ^
    --hidden-import=numpy.random._common ^
    --hidden-import=numpy.random.bit_generator ^
    --hidden-import=numpy.random._generator ^
    --hidden-import=numpy.fft ^
    --hidden-import=numpy.ma ^
    --hidden-import=numpy.ma.core ^
    --hidden-import=numpy.compat ^
    --hidden-import=numpy.compat.py3k ^
    --hidden-import=pandas._libs ^
    --hidden-import=pandas._libs.tslibs.timedeltas ^
    --hidden-import=pandas._libs.tslibs.nattype ^
    --hidden-import=pandas._libs.tslibs.np_datetime ^
    --hidden-import=pandas._libs.tslibs.tzconversion ^
    --hidden-import=pandas._libs.skiplist ^
    --hidden-import=pandas._libs.writers ^
    --hidden-import=pandas._libs.parsers ^
    --hidden-import=pandas._libs.index ^
    --hidden-import=pandas._libs.hashtable ^
    --hidden-import=pandas._libs.reduction ^
    --hidden-import=pandas._libs.groupby ^
    --hidden-import=pandas._libs.reshape ^
    --hidden-import=pandas._libs.sparse ^
    --hidden-import=pandas._libs.ops ^
    --hidden-import=pandas._libs.missing ^
    --hidden-import=pandas._libs.lib ^
    --hidden-import=pandas._libs.tslib ^
    --hidden-import=pandas._libs.tslibs.base ^
    --hidden-import=pandas._libs.tslibs.conversion ^
    --hidden-import=pandas._libs.tslibs.fields ^
    --hidden-import=pandas._libs.tslibs.offsets ^
    --hidden-import=pandas._libs.tslibs.parsing ^
    --hidden-import=pandas._libs.tslibs.period ^
    --hidden-import=pandas._libs.tslibs.timedeltas ^
    --hidden-import=pandas._libs.tslibs.timestamps ^
    --hidden-import=pandas._libs.tslibs.vectorized ^
    --hidden-import=pandas._libs.window.aggregations ^
    --hidden-import=pandas._libs.window.indexers ^
    --hidden-import=pandas._libs.join ^
    --hidden-import=pandas._libs.algos ^
    --hidden-import=pandas._libs.internals ^
    --hidden-import=pandas._libs.internals.blocks ^
    --hidden-import=pandas._libs.arrays ^
    --hidden-import=pandas._libs.properties ^
    --hidden-import=pandas._libs.ops_dispatch ^
    --hidden-import=pdfplumber ^
    --hidden-import=pdfplumber.cli ^
    --hidden-import=pdfplumber.ctm ^
    --hidden-import=pdfplumber.display ^
    --hidden-import=pdfplumber.layout ^
    --hidden-import=pdfplumber.page ^
    --hidden-import=pdfplumber.pdf ^
    --hidden-import=pdfplumber.table ^
    --hidden-import=pdfplumber.utils ^
    --hidden-import=openpyxl ^
    --hidden-import=tkinter ^
    --hidden-import=tkinterdnd2 ^
    --hidden-import=pytz ^
    --hidden-import=dateutil ^
    --hidden-import=dateutil.parser ^
    --hidden-import=dateutil.relativedelta ^
    --hidden-import=dateutil.tz ^
    --collect-all=pdfplumber ^
    --collect-all=pdfminer ^
    --collect-all=PIL ^
    --collect-submodules=pdfplumber ^
    --collect-submodules=pdfminer ^
    --collect-all=openpyxl ^
    --collect-all=pandas ^
    --collect-all=numpy ^
    --collect-all=tkinter ^
    --collect-all=pytz ^
    --collect-all=dateutil ^
    --collect-submodules=pandas ^
    --collect-submodules=numpy ^
    --collect-submodules=openpyxl ^
    --collect-data=pandas ^
    --collect-data=numpy ^
    --collect-binaries=numpy ^
    --collect-binaries=pandas ^
    --noconfirm ^
    iniciar_sistema.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCESSO! Executavel criado!
    echo ========================================
    echo.
    echo A pasta com o executavel esta em: dist\setup
    echo O executavel principal e: dist\setup\setup.exe
    echo.
    echo IMPORTANTE: Mantenha toda a pasta "setup" junta ao distribuir!
    echo.
    echo Pronto para distribuir!
    echo.
) else (
    echo.
    echo ERRO: Falha ao criar o executavel
    echo.
)

pause

