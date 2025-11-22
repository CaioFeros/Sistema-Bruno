# Guia Completo de Instalação

Este guia irá ajudá-lo a instalar e executar o Sistema de Extração de Recibos PDF em qualquer computador.

## 📋 Pré-requisitos

Antes de começar, você precisa ter instalado:

1. **Python 3.8 ou superior**
   - Verificar versão: `python --version` ou `python3 --version`
   - [Download Python](https://www.python.org/downloads/)

2. **Git** (para clonar o repositório)
   - [Download Git](https://git-scm.com/downloads)

## 🚀 Instalação Passo a Passo

### Windows

1. **Instalar Python:**
   - Baixe o instalador em: https://www.python.org/downloads/
   - **IMPORTANTE:** Durante a instalação, marque "Add Python to PATH"
   - Conclua a instalação

2. **Abrir Prompt de Comando ou PowerShell:**
   - Pressione `Win + R`
   - Digite `cmd` ou `powershell` e pressione Enter

3. **Clonar o repositório:**
```bash
git clone https://github.com/CaioFeros/Sistema-Bruno.git
cd Sistema-Bruno
```

4. **Instalar dependências:**
```bash
python -m pip install -r requirements.txt
```

5. **Executar o programa:**
   - Opção 1: Clique duas vezes em `executar.bat`
   - Opção 2: Execute `python run.py` no terminal
   - Opção 3: Execute `python main.py` no terminal

### Linux (Ubuntu/Debian)

1. **Instalar Python e ferramentas:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk git
```

2. **Clonar o repositório:**
```bash
git clone https://github.com/CaioFeros/Sistema-Bruno.git
cd Sistema-Bruno
```

3. **Instalar dependências:**
```bash
pip3 install -r requirements.txt
```

4. **Executar o programa:**
```bash
python3 run.py
```

### macOS

1. **Instalar Python (se necessário):**
   - Python geralmente já vem instalado no macOS
   - Ou instale via Homebrew: `brew install python3`

2. **Clonar o repositório:**
```bash
git clone https://github.com/CaioFeros/Sistema-Bruno.git
cd Sistema-Bruno
```

3. **Instalar dependências:**
```bash
pip3 install -r requirements.txt
```

4. **Executar o programa:**
```bash
python3 run.py
```

## 🔧 Verificação da Instalação

Execute estes comandos para verificar se tudo está instalado:

```bash
# Verificar versão do Python
python --version  # ou python3 --version

# Verificar se as dependências estão instaladas
pip list | grep pdfplumber
pip list | grep pandas
pip list | grep openpyxl
```

## ❌ Solução de Problemas

### Erro: "python não é reconhecido como comando"

**Windows:**
- Python não foi adicionado ao PATH durante a instalação
- Reinstale o Python marcando "Add Python to PATH"
- Ou adicione manualmente o Python ao PATH do sistema

### Erro: "tkinter não encontrado"

**Windows:**
- O tkinter geralmente já vem com Python
- Se não tiver, reinstale o Python e marque a opção "tcl/tk"

**Linux:**
```bash
sudo apt-get install python3-tk
```

**macOS:**
- Geralmente já vem instalado
- Se não tiver, instale via Homebrew: `brew install python-tk`

### Erro: "ModuleNotFoundError: No module named 'pdfplumber'"

Instale as dependências novamente:
```bash
pip install -r requirements.txt
```

Ou instale individualmente:
```bash
pip install pdfplumber pandas openpyxl
```

### Erro ao instalar tkinterdnd2

Este pacote é **opcional**. O programa funciona sem ele, apenas sem a funcionalidade de arrastar e soltar arquivos.

Se quiser instalar no Windows:
```bash
pip install tkinterdnd2
```

## ✅ Teste Rápido

Após a instalação, teste se está tudo funcionando:

1. Execute o programa: `python run.py` ou `python main.py`
2. A interface gráfica deve abrir
3. Se a janela abrir, está tudo funcionando! 🎉

## 📦 Instalação em Ambiente Virtual (Recomendado)

Para evitar conflitos com outros projetos Python, é recomendado usar um ambiente virtual:

### Windows:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

### Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 run.py
```

## 🆘 Precisa de Ajuda?

Se encontrar problemas, verifique:
1. A versão do Python (deve ser 3.8+)
2. Se todas as dependências foram instaladas (`pip list`)
3. Se o tkinter está disponível (`python -m tkinter` - deve abrir uma janela de teste)

## 📝 Notas Importantes

- O programa **não precisa** de acesso à internet para funcionar
- Todos os arquivos necessários estão no repositório
- Não há configurações ou arquivos externos necessários
- O programa funciona **offline** após a instalação

