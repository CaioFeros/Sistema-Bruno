# Sistema de Extração de Dados de Recibos PDF

Sistema desktop em Python para extrair dados de recibos de venda de PDFs e exportar para Excel.

## Funcionalidades

- Upload de PDFs contendo recibos de venda
- Extração automática de dados estruturados:
  - Nº do recibo
  - Vendedor
  - Nome/Razão Social do cliente
  - Descrição dos produtos
  - Quantidade
  - Valor unitário
- Preview dos dados extraídos
- Exportação para Excel formatado

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

Execute o sistema:
```bash
python main.py
```

1. Clique em "Selecionar PDF" ou arraste o arquivo PDF para a área de upload
2. Visualize os dados extraídos no preview
3. Clique em "Exportar para Excel" para salvar os dados

## Estrutura do Projeto

- `main.py` - Interface principal tkinter
- `pdf_extractor.py` - Módulo de extração de dados do PDF
- `data_processor.py` - Processamento e estruturação dos dados
- `excel_exporter.py` - Exportação para Excel

## Requisitos

- Python 3.8+
- tkinter (geralmente incluído no Python)

