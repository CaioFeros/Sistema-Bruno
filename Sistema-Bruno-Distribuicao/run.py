#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de execução do Sistema de Extração de Recibos PDF
Execute este arquivo para iniciar o sistema.
"""

import sys
import os

# Adicionar o diretório atual ao path (caso necessário)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        from main import main
        print("=" * 50)
        print("Sistema de Extração de Recibos PDF")
        print("=" * 50)
        print("\nIniciando o sistema...\n")
        main()
    except ImportError as e:
        print(f"\nERRO: Não foi possível importar os módulos necessários.")
        print(f"Detalhes: {e}\n")
        print("Verifique se todas as dependências estão instaladas:")
        print("  pip install -r requirements.txt\n")
        sys.exit(1)
    except Exception as e:
        print(f"\nERRO: Ocorreu um erro ao executar o sistema.")
        print(f"Detalhes: {e}\n")
        sys.exit(1)

