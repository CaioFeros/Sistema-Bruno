# Hook personalizado para garantir que todas as dependências do pdfplumber sejam incluídas
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules, collect_data_files, collect_all

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

# Coletar dependências do pdfplumber (pdfminer, etc)
try:
    pdfminer_binaries, pdfminer_hidden, pdfminer_datas = collect_all('pdfminer.six')
    binaries += pdfminer_binaries
    hiddenimports += pdfminer_hidden
    datas += pdfminer_datas
except:
    pass

print(f"hook-pdfplumber: Coletando {len(binaries)} binarios, {len(hiddenimports)} imports, {len(datas)} arquivos de dados")

