# Marketing Automation Agents

Sistema de automação para agência de marketing digital usando Claude Code e MCPs.

**Meta 2026:** $500k/mês | 80% margem | 6 clientes high-ticket

---

## Estrutura do Projeto

```
Marketing Automation Agents/
│
├── 📁 _templates/              ← COPIE PARA CRIAR NOVO
│   ├── client-template/        → Novo cliente
│   └── agent-template/         → Novo agente
│
├── 📁 agents/                  ← AGENTES DE IA
│   ├── data-pulse/             → Análise de dados (/dados)
│   ├── ad-launcher/            → Gestão de anúncios (/ads)
│   ├── copy-forge/             → Criação de copies (/copy)
│   └── command-center/         → Orquestrador (/status)
│
├── 📁 mcps/                    ← INTEGRACÕES (APIs)
│   ├── meta-ads/               → Facebook/Instagram Ads
│   ├── gohighlevel/            → CRM GoHighLevel
│   └── zapier/                 → Automações Zapier
│
├── 📁 clients/                 ← CLIENTES
│   └── brez-scales/            → Projeto piloto
│
├── 📁 docs/                    ← DOCUMENTAÇÃO
│   ├── board/                  → Análises estratégicas
│   ├── guides/                 → Guias de setup
│   └── strategy/               → Prompt semente
│
└── 📁 config/                  ← CONFIGURAÇÃO
    └── claude-desktop.json     → Config do Claude Code
```

---

## Quick Start

### Criar Novo Cliente
```bash
cp -r _templates/client-template clients/nome-cliente
# Edite clients/nome-cliente/config.yaml
```

### Criar Novo Agente
```bash
cp -r _templates/agent-template agents/nome-agente
# Edite o system-prompt.md
```

### Configurar Claude Code
```bash
# Copie config/claude-desktop.json para:
# ~/.claude/claude_desktop_config.json
# Preencha as credenciais
```

---

## Agentes Disponíveis

| Agente | Comando | Função | Status |
|--------|---------|--------|--------|
| **Data Pulse** | `/dados` | Análise de métricas | 🟢 Pronto |
| **Ad Launcher** | `/ads` | Criar/gerenciar campanhas | 🟢 Pronto |
| **Copy Forge** | `/copy` | Gerar variações de copy | 🟡 Template |
| **Command Center** | `/status` | Orquestrar agentes | 🟢 Pronto |

---

## MCPs (Integrações)

| MCP | Plataforma | Status |
|-----|------------|--------|
| `meta-ads` | Facebook/Instagram Ads | 🟢 Pronto |
| `gohighlevel` | GoHighLevel CRM | 🟢 Pronto |
| `zapier` | Zapier Automations | 🟢 Pronto |

---

## Clientes

| Cliente | Status | Stack |
|---------|--------|-------|
| **Brez Scales** | 🟢 Piloto | Meta, Google, GHL, Zapier, Whop |

---

## Documentação

| Doc | Descrição |
|-----|-----------|
| [Setup Guide](docs/guides/SETUP_GUIDE.md) | Como configurar tudo |
| [Token Meta](docs/guides/GUIA_TOKEN_META_ADS.md) | Criar token Meta Ads |
| [Prompt Semente](docs/strategy/PROMPT_SEMENTE.md) | Base estratégica |
| [Board Docs](docs/board/) | Análises do board |

---

## Próximos Passos

- [ ] Gerar token Meta Ads (Brez Scales)
- [ ] Testar MCP meta-ads
- [ ] Definir métricas do funil
- [ ] Criar planilha de tracking
- [ ] Primeiro Daily Pulse

---

**Contato:** Rodrigo (CMO) | Pierre (CEO)

**Criado:** 2026-01-02
