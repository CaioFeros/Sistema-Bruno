# Hook personalizado para garantir que todas as dependências do pdfplumber sejam incluídas
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules, collect_data_files
import os

# Coletar todas as DLLs dinâmicas do pdfplumber
binaries = collect_dynamic_libs('pdfplumber')

# Coletar todos os submódulos
hiddenimports = collect_submodules('pdfplumber')

# Coletar arquivos de dados
datas = collect_data_files('pdfplumber')

# Adicionar explicitamente módulos importantes
hiddenimports += [
    'pdfplumber',
    'pdfplumber.cli',
    'pdfplumber.ctm',
    'pdfplumber.display',
    'pdfplumber.layout',
    'pdfplumber.page',
    'pdfplumber.pdf',
    'pdfplumber.table',
    'pdfplumber.utils',
]

# IMPORTANTE: Garantir que o próprio pacote pdfplumber seja incluído
# Isso força o PyInstaller a incluir o diretório completo do pdfplumber
try:
    import pdfplumber
    pdfplumber_path = os.path.dirname(pdfplumber.__file__)
    # Adicionar todos os arquivos do diretório pdfplumber
    for root, dirs, files in os.walk(pdfplumber_path):
        for file in files:
            if file.endswith(('.py', '.pyc', '.pyd')):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, os.path.dirname(pdfplumber_path))
                datas.append((file_path, os.path.join('pdfplumber', os.path.dirname(rel_path))))
except Exception as e:
    print(f"AVISO hook-pdfplumber: Erro ao coletar diretório: {e}")

print(f"hook-pdfplumber: Coletando {len(binaries)} binarios, {len(hiddenimports)} imports, {len(datas)} arquivos de dados")

