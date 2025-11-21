# Comandos para Criar e Publicar o Repositório no GitHub

## 1. Criar o Repositório no GitHub

1. Acesse https://github.com
2. Clique em "+" no canto superior direito
3. Selecione "New repository"
4. Nome do repositório: `Sistema-Bruno` (ou o nome que preferir)
5. Descrição: "Sistema de Extração de Dados de Recibos PDF"
6. Escolha se será público ou privado
7. **NÃO** marque "Initialize this repository with a README" (já temos um)
8. Clique em "Create repository"

## 2. Conectar o Repositório Local ao GitHub

Após criar o repositório no GitHub, você verá uma página com instruções. Use os seguintes comandos:

```bash
# Adicionar o repositório remoto (substitua SEU-USUARIO pelo seu nome de usuário do GitHub)
git remote add origin https://github.com/SEU-USUARIO/Sistema-Bruno.git

# Renomear branch para main (se necessário)
git branch -M main

# Fazer push do código para o GitHub
git push -u origin main
```

## 3. Verificar se tudo está correto

```bash
# Ver os repositórios remotos configurados
git remote -v

# Ver o status do repositório
git status
```

## 4. Próximos Commits (Para Futuras Atualizações)

Quando fizer mudanças no código:

```bash
# Ver as mudanças
git status

# Adicionar os arquivos modificados
git add .

# Fazer commit com uma mensagem descritiva
git commit -m "Descrição das mudanças realizadas"

# Enviar para o GitHub
git push
```

## Autenticação no GitHub

Se for solicitada autenticação, você pode:

1. **Usar Personal Access Token** (recomendado):
   - Vá em Settings > Developer settings > Personal access tokens > Tokens (classic)
   - Gere um novo token com permissão `repo`
   - Use o token como senha quando solicitado

2. **Usar GitHub CLI**:
   ```bash
   gh auth login
   ```

3. **Configurar SSH** (mais seguro):
   - Gere uma chave SSH: `ssh-keygen -t ed25519 -C "seu-email@example.com"`
   - Adicione a chave pública ao GitHub em Settings > SSH and GPG keys
   - Altere a URL do remote para SSH: `git remote set-url origin git@github.com:SEU-USUARIO/Sistema-Bruno.git`

