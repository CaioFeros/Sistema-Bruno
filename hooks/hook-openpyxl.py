# Hook personalizado para garantir que todas as dependências do openpyxl sejam incluídas
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

# Coletar arquivos de dados do openpyxl (muito importante!)
datas = collect_data_files('openpyxl')

# Coletar submódulos
hiddenimports = collect_submodules('openpyxl')

# Coletar binários
binaries = collect_dynamic_libs('openpyxl')

# Garantir que o módulo principal está incluído
if 'openpyxl' not in hiddenimports:
    hiddenimports.append('openpyxl')

print(f"hook-openpyxl: Coletando {len(binaries)} binarios, {len(hiddenimports)} imports, {len(datas)} arquivos de dados")
