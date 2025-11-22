#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar se todas as dependências estão na pasta _internal do executável.
Execute este script após criar o executável com instaler.bat.
"""

import os
import sys

def verificar_dependencias():
    """Verifica se todas as dependências estão presentes na pasta _internal."""
    
    print("=" * 60)
    print("VERIFICACAO DE DEPENDENCIAS DO EXECUTAVEL")
    print("=" * 60)
    print()
    
    # Caminho da pasta _internal
    base_path = os.path.join("dist", "setup", "_internal")
    
    if not os.path.exists(base_path):
        print(f"[ERRO] Pasta _internal nao encontrada em: {base_path}")
        print("Execute instaler.bat primeiro para criar o executavel.")
        return False
    
    print(f"Verificando dependencias em: {base_path}")
    print()
    
    # Dependências obrigatórias
    dependencias_obrigatorias = {
        'numpy': 'NumPy (processamento numérico)',
        'pandas': 'Pandas (manipulação de dados)',
        'pdfplumber': 'PDFPlumber (extração de PDF)',
        'openpyxl': 'OpenPyXL (exportação Excel)',
    }
    
    # Dependências opcionais
    dependencias_opcionais = {
        'tkinterdnd2': 'TkinterDnD2 (drag and drop)',
        'pytz': 'Pytz (fusos horários)',
        'dateutil': 'DateUtil (datas)',
    }
    
    todas_ok = True
    
    print("DEPENDENCIAS OBRIGATORIAS:")
    print("-" * 60)
    for dep, desc in dependencias_obrigatorias.items():
        dep_path = os.path.join(base_path, dep)
        if os.path.exists(dep_path):
            # Verificar se tem arquivos Python
            tem_py = False
            for root, dirs, files in os.walk(dep_path):
                if any(f.endswith(('.py', '.pyd', '.so', '.dll')) for f in files):
                    tem_py = True
                    break
            
            if tem_py:
                print(f"  [OK] {dep:15} - {desc}")
            else:
                print(f"  [AVISO] {dep:15} - Pasta existe mas parece vazia")
                todas_ok = False
        else:
            print(f"  [ERRO] {dep:15} - NAO ENCONTRADO!")
            todas_ok = False
    
    print()
    print("DEPENDENCIAS OPCIONAIS:")
    print("-" * 60)
    for dep, desc in dependencias_opcionais.items():
        dep_path = os.path.join(base_path, dep)
        if os.path.exists(dep_path):
            print(f"  [OK] {dep:15} - {desc}")
        else:
            print(f"  [--] {dep:15} - Nao encontrado (opcional)")
    
    print()
    print("VERIFICANDO MODULOS ESPECIFICOS:")
    print("-" * 60)
    
    # Verificar módulos específicos do numpy
    numpy_core = os.path.join(base_path, "numpy", "core")
    if os.path.exists(numpy_core):
        print(f"  [OK] numpy.core encontrado")
        # Verificar multiarray
        multiarray_files = [f for f in os.listdir(numpy_core) if 'multiarray' in f.lower()]
        if multiarray_files:
            print(f"  [OK] numpy.core.multiarray encontrado")
        else:
            print(f"  [ERRO] numpy.core.multiarray NAO encontrado!")
            todas_ok = False
    else:
        print(f"  [ERRO] numpy.core NAO encontrado!")
        todas_ok = False
    
    # Verificar módulos específicos do pandas
    pandas_libs = os.path.join(base_path, "pandas", "_libs")
    if os.path.exists(pandas_libs):
        print(f"  [OK] pandas._libs encontrado")
    else:
        print(f"  [ERRO] pandas._libs NAO encontrado!")
        todas_ok = False
    
    # Verificar módulos específicos do pdfplumber
    pdfplumber_pdf = os.path.join(base_path, "pdfplumber", "pdf.py")
    if os.path.exists(pdfplumber_pdf):
        print(f"  [OK] pdfplumber.pdf encontrado")
    else:
        print(f"  [ERRO] pdfplumber.pdf NAO encontrado!")
        todas_ok = False
    
    print()
    print("=" * 60)
    if todas_ok:
        print("[OK] Todas as dependencias obrigatorias foram encontradas!")
        print("O executavel parece estar completo e pronto para distribuir.")
    else:
        print("[ERRO] Algumas dependencias estao faltando!")
        print("Execute instaler.bat novamente ou verifique os hooks.")
    print("=" * 60)
    print()
    
    return todas_ok

if __name__ == "__main__":
    try:
        sucesso = verificar_dependencias()
        input("Pressione Enter para sair...")
        sys.exit(0 if sucesso else 1)
    except Exception as e:
        print(f"\n[ERRO] Erro durante verificacao: {e}")
        import traceback
        traceback.print_exc()
        input("\nPressione Enter para sair...")
        sys.exit(1)

