#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de inicialização do Sistema de Extração de Recibos PDF.
Verifica dependências antes de iniciar o programa.
"""

import sys
import os

def verificar_python():
    """Verifica se a versão do Python é compatível."""
    versao = sys.version_info
    if versao.major < 3 or (versao.major == 3 and versao.minor < 8):
        print("ERRO: Python 3.8 ou superior e necessario!")
        print(f"Versao atual: {versao.major}.{versao.minor}.{versao.micro}")
        print("\nBaixe Python em: https://www.python.org/downloads/")
        input("\nPressione Enter para sair...")
        return False
    return True

def instalar_dependencia(modulo):
    """Tenta instalar uma dependência automaticamente."""
    import subprocess
    try:
        print(f"Instalando {modulo}...")
        resultado = subprocess.run(
            [sys.executable, "-m", "pip", "install", modulo],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos timeout
        )
        if resultado.returncode == 0:
            print(f"[OK] {modulo} instalado com sucesso!")
            return True
        else:
            print(f"[ERRO] Falha ao instalar {modulo}")
            print(resultado.stderr)
            return False
    except Exception as e:
        print(f"[ERRO] Erro ao instalar {modulo}: {e}")
        return False

def verificar_e_instalar_dependencias():
    """Verifica e instala dependências automaticamente se necessário."""
    dependencias_obrigatorias = ['pdfplumber', 'pandas', 'openpyxl']
    dependencias_faltando = []
    
    # Verificar quais dependências faltam
    for modulo in dependencias_obrigatorias:
        try:
            __import__(modulo)
        except ImportError:
            dependencias_faltando.append(modulo)
    
    # Se todas estão instaladas, retornar True
    if not dependencias_faltando:
        return True
    
    # Tentar instalar automaticamente
    print("=" * 60)
    print("INSTALANDO DEPENDENCIAS AUTOMATICAMENTE")
    print("=" * 60)
    print()
    
    todas_instaladas = True
    for dep in dependencias_faltando:
        if not instalar_dependencia(dep):
            todas_instaladas = False
    
    print()
    
    if todas_instaladas:
        # Verificar novamente se foram instaladas corretamente
        for modulo in dependencias_faltando:
            try:
                __import__(modulo)
            except ImportError:
                todas_instaladas = False
                break
        
        if todas_instaladas:
            print("[OK] Todas as dependencias foram instaladas!")
            print()
            return True
    
    # Se não conseguiu instalar automaticamente, mostrar instruções
    print("=" * 60)
    print("FALHA NA INSTALACAO AUTOMATICA")
    print("=" * 60)
    print("\nAs seguintes dependencias precisam ser instaladas manualmente:")
    for dep in dependencias_faltando:
        print(f"  - {dep}")
    
    print("\nPara instalar manualmente, abra o Prompt de Comando e execute:")
    print("  pip install -r requirements.txt")
    print("\nOu instale individualmente:")
    for dep in dependencias_faltando:
        print(f"  pip install {dep}")
    
    input("\nPressione Enter para sair...")
    return False

def verificar_arquivos():
    """Verifica se todos os arquivos necessários estão presentes."""
    arquivos_necessarios = [
        'main.py',
        'pdf_extractor.py',
        'data_processor.py',
        'excel_exporter.py'
    ]
    
    arquivos_faltando = []
    for arquivo in arquivos_necessarios:
        if not os.path.exists(arquivo):
            arquivos_faltando.append(arquivo)
    
    if arquivos_faltando:
        print("ERRO: Arquivos do programa nao encontrados:")
        for arquivo in arquivos_faltando:
            print(f"  - {arquivo}")
        print("\nCertifique-se de que todos os arquivos estao na mesma pasta.")
        input("\nPressione Enter para sair...")
        return False
    
    return True

def main():
    """Função principal de inicialização."""
    # Mudar para o diretório do script
    is_standalone = getattr(sys, 'frozen', False)
    
    if is_standalone:
        # Se estiver rodando como executável standalone
        os.chdir(os.path.dirname(sys.executable))
        # Standalone já tem tudo embutido, pular verificações
        print("Iniciando sistema...")
        print()
    else:
        # Se estiver rodando como script Python
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        print("=" * 60)
        print("Sistema de Extracao de Recibos PDF")
        print("Verificando dependencias...")
        print("=" * 60)
        print()
        
        # Verificar Python apenas se não for standalone
        if not verificar_python():
            sys.exit(1)
        
        # Verificar arquivos apenas se não for standalone
        if not verificar_arquivos():
            sys.exit(1)
        
        # Verificar e instalar dependências automaticamente apenas se não for standalone
        if not verificar_e_instalar_dependencias():
            sys.exit(1)
        
        print("Tudo OK! Iniciando o sistema...")
        print()
    
    # Importar e executar o programa principal
    try:
        # Testar importações críticas primeiro
        if is_standalone:
            try:
                import pandas as pd
            except ImportError as e:
                import tkinter.messagebox as msgbox
                msgbox.showerror("Erro de Dependência", 
                    f"Erro ao carregar pandas:\n\n{str(e)}\n\n"
                    "O executável pode estar corrompido ou incompleto.\n"
                    "Por favor, gere um novo executável usando instaler.bat")
                sys.exit(1)
        
        from main import main as main_app
        main_app()
    except ImportError as e:
        if is_standalone:
            # Em standalone, mostrar erro mais amigável
            import tkinter.messagebox as msgbox
            try:
                error_msg = str(e)
                if 'pandas' in error_msg.lower():
                    msgbox.showerror("Erro de Dependência", 
                        f"Erro ao carregar pandas:\n\n{error_msg}\n\n"
                        "O executável pode estar incompleto.\n"
                        "Por favor, gere um novo executável usando instaler.bat")
                else:
                    msgbox.showerror("Erro ao Iniciar", 
                        f"Ocorreu um erro ao iniciar o sistema:\n\n{error_msg}\n\n"
                        "Por favor, entre em contato com o suporte.")
            except:
                # Se tkinter não funcionar, usar print
                print(f"\nERRO ao iniciar o sistema: {e}")
                input("\nPressione Enter para sair...")
        else:
            print(f"\nERRO ao iniciar o sistema: {e}")
            print("\nDetalhes tecnicos:")
            import traceback
            traceback.print_exc()
            input("\nPressione Enter para sair...")
        sys.exit(1)
    except Exception as e:
        if is_standalone:
            # Em standalone, mostrar erro mais amigável
            import tkinter.messagebox as msgbox
            try:
                msgbox.showerror("Erro ao Iniciar", 
                    f"Ocorreu um erro ao iniciar o sistema:\n\n{str(e)}\n\n"
                    "Por favor, entre em contato com o suporte.")
            except:
                # Se tkinter não funcionar, usar print
                print(f"\nERRO ao iniciar o sistema: {e}")
                input("\nPressione Enter para sair...")
        else:
            print(f"\nERRO ao iniciar o sistema: {e}")
            print("\nDetalhes tecnicos:")
            import traceback
            traceback.print_exc()
            input("\nPressione Enter para sair...")
        sys.exit(1)

if __name__ == "__main__":
    main()

