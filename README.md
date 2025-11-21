# Sistema de Extração de Dados de Recibos PDF

Sistema desktop em Python para extrair dados de recibos de venda de PDFs e exportar para Excel.

## Funcionalidades

- 🎨 Interface moderna com tema dark mode
- 📄 Upload de PDFs contendo recibos de venda
- 🔍 Extração automática de dados estruturados:
  - Nº do recibo
  - Vendedor
  - Nome/Razão Social do cliente
  - Descrição dos produtos (com limpeza inteligente)
  - Quantidade
  - Valor unitário
- 👁️ Preview dos dados extraídos em tempo real
- 📊 Exportação para Excel formatado com:
  - Aba de Recibos com linhas intercaladas (zebrado)
  - Aba de Estatísticas por Vendedor com blocos separados
  - Formatação profissional
- 📈 Estatísticas agrupadas por vendedor:
  - Quantidade total vendida
  - Valor total vendido
  - Preço médio por MG
  - Preço mínimo por MG
  - Preço máximo por MG
- 🧹 Limpeza inteligente de descrições de produtos
- ✅ Validação e filtragem de dados

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/Sistema-Bruno.git
cd Sistema-Bruno
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

### Executar o sistema:

**Windows:**
- Clique duas vezes em `executar.bat`, ou
- Execute `python run.py` no terminal

**Linux/Mac:**
```bash
python run.py
```

Ou diretamente:
```bash
python main.py
```

### Como usar:

1. Clique em "Selecionar PDF" ou arraste o arquivo PDF para a área de upload
2. Clique em "Processar PDF" para extrair os dados
3. Visualize os dados extraídos no preview
4. Clique em "Exportar para Excel" para salvar os dados formatados
5. Use "Limpar Dados" para processar um novo PDF

## Estrutura do Projeto

- `main.py` - Interface principal tkinter com tema dark mode
- `pdf_extractor.py` - Módulo de extração de dados do PDF
- `data_processor.py` - Processamento, limpeza e estruturação dos dados
- `excel_exporter.py` - Exportação para Excel com formatação profissional
- `executar.bat` - Script de execução para Windows
- `executar.ps1` - Script PowerShell para Windows
- `run.py` - Script Python multiplataforma
- `requirements.txt` - Dependências do projeto

## Requisitos

- Python 3.8+
- tkinter (geralmente incluído no Python)
- pdfplumber
- pandas
- openpyxl
- tkinterdnd2 (opcional, para drag and drop)

## Características Técnicas

- **Tema Dark Mode**: Interface moderna com cores escuras
- **Multithreading**: Processamento em thread separada para não travar a interface
- **Validação de Dados**: Filtragem automática de linhas inválidas
- **Limpeza Inteligente**: Correção automática de descrições de produtos
- **Formatação Profissional**: Excel exportado com estilos e cores

## Contribuição

Sinta-se à vontade para contribuir com melhorias, correções de bugs ou novas funcionalidades!

## Licença

Este projeto é de código aberto.

