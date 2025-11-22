#!/bin/bash

echo "========================================"
echo "Build do Executável - Sistema Bruno"
echo "========================================"
echo ""

# Verificar se PyInstaller está instalado
if ! python3 -m pip show pyinstaller &> /dev/null; then
    echo "PyInstaller não encontrado. Instalando..."
    python3 -m pip install pyinstaller
    if [ $? -ne 0 ]; then
        echo "ERRO: Não foi possível instalar PyInstaller"
        exit 1
    fi
fi

echo ""
echo "Limpando builds anteriores..."
rm -rf build dist *.spec

echo ""
echo "Criando o executável..."
echo ""

# Criar o executável com PyInstaller
python3 -m PyInstaller \
    --name="setup" \
    --onefile \
    --windowed \
    --add-data "requirements.txt:." \
    --hidden-import=pdfplumber \
    --hidden-import=pandas \
    --hidden-import=openpyxl \
    --hidden-import=tkinter \
    --hidden-import=tkinterdnd2 \
    --collect-all=pdfplumber \
    --collect-all=openpyxl \
    iniciar_sistema.py

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "SUCESSO! Executável criado!"
    echo "========================================"
    echo ""
    echo "O executável está em: dist/setup"
    echo ""
    echo "Pronto para distribuir!"
    echo ""
else
    echo ""
    echo "ERRO: Falha ao criar o executável"
    echo ""
    exit 1
fi

