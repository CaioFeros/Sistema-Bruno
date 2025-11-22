# Hook personalizado para garantir que todas as dependências do openpyxl sejam incluídas
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules, collect_data_files
import os

# Coletar todas as DLLs dinâmicas do openpyxl
binaries = collect_dynamic_libs('openpyxl')

# Coletar todos os submódulos
hiddenimports = collect_submodules('openpyxl')

# Coletar arquivos de dados
datas = collect_data_files('openpyxl')

# Adicionar explicitamente o módulo principal
if 'openpyxl' not in hiddenimports:
    hiddenimports.append('openpyxl')

# IMPORTANTE: Garantir que o próprio pacote openpyxl seja incluído
# Adicionar o diretório completo do openpyxl aos dados
try:
    import openpyxl
    openpyxl_path = os.path.dirname(openpyxl.__file__)
    # Adicionar o diretório completo do openpyxl
    # O PyInstaller precisa do diretório pai para incluir o pacote completo
    openpyxl_parent = os.path.dirname(openpyxl_path)
    datas.append((openpyxl_path, 'openpyxl'))
    print(f"hook-openpyxl: Adicionando diretório completo: {openpyxl_path} -> openpyxl")
    print(f"hook-openpyxl: Diretório pai: {openpyxl_parent}")
except Exception as e:
    print(f"AVISO hook-openpyxl: Erro ao coletar diretório: {e}")
    import traceback
    traceback.print_exc()

# Adicionar submódulos importantes
hiddenimports += [
    'openpyxl.cell',
    'openpyxl.cell._writer',
    'openpyxl.cell.text',
    'openpyxl.chart',
    'openpyxl.chart._chart',
    'openpyxl.chart.area_chart',
    'openpyxl.chart.bar_chart',
    'openpyxl.chart.bubble_chart',
    'openpyxl.chart.line_chart',
    'openpyxl.chart.pie_chart',
    'openpyxl.chart.radar_chart',
    'openpyxl.chart.scatter_chart',
    'openpyxl.chart.surface_chart',
    'openpyxl.compat',
    'openpyxl.compat.abc',
    'openpyxl.compat.product',
    'openpyxl.compat.singleton',
    'openpyxl.descriptors',
    'openpyxl.descriptors.base',
    'openpyxl.descriptors.excel',
    'openpyxl.descriptors.slots',
    'openpyxl.drawing',
    'openpyxl.drawing.colors',
    'openpyxl.drawing.fill',
    'openpyxl.drawing.geometry',
    'openpyxl.drawing.image',
    'openpyxl.drawing.line',
    'openpyxl.drawing.spreadsheet_drawing',
    'openpyxl.formula',
    'openpyxl.formula.translate',
    'openpyxl.packaging',
    'openpyxl.packaging.interface',
    'openpyxl.packaging.manifest',
    'openpyxl.packaging.relationship',
    'openpyxl.packaging.workbook',
    'openpyxl.reader',
    'openpyxl.reader.excel',
    'openpyxl.styles',
    'openpyxl.styles.alignment',
    'openpyxl.styles.borders',
    'openpyxl.styles.colors',
    'openpyxl.styles.fills',
    'openpyxl.styles.fonts',
    'openpyxl.styles.numbers',
    'openpyxl.styles.protection',
    'openpyxl.styles.proxy',
    'openpyxl.styles.table',
    'openpyxl.utils',
    'openpyxl.utils.dataframe',
    'openpyxl.utils.datetime',
    'openpyxl.utils.exceptions',
    'openpyxl.utils.formulas',
    'openpyxl.utils.inference',
    'openpyxl.utils.units',
    'openpyxl.workbook',
    'openpyxl.workbook.child',
    'openpyxl.workbook.defined_name',
    'openpyxl.workbook.external_link',
    'openpyxl.workbook.external_reference',
    'openpyxl.workbook.function_group',
    'openpyxl.workbook.properties',
    'openpyxl.workbook.protection',
    'openpyxl.workbook.smart_tags',
    'openpyxl.workbook.views',
    'openpyxl.workbook.web',
    'openpyxl.worksheet',
    'openpyxl.worksheet._reader',
    'openpyxl.worksheet._writer',
    'openpyxl.worksheet.cell_range',
    'openpyxl.worksheet.cell_watch',
    'openpyxl.worksheet.controls',
    'openpyxl.worksheet.custom',
    'openpyxl.worksheet.datavalidation',
    'openpyxl.worksheet.dimensions',
    'openpyxl.worksheet.errors',
    'openpyxl.worksheet.filters',
    'openpyxl.worksheet.formula',
    'openpyxl.worksheet.header_footer',
    'openpyxl.worksheet.hyperlink',
    'openpyxl.worksheet.page',
    'openpyxl.worksheet.pagebreak',
    'openpyxl.worksheet.picture',
    'openpyxl.worksheet.print_settings',
    'openpyxl.worksheet.protection',
    'openpyxl.worksheet.related',
    'openpyxl.worksheet.scenario',
    'openpyxl.worksheet.smart_tag',
    'openpyxl.worksheet.table',
    'openpyxl.worksheet.views',
    'openpyxl.writer',
    'openpyxl.writer.excel',
    'openpyxl.xml',
    'openpyxl.xml.constants',
    'openpyxl.xml.functions',
]

print(f"hook-openpyxl: Coletando {len(binaries)} binarios, {len(hiddenimports)} imports, {len(datas)} arquivos de dados")

