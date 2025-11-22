#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para verificar problemas com numpy/pandas em executáveis.
Execute este script na máquina que está com problema para gerar um relatório.
"""

import sys
import os

print("=" * 60)
print("DIAGNOSTICO DO SISTEMA")
print("=" * 60)
print()

print("Python:")
print(f"  Versao: {sys.version}")
print(f"  Executavel: {sys.executable}")
print(f"  Frozen: {getattr(sys, 'frozen', False)}")
print()

if getattr(sys, 'frozen', False):
    print("Modo Executavel:")
    print(f"  Executavel: {sys.executable}")
    print(f"  Diretorio do executavel: {os.path.dirname(sys.executable)}")
    print()
    
    base_path = os.path.dirname(sys.executable)
    internal_path = os.path.join(base_path, '_internal')
    print(f"  Pasta _internal existe: {os.path.exists(internal_path)}")
    if os.path.exists(internal_path):
        print(f"  Caminho _internal: {internal_path}")
        print(f"  Conteudo _internal:")
        try:
            items = os.listdir(internal_path)
            for item in sorted(items)[:20]:  # Primeiros 20 itens
                item_path = os.path.join(internal_path, item)
                item_type = "DIR" if os.path.isdir(item_path) else "FILE"
                print(f"    [{item_type}] {item}")
            if len(items) > 20:
                print(f"    ... e mais {len(items) - 20} itens")
        except Exception as e:
            print(f"    ERRO ao listar: {e}")
    print()
    
    print("sys.path:")
    for i, path in enumerate(sys.path[:10]):
        print(f"  [{i}] {path}")
    if len(sys.path) > 10:
        print(f"  ... e mais {len(sys.path) - 10} caminhos")
    print()

print("Testando importacoes:")
print("-" * 60)

try:
    import numpy
    print(f"  [OK] numpy - versao: {numpy.__version__}")
    print(f"       caminho: {numpy.__file__}")
    try:
        import numpy.core.multiarray
        print(f"  [OK] numpy.core.multiarray")
    except Exception as e:
        print(f"  [ERRO] numpy.core.multiarray: {e}")
except ImportError as e:
    print(f"  [ERRO] numpy: {e}")
    print(f"         Detalhes: {type(e).__name__}")

print()

try:
    import pandas
    print(f"  [OK] pandas - versao: {pandas.__version__}")
    print(f"       caminho: {pandas.__file__}")
except ImportError as e:
    print(f"  [ERRO] pandas: {e}")
    print(f"         Detalhes: {type(e).__name__}")

print()
print("=" * 60)
input("Pressione Enter para sair...")

