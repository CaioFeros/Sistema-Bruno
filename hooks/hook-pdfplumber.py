# Hook personalizado para garantir que todas as dependências do pdfplumber sejam incluídas
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

# Usar collect_all que coleta TUDO do pdfplumber (módulos, dados, binários)
binaries, hiddenimports, datas = collect_all('pdfplumber')

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

# Coletar também dependências do pdfplumber
try:
    pdfminer_binaries, pdfminer_hidden, pdfminer_datas = collect_all('pdfminer.six')
    binaries += pdfminer_binaries
    hiddenimports += pdfminer_hidden
    datas += pdfminer_datas
except:
    pass

print(f"hook-pdfplumber: Coletando {len(binaries)} binarios, {len(hiddenimports)} imports, {len(datas)} arquivos de dados")
