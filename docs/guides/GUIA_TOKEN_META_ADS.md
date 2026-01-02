# GUIA: Criar Token de Acesso Meta Ads

## Tempo estimado: 10-15 minutos

---

## PASSO 1: Acessar Meta for Developers

1. Acesse: **https://developers.facebook.com**
2. Faça login com a conta que tem acesso ao Business Manager do Brez
3. Clique em **"My Apps"** no canto superior direito

---

## PASSO 2: Criar um App (se não existir)

1. Clique em **"Create App"**
2. Selecione **"Other"** como caso de uso
3. Selecione **"Business"** como tipo de app
4. Preencha:
   - **App Name:** `Brez Automation`
   - **App Contact Email:** seu email
   - **Business Account:** Selecione o Business Manager do Brez
5. Clique em **"Create App"**

---

## PASSO 3: Adicionar Marketing API

1. No dashboard do app, encontre **"Add Products"**
2. Procure por **"Marketing API"**
3. Clique em **"Set Up"**

---

## PASSO 4: Gerar Access Token

### Opção A: Token de Teste (Expira em 1h - para testar)

1. Vá para **Tools > Graph API Explorer**
2. No dropdown "Meta App", selecione `Brez Automation`
3. Clique em **"Generate Access Token"**
4. Selecione as permissões:
   - `ads_read`
   - `ads_management`
   - `business_management`
   - `read_insights`
5. Clique em **"Generate"**
6. Copie o token gerado

### Opção B: Token de Longa Duração (Recomendado - 60 dias)

1. Vá para **Settings > Basic** no seu app
2. Copie o **App ID** e **App Secret**
3. Vá para **Tools > Access Token Tool**
4. Encontre seu app e clique em **"Debug"** no User Token
5. Clique em **"Extend Access Token"**
6. Copie o token estendido (válido por 60 dias)

### Opção C: System User Token (Permanente - Melhor opção)

1. Acesse **Business Manager > Business Settings**
2. Vá para **Users > System Users**
3. Clique em **"Add"**
4. Crie um System User:
   - **Name:** `Brez Automation Bot`
   - **Role:** Admin
5. Clique no System User criado
6. Clique em **"Add Assets"**
7. Adicione a Ad Account `1202800550735727` com permissão **"Manage campaigns"**
8. Clique em **"Generate New Token"**
9. Selecione o App `Brez Automation`
10. Selecione as permissões:
    - `ads_read`
    - `ads_management`
    - `read_insights`
11. Clique em **"Generate Token"**
12. **COPIE E SALVE** - este token não expira mas só aparece uma vez!

---

## PASSO 5: Testar o Token

Abra o terminal e execute:

```bash
curl -G \
  "https://graph.facebook.com/v18.0/act_1202800550735727" \
  -d "fields=name,account_status,currency" \
  -d "access_token=SEU_TOKEN_AQUI"
```

Resposta esperada:
```json
{
  "name": "Ads Manager - Brez",
  "account_status": 1,
  "currency": "USD",
  "id": "act_1202800550735727"
}
```

---

## PASSO 6: Configurar no Projeto

Após obter o token, adicione ao arquivo `.env`:

```bash
META_ACCESS_TOKEN=seu_token_aqui
META_AD_ACCOUNT_ID=act_1202800550735727
```

---

## Permissões Necessárias (Resumo)

| Permissão | Para quê |
|-----------|----------|
| `ads_read` | Ler campanhas, métricas, insights |
| `ads_management` | Criar/editar campanhas, pausar ads |
| `read_insights` | Acessar relatórios detalhados |
| `business_management` | Acessar Business Manager |

---

## Troubleshooting

### "Invalid OAuth access token"
- Token expirou ou está incorreto
- Solução: Gerar novo token

### "User does not have permission"
- O System User não tem acesso à Ad Account
- Solução: Adicionar asset no Business Settings

### "(#100) You must be an admin of the ad account"
- Permissão insuficiente
- Solução: Dar permissão "Manage campaigns" ao System User

---

## Checklist Final

- [ ] App criado no Meta for Developers
- [ ] Marketing API adicionada ao app
- [ ] System User criado no Business Manager
- [ ] Ad Account `1202800550735727` adicionada ao System User
- [ ] Token gerado com permissões corretas
- [ ] Token testado via curl
- [ ] Token salvo no arquivo `.env`

---

**Próximo passo após ter o token:** Me envie o token (ou confirme que está configurado) para testarmos a conexão com o MCP.
