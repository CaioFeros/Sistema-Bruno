# Hook personalizado para garantir que todas as DLLs do numpy sejam incluídas
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules, collect_data_files
import os

# Coletar todas as DLLs dinâmicas do numpy
binaries = collect_dynamic_libs('numpy')

# Coletar todos os submódulos
hiddenimports = collect_submodules('numpy')

# Coletar arquivos de dados
datas = collect_data_files('numpy')

# Adicionar explicitamente os módulos core do numpy
hiddenimports += [
    'numpy.core._multiarray_umath',
    'numpy.core.multiarray',
    'numpy.core.umath',
    'numpy.core._dtype_ctypes',
    'numpy.core._internal',
    'numpy.core._struct_ufunc_tests',
    'numpy.core._operand_flag_tests',
    'numpy.core._rational_tests',
    'numpy.core._umath_tests',
]

print(f"hook-numpy: Coletando {len(binaries)} binarios, {len(hiddenimports)} imports, {len(datas)} arquivos de dados")

