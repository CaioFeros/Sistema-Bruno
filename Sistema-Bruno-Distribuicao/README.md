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

### Pré-requisitos

- **Python 3.8 ou superior** (recomendado: Python 3.11+)
- **Git** (para clonar o repositório) - [Download](https://git-scm.com/downloads)

### Passos de Instalação

1. **Clone o repositório:**
```bash
git clone https://github.com/CaioFeros/Sistema-Bruno.git
cd Sistema-Bruno
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

Se estiver usando Python 3, pode ser necessário usar `pip3`:
```bash
pip3 install -r requirements.txt
```

**Nota para Windows:** Se encontrar problemas, tente:
```bash
python -m pip install -r requirements.txt
```

### Verificação da Instalação

Para verificar se tudo está instalado corretamente:
```bash
python --version  # Deve mostrar Python 3.8 ou superior
pip list  # Deve mostrar pdfplumber, pandas, openpyxl na lista
```

### Problemas Comuns

**tkinter não encontrado:**
- **Windows:** Geralmente já vem instalado com Python
- **Linux (Ubuntu/Debian):** `sudo apt-get install python3-tk`
- **Mac:** Geralmente já vem instalado com Python

**tkinterdnd2 não instala:**
- Este pacote é opcional (drag and drop)
- O programa funciona sem ele, apenas sem a funcionalidade de arrastar arquivos
- Em Windows, pode precisar: `pip install tkinterdnd2`

## 🚀 Uso Rápido

### Opção 1: Executável (Recomendado para Usuários)

1. Baixe o ZIP do repositório ou da [página de Releases](https://github.com/CaioFeros/Sistema-Bruno/releases)
2. Extraia o ZIP em uma pasta
3. Clique duas vezes em `Sistema-Bruno.exe`
4. O sistema verificará e instalará dependências automaticamente
5. Aguarde a instalação (primeira vez apenas)

📖 **Guia completo do executável**: Veja `README_EXECUTAVEL.md`

### Opção 2: Código Fonte (Para Desenvolvedores)

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

### Sistemas Operacionais Suportados
- ✅ Windows 10/11
- ✅ Linux (Ubuntu, Debian, etc.)
- ✅ macOS

### Dependências Python
- **Python 3.8 ou superior** (recomendado: 3.11+)
- **pdfplumber** (>=0.10.0) - Extração de texto de PDFs
- **pandas** (>=2.0.0) - Manipulação de dados
- **openpyxl** (>=3.1.0) - Exportação para Excel
- **tkinter** - Interface gráfica (geralmente incluído no Python)
- **tkinterdnd2** (>=0.3.0) - Drag and drop (opcional)

### Instalação Rápida de Todas as Dependências
```bash
pip install pdfplumber pandas openpyxl tkinterdnd2
```

Ou usando o arquivo requirements.txt:
```bash
pip install -r requirements.txt
```

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

