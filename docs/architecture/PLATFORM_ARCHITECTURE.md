# Marketing Command Center - Platform Architecture

## Visao Geral

Sistema de automacao de marketing multi-cliente, multi-funil, preparado para escala com multiplos agentes de IA.

---

## Estrutura de Nomenclatura de Campanhas

### Convencao Obrigatoria

Todas as campanhas devem seguir o padrao:

```
{FUNIL} - {TIPO} - {DESCRICAO}
```

**Exemplos:**
- `{VSL_CHALLENGE} - COLD - Broad Interest`
- `{VSL_CHALLENGE} - RET - Viewers 50%`
- `{WEBINAR_LIVE} - COLD - Lookalike 1%`
- `{HIGH_TICKET} - COLD - Custom Audience`

### Tags Reconhecidas

| Tag | Tipo de Funil | Metricas Chave |
|-----|---------------|----------------|
| `{VSL_CHALLENGE}` | VSL + Desafio Pago | ROAS, CPP, Close Rate |
| `{WEBINAR_LIVE}` | Webinar ao Vivo | CPL, Show Rate, Close Rate |
| `{WEBINAR_EVERGREEN}` | Webinar Gravado | CPL, Watch Rate, Close Rate |
| `{HIGH_TICKET}` | Venda Direta High Ticket | ROAS, CAC, LTV |
| `{LOW_TICKET}` | Venda Direta Low Ticket | ROAS, AOV, Frequency |
| `{LEAD_GEN}` | Geracao de Leads | CPL, Lead Quality Score |
| `{ECOMMERCE}` | E-commerce | ROAS, AOV, Cart Abandon Rate |
| `{APP_INSTALL}` | Instalacao de App | CPI, Retention D7, LTV |

---

## Arquitetura de Dados

```
┌─────────────────────────────────────────────────────────────────┐
│                        PLATFORM CORE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Client     │  │   Funnel     │  │   Campaign   │          │
│  │   Registry   │──│   Registry   │──│   Parser     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                │                  │                    │
│         └────────────────┼──────────────────┘                   │
│                          ▼                                       │
│               ┌──────────────────────┐                          │
│               │   Data Aggregator    │                          │
│               │   (by client/funnel) │                          │
│               └──────────────────────┘                          │
│                          │                                       │
└──────────────────────────┼──────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
  │   Meta Ads  │  │  Google Ads │  │    Hyros    │
  │   Adapter   │  │   Adapter   │  │   Adapter   │
  └─────────────┘  └─────────────┘  └─────────────┘
```

---

## Estrutura de Pastas (Refatorada)

```
Marketing Automation Agents/
│
├── core/                           ← NOVO: Nucleo da plataforma
│   ├── __init__.py
│   ├── client_registry.py          → Registro de clientes
│   ├── funnel_registry.py          → Registro de funis
│   ├── campaign_parser.py          → Parser de nomenclatura {TAG}
│   ├── data_aggregator.py          → Agregacao por cliente/funil
│   └── config.py                   → Configuracoes globais
│
├── adapters/                       ← NOVO: Conectores de plataforma
│   ├── __init__.py
│   ├── base_adapter.py             → Interface base
│   ├── meta_ads_adapter.py         → Meta Ads API
│   ├── google_ads_adapter.py       → Google Ads API
│   └── hyros_adapter.py            → Hyros API
│
├── agents/                          ← Agentes de IA (existente)
│   ├── command-center/
│   ├── data-pulse/
│   ├── ad-launcher/
│   ├── copy-forge/
│   └── [futuros agentes]/
│
├── clients/                         ← Dados por cliente
│   ├── _registry.yaml               → NOVO: Indice de clientes
│   ├── brez-scales/
│   │   ├── config.yaml
│   │   ├── funnels/                 → NOVO: Configs por funil
│   │   │   ├── vsl_challenge.yaml
│   │   │   └── high_ticket.yaml
│   │   ├── dashboards/
│   │   ├── data/
│   │   └── reports/
│   └── [outros clientes]/
│
├── dashboard/                       ← NOVO: Dashboard unificado
│   ├── app.py                       → Streamlit multi-cliente
│   ├── components/
│   │   ├── navigation.py            → Navegacao fluida
│   │   ├── client_selector.py       → Seletor de cliente
│   │   ├── funnel_filter.py         → Filtro de funil
│   │   └── campaign_table.py        → Tabela de campanhas
│   ├── pages/
│   │   ├── overview.py              → Visao geral
│   │   ├── campaigns.py             → Gestao de campanhas
│   │   ├── funnels.py               → Analise por funil
│   │   ├── ai_suggestions.py        → Sugestoes IA
│   │   └── agents.py                → Central de agentes
│   └── requirements.txt
│
└── docs/
    └── architecture/
        └── PLATFORM_ARCHITECTURE.md  → Este documento
```

---

## Modelo de Dados

### Client

```python
@dataclass
class Client:
    id: str                    # CLI_001
    name: str                  # "Brez Scales"
    slug: str                  # "brez-scales"
    status: str                # active, paused, churned
    meta_account_id: str       # act_1202800550735727
    meta_access_token: str     # Token do cliente
    google_account_id: str     # (opcional)
    hyros_api_key: str         # (opcional)
    funnels: List[Funnel]
    created_at: datetime
```

### Funnel

```python
@dataclass
class Funnel:
    id: str                    # FUN_001
    name: str                  # "VSL Challenge"
    tag: str                   # "VSL_CHALLENGE"
    type: FunnelType           # vsl, webinar, high_ticket, etc
    client_id: str
    thresholds: Dict           # KPIs especificos do funil
    campaigns: List[Campaign]
```

### Campaign (Parseada)

```python
@dataclass
class ParsedCampaign:
    id: str                    # ID do Meta
    name: str                  # Nome completo
    funnel_tag: str            # Tag extraida {TAG}
    campaign_type: str         # COLD, RET, etc
    description: str           # Resto do nome
    status: str
    metrics: Dict
```

---

## Fluxo de Navegacao

```
┌─────────────────────────────────────────────────────────────┐
│                    HEADER - Quick Switcher                   │
├─────────────────────────────────────────────────────────────┤
│  [Cliente: Brez Scales ▼]  [Funil: VSL Challenge ▼]  [7d ▼] │
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
   ┌───────────┐       ┌───────────┐       ┌───────────┐
   │  Overview │       │  Funnels  │       │  Agents   │
   │  (KPIs)   │       │  (Drill)  │       │  (IA)     │
   └───────────┘       └───────────┘       └───────────┘
         │                    │                    │
         ▼                    ▼                    ▼
   ┌───────────┐       ┌───────────┐       ┌───────────┐
   │ Campaigns │       │  Ad Sets  │       │  Actions  │
   │ (Control) │       │  (Perf)   │       │  (Exec)   │
   └───────────┘       └───────────┘       └───────────┘
```

---

## Integracao Hyros

### Endpoints Necessarios

```
GET /api/v1/accounts/{account_id}/campaigns
GET /api/v1/accounts/{account_id}/metrics
GET /api/v1/accounts/{account_id}/funnels
POST /api/v1/webhooks/subscribe
```

### Dados Consumidos

- Performance de campanhas em tempo real
- Atribuicao de conversoes
- Analise de cohort
- Predicao de LTV

---

## Agentes de IA

| Agente | Funcao | Status | Arquivo |
|--------|--------|--------|---------|
| `data-pulse` | Analise de dados | Ativo | - |
| `ad-launcher` | Gestao de campanhas | Ativo | - |
| `CopyForge` | Geracao de copies/headlines | Implementado | `agents/copy_forge/` |
| `CreativeLab` | Conceitos criativos | Implementado | `agents/creative_lab/` |
| `AudienceBuilder` | Construcao de publicos | Implementado | `agents/audience_builder/` |
| `PerformanceOptimizer` | Otimizacao de performance | Implementado | `agents/performance_optimizer/` |
| `report-generator` | Geracao de reports | Planejado | - |
| `client-manager` | Gestao de clientes | Planejado | - |

### Uso dos Agentes

```python
from agents import CopyForgeAgent, PerformanceOptimizerAgent

# Gerar headlines
copy_agent = CopyForgeAgent()
headlines = copy_agent.generate_headlines(
    product="Curso de Marketing Digital",
    audience="Empreendedores 25-45",
    count=5
)

# Analisar performance
optimizer = PerformanceOptimizerAgent()
result = optimizer.run({
    'action': 'analyze',
    'campaigns': campaigns_data,
    'thresholds': {'roas_min': 2.0}
})
```

---

## Proximos Passos

1. [x] Documentar arquitetura
2. [x] Criar modulo `core/`
   - `client_registry.py` - Registro multi-cliente
   - `funnel_registry.py` - Tipos e thresholds de funil
   - `campaign_parser.py` - Parser de tags `{FUNNEL}`
   - `data_aggregator.py` - Agregacao por cliente/funil
3. [x] Implementar `campaign_parser.py`
   - Regex para extracao de `{TAG}` de nomes
   - Deteccao de tipo de campanha (COLD, RET, etc)
   - Agrupamento por funil
4. [x] Criar dashboard unificado
   - `dashboard/app.py` - Dashboard multi-cliente
   - Componentes reutilizaveis em `dashboard/components/`
   - Navegacao fluida entre clientes/funis
5. [x] Criar adapters de plataforma
   - `core/adapters/meta_ads.py` - Meta Ads API
   - `core/adapters/hyros.py` - Hyros API (preparado)
6. [x] Criar estrutura de agentes IA
   - `agents/base.py` - Classe base para agentes
   - `agents/copy_forge/` - Geracao de copies
   - `agents/creative_lab/` - Conceitos criativos
   - `agents/audience_builder/` - Construcao de publicos
   - `agents/performance_optimizer/` - Otimizacao
7. [ ] Migrar Brez Scales para nova estrutura
8. [ ] Integrar Hyros API (quando disponivel)
9. [ ] Adicionar autenticacao multi-usuario
10. [ ] Implementar sistema de notificacoes
