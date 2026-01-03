# Adlytics - Intelligence for Scale

Sistema de automacao de marketing digital com agentes de IA.

---

## Deploy Rapido (Streamlit Cloud)

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. **New app** → Repo: `rodrigokruegersm/marketing-automation-agents`
3. **Main file path:** `dashboard/app.py`
4. **Advanced settings** → Cole os secrets:

```toml
DASHBOARD_PASSWORD = "adlytics2026"
META_ACCESS_TOKEN = "seu_token"
META_AD_ACCOUNT_ID = "act_xxxxx"
WHOP_API_KEY = "sua_chave"
HYROS_API_KEY = "sua_chave"
```

5. **Deploy!**

---

## Estrutura

```
Adlytics/
├── dashboard/
│   ├── app.py           # Dashboard principal
│   ├── auth.py          # Autenticacao
│   └── components/      # UI components
│
├── core/
│   ├── adapters/        # APIs (Meta, Hyros, Leonardo, etc)
│   └── *.py             # Parsers e registries
│
├── agents/              # Agentes de IA
│
└── requirements.txt
```

---

## Executar Localmente

```bash
streamlit run dashboard/app.py
```

**URL:** http://localhost:8501

---

## Integracoes

| Plataforma | Status |
|------------|--------|
| Meta Ads | Ativo |
| Leonardo.ai | Ativo |
| ElevenLabs | Ativo |
| HeyGen | Ativo |
| Whop | Ativo |
| Hyros | Ativo |

---

**Atualizado:** 2026-01-03
