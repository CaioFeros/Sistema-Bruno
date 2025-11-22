# Como Publicar o Executável no GitHub Release

Este guia explica como publicar o executável criado como Release no GitHub para que usuários possam baixar facilmente.

## 📋 Pré-requisitos

1. ✅ Executável criado (`dist\Sistema-Bruno.exe`)
2. ✅ ZIP de distribuição criado (`Sistema-Bruno-Distribuicao.zip`)
3. ✅ Conta do GitHub logada

## 🚀 Passo a Passo

### Passo 1: Criar o Executável (se ainda não tiver)

```bash
build_executavel.bat
```

Aguarde a conclusão. O executável será criado em `dist\Sistema-Bruno.exe`.

### Passo 2: Preparar o ZIP de Distribuição

```bash
distribuir.bat
```

Isso criará o arquivo `Sistema-Bruno-Distribuicao.zip` pronto para distribuir.

### Passo 3: Acessar a Página de Releases

1. Acesse: https://github.com/CaioFeros/Sistema-Bruno/releases/new
2. Ou vá em: https://github.com/CaioFeros/Sistema-Bruno → "Releases" → "Create a new release"

### Passo 4: Preencher Informações da Release

**Tag version:**
- Use formato semântico: `v1.0.0`, `v1.0.1`, etc.
- Exemplo: `v1.0.0`
- ⚠️ Se for a primeira release, crie uma nova tag ou use `v1.0.0`

**Release title:**
- Título descritivo
- Exemplo: `Sistema Bruno v1.0.0 - Executável Standalone`

**Description:**
```
## 🚀 Sistema de Extração de Recibos PDF v1.0.0

### 📦 Download

Baixe o arquivo `Sistema-Bruno-Distribuicao.zip` abaixo e extraia em uma pasta.

### 🎯 Como Usar

1. Extraia o arquivo ZIP em uma pasta
2. Clique duas vezes em `Sistema-Bruno.exe`
3. O sistema verificará e instalará dependências automaticamente
4. Aguarde a instalação (primeira vez apenas)
5. O sistema abrirá automaticamente

### ✅ Requisitos

- Windows 10 ou superior
- Python 3.8 ou superior instalado
  - Download: https://www.python.org/downloads/

### 📝 Funcionalidades

- Interface moderna com tema dark mode
- Extração automática de dados de PDFs
- Exportação para Excel formatado
- Estatísticas por vendedor
- Limpeza inteligente de descrições

### 📖 Documentação

Consulte os arquivos incluídos no ZIP:
- `LER_PRIMEIRO.txt` - Guia rápido
- `README_EXECUTAVEL.md` - Guia completo do executável
- `README.md` - Documentação completa
```

### Passo 5: Anexar o Arquivo ZIP

1. Na seção "Attach binaries", clique em "Choose your files"
2. Selecione o arquivo: `Sistema-Bruno-Distribuicao.zip`
3. Aguarde o upload completar

**⚠️ IMPORTANTE:** 
- Não anexe arquivos muito grandes (>100MB pode falhar)
- Se o arquivo for muito grande, considere usar Git LFS ou criar uma versão que requer Python instalado

### Passo 6: Publicar a Release

1. Clique em **"Publish release"**
2. Pronto! A release está publicada

## 📥 Como Usuários Baixarão

Os usuários poderão:

1. Acessar: https://github.com/CaioFeros/Sistema-Bruno/releases
2. Ver a lista de releases
3. Baixar o arquivo `Sistema-Bruno-Distribuicao.zip` da release mais recente
4. Extrair e executar `Sistema-Bruno.exe`

## 🔄 Atualizar uma Release Existente

Se quiser atualizar uma release existente:

1. Acesse: https://github.com/CaioFeros/Sistema-Bruno/releases
2. Clique na release que deseja atualizar
3. Clique em "Edit release"
4. Anexe o novo arquivo ZIP
5. Atualize a descrição se necessário
6. Clique em "Update release"

## 📝 Boas Práticas

### Tags Semânticas

Use versões semânticas:
- `v1.0.0` - Primeira versão estável
- `v1.0.1` - Correção de bugs
- `v1.1.0` - Novas funcionalidades
- `v2.0.0` - Mudanças maiores

### Descrição da Release

Sempre inclua:
- ✅ Número da versão
- ✅ Lista de mudanças principais
- ✅ Instruções de uso
- ✅ Requisitos do sistema
- ✅ Links para documentação

### Nome do Arquivo ZIP

Use nomes descritivos:
- `Sistema-Bruno-v1.0.0-Windows.zip`
- `Sistema-Bruno-v1.0.0-Standalone.zip`

## ⚠️ Avisos Importantes

### Tamanho do Arquivo

- **ZIP de distribuição**: ~60MB (normal para executáveis Python)
- **GitHub suporta**: até 100MB sem Git LFS
- **Se maior que 100MB**: Use Git LFS ou divida em partes

### Executável no Repositório

- ✅ **Código fonte**: no repositório principal
- ✅ **Executável**: apenas nas Releases (não no repositório)
- ✅ **ZIP de distribuição**: apenas nas Releases

Isso mantém o repositório leve e o executável acessível nas Releases.

## ✅ Checklist

Antes de publicar, verifique:

- [ ] Executável foi testado e funciona
- [ ] ZIP contém todos os arquivos necessários
- [ ] Documentação está incluída no ZIP
- [ ] Tag da versão está correta
- [ ] Descrição da release está completa
- [ ] Arquivo ZIP está pronto para upload

## 🎉 Pronto!

Após publicar a release, os usuários poderão baixar e usar o sistema diretamente do GitHub!

