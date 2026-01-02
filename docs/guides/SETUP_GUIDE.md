# GUIA DE SETUP - Marketing Automation Agents

## Pré-requisitos

- Node.js 18+ instalado
- Claude Code CLI instalado
- Acesso às APIs necessárias (Meta, Google, etc.)

---

## PASSO 1: Configurar Variáveis de Ambiente

Copie o arquivo de exemplo e preencha suas credenciais:

```bash
cp .env.example .env
```

### Credenciais Necessárias para o Piloto (Brez Scales):

#### Meta Ads
```bash
# Como obter:
# 1. Acesse https://developers.facebook.com
# 2. Crie um app ou use existente
# 3. Adicione o produto "Marketing API"
# 4. Gere um token de acesso com permissões:
#    - ads_read
#    - ads_management
#    - business_management

META_ACCESS_TOKEN=seu_token_aqui
META_AD_ACCOUNT_ID=act_XXXXXXXXX  # Encontre em Business Manager > Ad Accounts
```

#### Google Sheets (para relatórios)
```bash
# Como obter:
# 1. Acesse https://console.cloud.google.com
# 2. Crie um projeto ou use existente
# 3. Ative a Google Sheets API
# 4. Crie credenciais OAuth2 ou Service Account

GOOGLE_CREDENTIALS_PATH=./credentials/google-credentials.json
```

---

## PASSO 2: Instalar MCPs Oficiais no Claude Code

Abra as configurações do Claude Code e adicione os MCPs:

**Via CLI:**
```bash
claude mcp add filesystem
claude mcp add fetch
```

**Via arquivo de configuração** (recomendado):

Edite `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/rodrigokrueger/Documents/Dev Projects/Active/Marketing Automation Agents"
      ]
    },
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    }
  }
}
```

Reinicie o Claude Code após modificar.

---

## PASSO 3: Instalar MCP Meta Ads (Customizado)

```bash
# Navegue até o diretório do MCP
cd src/mcps/custom/meta-ads

# Instale dependências
npm install

# Teste se funciona
META_ACCESS_TOKEN=seu_token META_AD_ACCOUNT_ID=act_xxx node index.js
```

Adicione ao Claude Code config:

```json
{
  "mcpServers": {
    "meta-ads": {
      "command": "node",
      "args": ["/Users/rodrigokrueger/Documents/Dev Projects/Active/Marketing Automation Agents/src/mcps/custom/meta-ads/index.js"],
      "env": {
        "META_ACCESS_TOKEN": "seu_token_aqui",
        "META_AD_ACCOUNT_ID": "act_XXXXXXXXX"
      }
    }
  }
}
```

---

## PASSO 4: Verificar Instalação

Após reiniciar o Claude Code, teste os comandos:

```
# Testar filesystem
"Liste os arquivos no diretório do projeto"

# Testar fetch
"Faça uma requisição para https://api.ipify.org"

# Testar meta-ads
"Mostre as campanhas ativas da conta Meta Ads"
```

---

## PASSO 5: Configurar Cliente Piloto (Brez Scales)

Edite o arquivo `clients/brez-scales/config.yaml` com as informações reais:

```yaml
stack:
  ads:
    meta:
      enabled: true
      account_id: "act_XXXXXXXXX"  # Seu ID real
      pixel_id: "XXXXXXXXX"
```

---

## Estrutura de Comandos Disponíveis

### Data Pulse (Análise de Dados)
```
/dados brez hoje           → Métricas do dia
/dados brez semana         → Resumo semanal
/dados brez comparar       → Comparativo
/dados brez anomalias      → Alertas
```

### Ad Launcher (Anúncios)
```
/ads brez criar [nome]     → Nova campanha
/ads brez subir [pasta]    → Upload criativos
/ads brez pausar [id]      → Pausar campanha
/ads brez escalar [id] 20  → Aumentar budget 20%
```

---

## Troubleshooting

### MCP não aparece no Claude Code
1. Verifique se o arquivo de config está em `~/.claude/claude_desktop_config.json`
2. Verifique se o JSON está válido (use jsonlint)
3. Reinicie o Claude Code completamente

### Erro de autenticação Meta
1. Verifique se o token não expirou
2. Verifique se o token tem as permissões necessárias
3. Teste o token em: https://developers.facebook.com/tools/debug/accesstoken

### Erro de permissão de arquivos
1. Verifique se os caminhos no filesystem MCP estão corretos
2. Verifique se você tem permissão de leitura nos diretórios

---

## Próximos Passos

1. [ ] Configurar credenciais Meta Ads
2. [ ] Instalar MCPs no Claude Code
3. [ ] Testar comandos básicos
4. [ ] Configurar Brez Scales como piloto
5. [ ] Executar primeiro Daily Pulse

---

**Suporte:** Se tiver problemas, documente o erro e entre em contato.
