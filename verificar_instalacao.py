#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar se todas as dependências estão instaladas corretamente.
Execute este script antes de usar o programa pela primeira vez.
"""

import sys

def verificar_python():
    """Verifica a versão do Python."""
    print("=" * 60)
    print("VERIFICAÇÃO DE INSTALAÇÃO")
    print("=" * 60)
    print()
    
    versao = sys.version_info
    print(f"[OK] Python {versao.major}.{versao.minor}.{versao.micro} encontrado")
    
    if versao.major < 3 or (versao.major == 3 and versao.minor < 8):
        print("[X] ERRO: Python 3.8 ou superior e necessario!")
        print(f"  Versao atual: {versao.major}.{versao.minor}")
        return False
    else:
        print("  Versao compativel!")
        return True

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas."""
    print()
    print("Verificando dependências...")
    print("-" * 60)
    
    dependencias = {
        'tkinter': 'Interface gráfica (geralmente já incluído)',
        'pdfplumber': 'Extração de dados de PDFs',
        'pandas': 'Manipulação de dados',
        'openpyxl': 'Exportação para Excel',
        'tkinterdnd2': 'Drag and drop (opcional)'
    }
    
    todas_ok = True
    opcionais_ok = True
    
    for modulo, descricao in dependencias.items():
        try:
            if modulo == 'tkinter':
                import tkinter
                print(f"[OK] {modulo:15} - {descricao}")
            elif modulo == 'tkinterdnd2':
                try:
                    import tkinterdnd2
                    print(f"[OK] {modulo:15} - {descricao}")
                except ImportError:
                    print(f"[--] {modulo:15} - {descricao} (OPCIONAL - nao instalado)")
                    opcionais_ok = False
                    continue
            else:
                __import__(modulo)
                print(f"[OK] {modulo:15} - {descricao}")
        except ImportError:
            print(f"[X] {modulo:15} - {descricao} (NAO INSTALADO)")
            if modulo != 'tkinterdnd2':
                todas_ok = False
    
    print("-" * 60)
    
    return todas_ok, opcionais_ok

def verificar_arquivos():
    """Verifica se todos os arquivos necessários estão presentes."""
    print()
    print("Verificando arquivos do programa...")
    print("-" * 60)
    
    arquivos_necessarios = [
        'main.py',
        'pdf_extractor.py',
        'data_processor.py',
        'excel_exporter.py',
        'requirements.txt'
    ]
    
    import os
    todos_presentes = True
    
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            print(f"[OK] {arquivo}")
        else:
            print(f"[X] {arquivo} (NAO ENCONTRADO)")
            todos_presentes = False
    
    print("-" * 60)
    
    return todos_presentes

def main():
    """Função principal."""
    resultado_geral = True
    
    # Verificar Python
    if not verificar_python():
        resultado_geral = False
    
    # Verificar dependências
    deps_ok, opcionais_ok = verificar_dependencias()
    if not deps_ok:
        resultado_geral = False
        print()
        print("[!] ATENCAO: Algumas dependencias nao estao instaladas!")
        print("  Execute: pip install -r requirements.txt")
    
    # Verificar arquivos
    arquivos_ok = verificar_arquivos()
    if not arquivos_ok:
        resultado_geral = False
        print()
        print("[!] ATENCAO: Alguns arquivos do programa nao foram encontrados!")
    
    # Resultado final
    print()
    print("=" * 60)
    if resultado_geral:
        print("[OK] TUDO OK! O programa esta pronto para ser executado.")
        print()
        print("Para executar o programa, use:")
        print("  python run.py")
        print("  ou")
        print("  python main.py")
    else:
        print("[X] ERROS ENCONTRADOS!")
        print()
        print("Corrija os erros acima antes de executar o programa.")
        print()
        print("Para instalar as dependencias:")
        print("  pip install -r requirements.txt")
    
    print("=" * 60)
    print()
    
    return resultado_geral

if __name__ == "__main__":
    try:
        sucesso = main()
        sys.exit(0 if sucesso else 1)
    except Exception as e:
        print(f"\n[X] ERRO durante a verificacao: {e}")
        sys.exit(1)

