# Setup - Guia de Configuracao

Este guia explica como configurar o Adlytics do zero.

---

## Pre-requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)
- Conta no Meta Business (para Meta Ads)
- Git (para versionamento)

---

## 1. Instalacao Local

### Clonar o Repositorio

```bash
git clone https://github.com/rodrigokruegersm/marketing-automation-agents.git
cd marketing-automation-agents
```

### Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Configurar Variaveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar com suas credenciais
nano .env  # ou use seu editor preferido
```

### Executar

```bash
streamlit run dashboard/app.py
```

Acesse: http://localhost:8501

---

## 2. Configurando API Keys

### Meta Ads (Obrigatorio)

1. Acesse [developers.facebook.com](https://developers.facebook.com)
2. Crie ou selecione um app
3. Adicione o produto "Marketing API"
4. Gere um Access Token com permissoes:
   - `ads_read`
   - `ads_management`
5. Anote o token e o Ad Account ID (`act_xxxxx`)

### Hyros (Opcional)

1. Acesse seu painel Hyros
2. Va em Settings → API
3. Copie a API Key

### Leonardo.ai (Opcional)

1. Acesse [leonardo.ai](https://leonardo.ai)
2. Va em API Settings
3. Gere uma API Key

### ElevenLabs (Opcional)

1. Acesse [elevenlabs.io](https://elevenlabs.io)
2. Va em Profile Settings
3. Copie a API Key

### HeyGen (Opcional)

1. Acesse [heygen.com](https://heygen.com)
2. Va em API Settings
3. Gere uma API Key

---

## 3. Arquivo .env

Seu arquivo `.env` deve conter:

```bash
# Autenticacao do Dashboard
DASHBOARD_PASSWORD=sua_senha_segura

# Meta Ads (Obrigatorio)
META_ACCESS_TOKEN=EAARxxx...
META_AD_ACCOUNT_ID=act_1234567890

# Hyros
HYROS_API_KEY=API_xxx...

# Whop
WHOP_API_KEY=apik_xxx...

# Leonardo.ai
LEONARDO_API_KEY=xxx...

# ElevenLabs
ELEVENLABS_API_KEY=xxx...

# HeyGen
HEYGEN_API_KEY=xxx...
```

---

## 4. Deploy no Streamlit Cloud

### Passo 1: Preparar Repositorio

Certifique-se de que seu repositorio esta no GitHub e que
os arquivos `.env` e secrets NAO estao commitados.

### Passo 2: Acessar Streamlit Cloud

1. Va para [share.streamlit.io](https://share.streamlit.io)
2. Faca login com GitHub

### Passo 3: Criar App

1. Clique "New app"
2. Selecione o repositorio
3. Branch: `main`
4. Main file path: `dashboard/app.py`

### Passo 4: Configurar Secrets

1. Clique em "Advanced settings"
2. Na secao "Secrets", adicione:

```toml
DASHBOARD_PASSWORD = "sua_senha"
META_ACCESS_TOKEN = "EAARxxx..."
META_AD_ACCOUNT_ID = "act_xxxxx"
WHOP_API_KEY = "apik_xxx"
HYROS_API_KEY = "API_xxx"
```

### Passo 5: Deploy

Clique "Deploy!" e aguarde alguns minutos.

---

## 5. Solucao de Problemas

### Erro: "ModuleNotFoundError"

```bash
pip install -r requirements.txt
```

### Erro: "API Token Invalid"

- Verifique se o token nao expirou (tokens de teste expiram em 60 dias)
- Gere um novo token em developers.facebook.com

### Erro: "No campaigns found"

- Verifique o Ad Account ID (deve comecar com `act_`)
- Verifique se a conta tem campanhas ativas

### Erro de Autenticacao no Dashboard

- Verifique se DASHBOARD_PASSWORD esta configurado
- Tente limpar cookies do navegador

---

## 6. Atualizando

### Atualizar Codigo

```bash
git pull origin main
```

### Atualizar Dependencias

```bash
pip install -r requirements.txt --upgrade
```

### Limpar Cache do Streamlit

No dashboard, clique no botao "Atualizar" ou:

```bash
streamlit cache clear
```

---

## 7. Checklist de Configuracao

- [ ] Python 3.10+ instalado
- [ ] Dependencias instaladas
- [ ] Meta Access Token configurado
- [ ] Ad Account ID configurado
- [ ] Dashboard funcionando localmente
- [ ] Deploy no Streamlit Cloud (opcional)

---

**Duvidas?** Consulte a documentacao em [ARCHITECTURE.md](ARCHITECTURE.md)
