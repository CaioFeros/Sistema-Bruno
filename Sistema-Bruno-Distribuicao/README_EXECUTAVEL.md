# Executável do Sistema - Guia Rápido

Este guia explica como usar o executável do Sistema de Extração de Recibos PDF.

## 📦 Como Obter o Executável

### Opção 1: Baixar do GitHub

1. Acesse: https://github.com/CaioFeros/Sistema-Bruno/releases
2. Baixe o arquivo `Sistema-Bruno.zip` ou `Sistema-Bruno.exe`
3. Extraia o ZIP (se necessário) em uma pasta

### Opção 2: Criar Você Mesmo

Siga as instruções em `INSTALACAO_EXECUTAVEL.md`

## 🚀 Como Usar

### Primeira Execução

1. **Clique duas vezes** em `Sistema-Bruno.exe`

2. Na primeira vez, o sistema irá:
   - ✅ Verificar se Python está instalado
   - ✅ Verificar se as dependências estão instaladas
   - ✅ Instalar automaticamente as dependências necessárias

3. Aguarde a instalação (pode levar alguns minutos na primeira vez)

4. O sistema abrirá automaticamente após tudo estar pronto

### Execuções Seguintes

- Simplesmente clique duas vezes em `Sistema-Bruno.exe`
- O sistema abrirá imediatamente (sem verificações se tudo já estiver instalado)

## ⚙️ Requisitos

### Mínimo Necessário

- ✅ **Windows 10** ou superior
- ✅ **Python 3.8** ou superior instalado
  - Download: https://www.python.org/downloads/
  - ⚠️ **IMPORTANTE**: Durante a instalação do Python, marque "Add Python to PATH"

### Dependências

As dependências serão instaladas **automaticamente** na primeira execução:
- pdfplumber
- pandas
- openpyxl
- tkinterdnd2 (opcional)

## 🆘 Problemas Comuns

### "Python não encontrado"

**Solução:**
1. Instale Python: https://www.python.org/downloads/
2. **Durante a instalação**, marque "Add Python to PATH"
3. Reinicie o computador após instalar
4. Execute o `Sistema-Bruno.exe` novamente

### "Falha ao instalar dependências"

**Solução Manual:**
1. Abra o **Prompt de Comando** (Windows + R, digite `cmd`)
2. Execute os comandos:
```bash
pip install pdfplumber pandas openpyxl
```
3. Execute o `Sistema-Bruno.exe` novamente

### "O sistema não abre"

**Verificações:**
1. Verifique se Python está instalado: `python --version`
2. Verifique se as dependências estão instaladas: `pip list`
3. Se necessário, instale manualmente: `pip install -r requirements.txt`

### Antivírus bloqueia o executável

Alguns antivírus podem marcar executáveis Python como suspeitos.

**Solução:**
1. Adicione o arquivo como exceção no antivírus
2. Ou desative temporariamente o antivírus durante a instalação

## 📝 Arquivos Inclusos

Quando você baixar o ZIP, encontrará:

- `Sistema-Bruno.exe` - **Executável principal** (clique aqui para iniciar)
- `requirements.txt` - Lista de dependências (para instalação manual se necessário)
- `README.md` - Documentação completa
- `INSTALACAO.md` - Guia de instalação detalhado
- `LER_PRIMEIRO.txt` - Este guia rápido

## 💡 Dicas

- **Primeira execução pode ser lenta**: O sistema está instalando dependências
- **Mantenha os arquivos juntos**: Não mova apenas o .exe, mantenha todos os arquivos na mesma pasta
- **Recomendado**: Execute como Administrador na primeira vez (clique com botão direito > Executar como administrador)

## ✅ Verificação Rápida

Para verificar se tudo está funcionando:

1. Abra o Prompt de Comando
2. Execute: `python verificar_instalacao.py` (se o arquivo estiver na pasta)
3. Ou execute diretamente o `Sistema-Bruno.exe`

## 📞 Precisa de Ajuda?

Se encontrar problemas:
1. Leia o arquivo `LER_PRIMEIRO.txt`
2. Consulte `INSTALACAO.md` para instruções detalhadas
3. Verifique se Python está instalado corretamente

