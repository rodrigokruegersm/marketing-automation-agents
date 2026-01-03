# Adlytics - Intelligence for Scale

Sistema de automacao de marketing digital com agentes de IA.

**Meta 2026:** $500k/mes | 80% margem | 6 clientes high-ticket

---

## Estrutura do Projeto

```
Adlytics/
├── dashboard/              # DASHBOARD PRINCIPAL (Streamlit)
│   ├── app.py              # Aplicacao principal
│   └── components/         # Componentes UI
│
├── core/                   # NUCLEO DO SISTEMA
│   ├── adapters/           # Integracoes com APIs
│   │   ├── meta_ads.py     # Meta Ads API
│   │   ├── hyros.py        # Hyros Attribution
│   │   ├── leonardo.py     # Leonardo.ai Image API
│   │   └── checkout/       # Plataformas de checkout
│   │       ├── whop.py
│   │       ├── clickfunnels.py
│   │       ├── hotmart.py
│   │       ├── kiwify.py
│   │       └── stripe.py
│   ├── campaign_parser.py  # Parser de campanhas {TAG}
│   ├── client_registry.py  # Registro de clientes
│   ├── funnel_registry.py  # Registro de funis
│   └── product_registry.py # Registro de produtos
│
├── agents/                 # AGENTES DE IA
│   ├── command-center/     # Orquestrador principal
│   ├── data-pulse/         # Analise de dados
│   ├── ad-launcher/        # Gestao de anuncios
│   ├── copy_forge/         # Geracao de copies
│   ├── creative_lab/       # Criacao de criativos
│   ├── design_agent/       # Geracao de imagens (Leonardo.ai)
│   ├── audience_builder/   # Construcao de publicos
│   └── performance_optimizer/  # Otimizacao de performance
│
├── clients/                # CLIENTES
│   └── brez-scales/        # Projeto piloto
│       ├── config.yaml
│       ├── products/       # Produtos do cliente
│       ├── funnels/        # Funis configurados
│       └── reports/        # Relatorios gerados
│
├── brand/                  # IDENTIDADE VISUAL
│   └── BRAND_GUIDELINES.md # Cores, fontes, logo
│
├── docs/                   # DOCUMENTACAO
│   ├── architecture/       # Arquitetura do sistema
│   ├── guides/             # Guias de setup
│   └── session-history/    # Historico de sessoes
│
├── mcps/                   # INTEGRACOES MCP
│   ├── meta-ads/
│   ├── google-sheets/
│   ├── gohighlevel/
│   └── zapier/
│
└── config/                 # CONFIGURACAO
    └── claude-desktop.json
```

---

## Dashboard

O dashboard Adlytics oferece:
- Metricas em tempo real (ROAS, CPP, Revenue)
- Analise por funil com tags {FUNNEL}
- Integracao com Whop, ClickFunnels, Hyros
- Sugestoes de IA para otimizacao
- Controle de campanhas Meta Ads

### Executar Dashboard

```bash
cd dashboard
streamlit run app.py
```

**URL Local:** http://localhost:8501

---

## Integracoes Suportadas

| Plataforma | Tipo | Status |
|------------|------|--------|
| **Meta Ads** | Anuncios | Ativo |
| **Leonardo.ai** | Geracao de Imagens | Ativo |
| **Hyros** | Atribuicao | Ativo |
| **Whop** | Checkout | Ativo |
| **ClickFunnels** | Checkout | Ativo |
| **Hotmart** | Checkout | Pronto |
| **Kiwify** | Checkout | Pronto |
| **Stripe** | Checkout | Pronto |

---

## Agentes de IA

| Agente | Funcao | Status |
|--------|--------|--------|
| **Command Center** | Orquestracao | Ativo |
| **Data Pulse** | Analise de dados | Ativo |
| **Ad Launcher** | Gestao de anuncios | Ativo |
| **Copy Forge** | Geracao de copies | Ativo |
| **Design Agent** | Imagens com Leonardo.ai | Ativo |
| **Creative Lab** | Criativos | Em dev |
| **Audience Builder** | Publicos | Em dev |
| **Performance Optimizer** | Otimizacao | Em dev |

---

## Configuracao

### Variaveis de Ambiente (.env)

```env
# Meta Ads
META_ACCESS_TOKEN=seu_token
META_AD_ACCOUNT_ID=act_xxxxx

# AI Image Generation (Leonardo.ai)
LEONARDO_API_KEY=sua_chave

# Checkout
WHOP_API_KEY=sua_chave
CLICKFUNNELS_API_KEY=sua_chave

# Atribuicao
HYROS_API_KEY=sua_chave
```

### Streamlit Secrets

Para deploy no Streamlit Cloud, configure os secrets em:
`.streamlit/secrets.toml`

---

## Marca Adlytics

- **Nome:** Adlytics (Ad + Analytics)
- **Tagline:** Intelligence for Scale
- **Cores:** Ocean Blue (#0066FF), Deep Navy (#0A1628)
- **Fonte:** Inter

Ver detalhes em [brand/BRAND_GUIDELINES.md](brand/BRAND_GUIDELINES.md)

---

## Resultados (Brez Scales)

| KPI | Valor | Status |
|-----|-------|--------|
| ROAS | 2.50x | GOOD |
| Revenue | $9,095 | - |
| Spend | $3,644 | - |
| Profit | $5,451 | GOOD |

---

**Criado:** 2026-01-02 | **Atualizado:** 2026-01-03
