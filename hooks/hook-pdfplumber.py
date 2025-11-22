# Hook personalizado para garantir que todas as dependências do pdfplumber sejam incluídas
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules, collect_data_files

# Coletar todas as DLLs dinâmicas do pdfplumber
binaries = collect_dynamic_libs('pdfplumber')

# Coletar todos os submódulos
hiddenimports = collect_submodules('pdfplumber')

# Coletar arquivos de dados
datas = collect_data_files('pdfplumber')

# Adicionar explicitamente o módulo principal
if 'pdfplumber' not in hiddenimports:
    hiddenimports.append('pdfplumber')

# Adicionar submódulos explícitos
hiddenimports += [
    'pdfplumber.cli',
    'pdfplumber.ctm',
    'pdfplumber.display',
    'pdfplumber.layout',
    'pdfplumber.page',
    'pdfplumber.pdf',
    'pdfplumber.table',
    'pdfplumber.utils',
]

# Coletar dependências do pdfplumber (pdfminer)
try:
    from PyInstaller.utils.hooks import collect_all
    pdfminer_result = collect_all('pdfminer.six')
    if isinstance(pdfminer_result, tuple) and len(pdfminer_result) == 3:
        pdfminer_binaries, pdfminer_hidden, pdfminer_datas = pdfminer_result
        binaries.extend(pdfminer_binaries)
        hiddenimports.extend(pdfminer_hidden)
        datas.extend(pdfminer_datas)
except Exception as e:
    # Se falhar, continuar sem pdfminer.six (pode não ser necessário)
    pass

print(f"hook-pdfplumber: Coletando {len(binaries)} binarios, {len(hiddenimports)} imports, {len(datas)} arquivos de dados")
