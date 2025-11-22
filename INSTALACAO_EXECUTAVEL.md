# Como Criar o Executável (.exe) do Sistema

Este guia explica como criar um arquivo executável que pode ser distribuído e executado sem precisar instalar Python ou dependências.

## 📋 Pré-requisitos

Para criar o executável, você precisa:

1. **Python instalado** na máquina de desenvolvimento
2. **PyInstaller** - Será instalado automaticamente pelo script

## 🚀 Criando o Executável

### Windows

1. Abra o Prompt de Comando ou PowerShell na pasta do projeto

2. Execute o script de build:
```bash
build_executavel.bat
```

3. O executável será criado em: `dist\Sistema-Bruno.exe`

### Linux/macOS

1. Dê permissão de execução:
```bash
chmod +x build_executavel.sh
```

2. Execute o script:
```bash
./build_executavel.sh
```

3. O executável será criado em: `dist/Sistema-Bruno`

## 📦 O que o Executável Faz

O executável criado (`Sistema-Bruno.exe` ou `Sistema-Bruno`) irá:

1. ✅ Verificar se o Python está instalado no computador de destino
2. ✅ Verificar se todas as dependências estão instaladas
3. ✅ Se tudo estiver OK, iniciar o sistema automaticamente
4. ✅ Se faltar algo, mostrar mensagens claras de como instalar

## 📝 Distribuindo o Executável

### Opção 1: Arquivo Único (Recomendado)

O script cria um executável único (`--onefile`) que contém tudo:

- **Vantagem**: Um único arquivo para distribuir
- **Desvantagem**: Mais lento ao iniciar (poucos segundos)

### Opção 2: Pasta Completa

Se preferir, pode remover a opção `--onefile` no script para criar uma pasta com todos os arquivos:

- **Vantagem**: Inicia mais rápido
- **Desvantagem**: Precisa distribuir toda a pasta

## ⚠️ Importante

O executável **AINDA PRECISA** de Python instalado no computador de destino!

Se quiser criar um executável que **NÃO** precisa de Python, você precisará usar ferramentas mais avançadas ou criar um instalador.

### Alternativa: Executável Standalone

Para criar um executável que não precisa de Python instalado, você pode usar:

- **Nuitka** - Compilador Python para executáveis standalone
- **cx_Freeze** - Alternativa ao PyInstaller
- **PyInstaller com opções especiais** - Incluir Python embutido

## 🔧 Troubleshooting

### Erro: "PyInstaller não encontrado"

Instale manualmente:
```bash
pip install pyinstaller
```

### Executável muito grande

Isso é normal! O PyInstaller inclui Python e todas as dependências.

### Erro ao executar o .exe

1. Verifique se o Python está instalado
2. Execute o verificador: `python verificar_instalacao.py`
3. Verifique os logs de erro

## 📤 Adicionando ao GitHub Release

Depois de criar o executável, você pode:

1. Ir em: https://github.com/CaioFeros/Sistema-Bruno/releases/new
2. Criar uma nova release
3. Anexar o arquivo `dist/Sistema-Bruno.exe` ou criar um ZIP
4. Usuários podem baixar e executar diretamente!

