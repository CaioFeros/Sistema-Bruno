#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de inicialização do Sistema de Extração de Recibos PDF.
Verifica dependências antes de iniciar o programa.
"""

import sys
import os

# CORREÇÃO CRÍTICA: Configurar paths ANTES de qualquer importação quando for executável
# Quando não usa --onefile, o PyInstaller coloca dependências em _internal
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
    internal_path = os.path.join(base_path, '_internal')
    
    # Adicionar _internal ao path PRIMEIRO (antes de qualquer importação)
    if os.path.exists(internal_path):
        if internal_path not in sys.path:
            sys.path.insert(0, internal_path)
    
    # Adicionar também o diretório base (onde está o executável)
    if base_path not in sys.path:
        sys.path.insert(0, base_path)
    
    # Adicionar subpastas importantes do numpy/pandas se existirem
    for subfolder in ['numpy', 'pandas', 'pandas.libs', 'numpy.libs', 'numpy.core', 'pandas._libs']:
        subfolder_path = os.path.join(internal_path, subfolder) if os.path.exists(internal_path) else os.path.join(base_path, subfolder)
        if os.path.exists(subfolder_path) and subfolder_path not in sys.path:
            sys.path.insert(0, subfolder_path)

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
        base_path = os.path.dirname(sys.executable)
        
        # Quando não é --onefile, as dependências ficam em _internal
        # Adicionar _internal ao sys.path ANTES de qualquer importação
        internal_path = os.path.join(base_path, '_internal')
        if os.path.exists(internal_path):
            # Adicionar no início do path para ter prioridade
            sys.path.insert(0, internal_path)
            # Também adicionar subpastas importantes
            for subfolder in ['numpy', 'pandas', 'pdfplumber', 'openpyxl', 'pandas.libs', 'numpy.libs', 'pdfminer', 'PIL']:
                subfolder_path = os.path.join(internal_path, subfolder)
                if os.path.exists(subfolder_path):
                    sys.path.insert(0, subfolder_path)
        
        os.chdir(base_path)
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
            # Debug: mostrar sys.path para diagnóstico
            print("sys.path configurado:")
            for i, path in enumerate(sys.path[:5]):
                print(f"  [{i}] {path}")
            if len(sys.path) > 5:
                print(f"  ... e mais {len(sys.path) - 5} caminhos")
            print()
            
            # Verificar se pdfplumber está acessível
            import importlib.util
            pdfplumber_found = False
            for path in sys.path:
                pdfplumber_path = os.path.join(path, 'pdfplumber')
                if os.path.exists(pdfplumber_path) or os.path.exists(pdfplumber_path + '.py'):
                    print(f"pdfplumber encontrado em: {path}")
                    pdfplumber_found = True
                    break
            if not pdfplumber_found:
                print("AVISO: pdfplumber nao encontrado em nenhum caminho do sys.path")
            print()
            print("Testando importações críticas...")
            try:
                import numpy
                print("  [OK] numpy")
            except ImportError as e:
                print(f"  [ERRO] numpy: {e}")
                import tkinter.messagebox as msgbox
                msgbox.showerror("Erro de Dependência", 
                    f"Erro ao carregar numpy:\n\n{str(e)}\n\n"
                    "O executável pode estar corrompido ou incompleto.\n"
                    "Por favor, gere um novo executável usando instaler.bat")
                sys.exit(1)
            
            try:
                import pandas as pd
                print("  [OK] pandas")
                # Testar funcionalidade básica do pandas
                df = pd.DataFrame({'test': [1, 2, 3]})
                print("  [OK] pandas funcional")
            except ImportError as e:
                print(f"  [ERRO] pandas: {e}")
                import tkinter.messagebox as msgbox
                msgbox.showerror("Erro de Dependência", 
                    f"Erro ao carregar pandas:\n\n{str(e)}\n\n"
                    "O executável pode estar corrompido ou incompleto.\n"
                    "Por favor, gere um novo executável usando instaler.bat")
                sys.exit(1)
            except Exception as e:
                print(f"  [ERRO] pandas funcionalidade: {e}")
                import tkinter.messagebox as msgbox
                msgbox.showerror("Erro de Dependência", 
                    f"Erro ao usar pandas:\n\n{str(e)}\n\n"
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

