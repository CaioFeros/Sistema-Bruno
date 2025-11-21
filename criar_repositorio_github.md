# Como Criar o Repositório no GitHub

## Passo 1: Criar o Repositório no GitHub

1. Acesse: https://github.com/new
2. Configure o repositório:
   - **Repository name**: `Sistema-Bruno`
   - **Description**: `Sistema de Extração de Dados de Recibos PDF com interface dark mode e exportação para Excel`
   - **Visibility**: Escolha Público ou Privado
   - **⚠️ IMPORTANTE**: **NÃO** marque nenhuma opção de inicialização (README, .gitignore, license)
   - O repositório deve estar completamente vazio
3. Clique em **"Create repository"**

## Passo 2: Conectar e Enviar o Código

Após criar o repositório vazio, execute o script abaixo ou use os comandos manuais:

### Opção A: Usar o Script Automático

```bash
conectar_github.bat
```

O script vai pedir a URL do repositório. Cole: `https://github.com/CaioFeros/Sistema-Bruno.git`

### Opção B: Comandos Manuais

```bash
# Adicionar o repositório remoto
git remote add origin https://github.com/CaioFeros/Sistema-Bruno.git

# Renomear branch para main
git branch -M main

# Enviar código para o GitHub
git push -u origin main
```

## Pronto!

Após executar os comandos, seu código estará no GitHub em:
**https://github.com/CaioFeros/Sistema-Bruno**

