# Media Buyer Automation - Documentação Completa

**Versão:** 1.0
**Data:** 2026-01-02
**Cliente Piloto:** Brez Scales

---

## Sumário

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Componentes](#componentes)
4. [Thresholds e Ações](#thresholds-e-ações)
5. [Fluxo de Automação](#fluxo-de-automação)
6. [Configuração](#configuração)
7. [Comandos](#comandos)
8. [Troubleshooting](#troubleshooting)

---

## Visão Geral

O sistema de Media Buyer Automation automatiza:

- **Coleta de dados** do Meta Ads API
- **Avaliação de KPIs** contra thresholds inteligentes
- **Disparo de ações** para agentes especializados
- **Geração de relatórios** diários e semanais
- **Alertas** quando métricas saem do range saudável

### Objetivo de Negócio

- **Meta 2026:** $500k/mês com 80% margem
- **Modelo:** 20% comissão sobre (Revenue - Ad Spend)
- **Projeção Brez Scales:** ~$10,900/mês de comissão

---

## Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                      COMMAND CENTER                              │
│                   (Orquestrador Principal)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│   │   SCHEDULER  │───►│  AUTOMATION  │───►│   AGENTS     │     │
│   │              │    │   ENGINE     │    │              │     │
│   │ • 9 AM Daily │    │              │    │ • Data Pulse │     │
│   │ • Hourly     │    │ • Fetch Data │    │ • Ad Launcher│     │
│   │ • Weekly Mon │    │ • Evaluate   │    │ • Copy Forge │     │
│   └──────────────┘    │ • Execute    │    └──────────────┘     │
│                       │ • Log        │                          │
│                       └──────────────┘                          │
│                              │                                   │
│                              ▼                                   │
│   ┌──────────────────────────────────────────────────────────┐ │
│   │                    DATA STORES                            │ │
│   │  • daily_metrics.csv    • action_log.json                │ │
│   │  • daily_pulse_*.md     • thresholds.yaml                │ │
│   └──────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │   META ADS API   │
                    │   Graph API v18  │
                    └──────────────────┘
```

---

## Componentes

### 1. Automation Engine (`automation_engine.py`)

O coração do sistema. Responsável por:

| Função | Descrição |
|--------|-----------|
| `MetaAdsFetcher` | Conecta à API do Meta e puxa dados |
| `ThresholdEvaluator` | Compara métricas com thresholds |
| `ActionExecutor` | Dispara ações para agentes |
| `DataLogger` | Salva métricas em CSV/JSON |
| `ReportGenerator` | Gera relatórios Markdown |

**Modos de execução:**
```bash
--mode=check    # Verificação única
--mode=daemon   # Monitoramento contínuo
--mode=report   # Gera relatório completo
```

### 2. Thresholds Config (`thresholds.yaml`)

Define regras inteligentes para cada KPI:

```yaml
kpis:
  roas:
    thresholds:
      critical: { value: 1.5, operator: "<", action: "PAUSE_AND_REVIEW" }
      warning:  { value: 1.8, operator: "<", action: "OPTIMIZE_TARGETING" }
      good:     { value: 2.0, operator: ">=", action: "MAINTAIN" }
      excellent:{ value: 2.5, operator: ">=", action: "SCALE_BUDGET" }
```

### 3. Scheduler (`scheduler.py`)

Agenda execuções automáticas:

| Horário | Ação |
|---------|------|
| 09:00 BRT | Daily Report completo |
| A cada hora | Threshold check rápido |
| Segunda 10:00 | Weekly Summary |

### 4. GitHub Actions (`.github/workflows/daily-automation.yml`)

Executa na nuvem mesmo com computador desligado:

- Roda às 9 AM São Paulo (12 PM UTC)
- Checks horários durante horário comercial
- Commits automáticos dos dados
- Notificação Slack em caso de falha

---

## Thresholds e Ações

### ROAS (Return on Ad Spend)

| Level | Condição | Ação | Urgência |
|-------|----------|------|----------|
| 🔴 Critical | < 1.5x | Pausar campanhas, revisar | Imediata |
| 🟡 Warning | < 1.8x | Otimizar targeting | 24h |
| 🟢 Good | ≥ 2.0x | Manter atual | - |
| 🌟 Excellent | ≥ 2.5x | Escalar budget 20% | Oportunidade |

### CPP (Cost Per Purchase)

| Level | Condição | Ação | Urgência |
|-------|----------|------|----------|
| 🔴 Critical | > $30 | Otimização urgente | Imediata |
| 🟡 Warning | > $25 | Revisar criativos | 24h |
| 🟢 Good | ≤ $20 | Manter | - |
| 🌟 Excellent | ≤ $15 | Escalar agressivamente | Oportunidade |

### CTR (Click Through Rate)

| Level | Condição | Ação | Urgência |
|-------|----------|------|----------|
| 🔴 Critical | < 1% | Emergência criativa | Imediata |
| 🟡 Warning | < 1.5% | Testar novos hooks | 24h |
| 🟢 Good | ≥ 2% | Manter | - |
| 🌟 Excellent | ≥ 3% | Expandir audiências | Oportunidade |

### Frequency (Ad Fatigue)

| Level | Condição | Ação | Urgência |
|-------|----------|------|----------|
| 🔴 Critical | > 4 | Rotacionar criativos urgente | Imediata |
| 🟡 Warning | > 3 | Preparar novos criativos | 24h |
| 🟢 Good | ≤ 2.5 | Manter | - |
| 🟢 Healthy | ≤ 2 | Ótimo | - |

### Taxas de Conversão do Funil

| KPI | Critical | Warning | Good | Excellent |
|-----|----------|---------|------|-----------|
| LP View Rate | < 30% | < 40% | ≥ 50% | - |
| Checkout Rate | < 3% | < 5% | ≥ 7% | ≥ 10% |
| Close Rate | < 40% | < 50% | ≥ 60% | ≥ 75% |

---

## Fluxo de Automação

### Exemplo: ROAS cai para 1.7x

```
1. Scheduler dispara check às 10:00
   │
2. Engine puxa dados do Meta
   │ ROAS = 1.7x (abaixo de 1.8)
   │
3. Threshold Evaluator detecta WARNING
   │ Action: OPTIMIZE_TARGETING
   │
4. Action Executor dispara:
   │
   ├──► DATA PULSE: analyze_audiences
   │    - Breakdown por age, gender, placement
   │    - Identifica audiência com pior performance
   │
   └──► AD LAUNCHER: refine_targeting
        - Exclui audiências ruins
        - Aumenta budget nas boas

5. Logger registra ação
   │
6. Report Generator atualiza Daily Pulse
   │ Status: 🟡 WARNING
   │ Alert: "ROAS 1.7x - Optimization in progress"
```

### Exemplo: ROAS sobe para 2.6x

```
1. Scheduler dispara check às 11:00
   │
2. Engine puxa dados do Meta
   │ ROAS = 2.6x (acima de 2.5)
   │
3. Threshold Evaluator detecta EXCELLENT
   │ Action: SCALE_BUDGET
   │
4. Action Executor dispara:
   │
   └──► AD LAUNCHER: scale_budget
        - Aumenta budget em 20%
        - Limite máximo: $500/dia
        - Status: Notifica equipe

5. Logger registra ação
   │
6. Notificação enviada:
   "🌟 Scaling opportunity: ROAS 2.6x - Budget increased 20%"
```

---

## Configuração

### 1. Variáveis de Ambiente

```bash
# .env
META_ACCESS_TOKEN=EAARxSE...
META_AD_ACCOUNT_ID=act_1202800550735727
SLACK_WEBHOOK_URL=https://hooks.slack.com/...  # Opcional
```

### 2. GitHub Secrets (para GitHub Actions)

Vá em **Settings > Secrets and variables > Actions** e adicione:

| Secret | Valor |
|--------|-------|
| `META_ACCESS_TOKEN` | Seu token do Meta |
| `META_AD_ACCOUNT_ID` | `act_1202800550735727` |
| `SLACK_WEBHOOK_URL` | (opcional) URL do webhook |

### 3. Instalar Dependências

```bash
cd agents/command-center
pip install -r requirements.txt
```

---

## Comandos

### Rodar Check Manual
```bash
cd agents/command-center
python3 automation_engine.py --mode=check --period=last_3d
```

### Rodar Relatório Completo
```bash
python3 automation_engine.py --mode=report --period=last_7d
```

### Iniciar Scheduler Local
```bash
python3 scheduler.py
```

### Instalar como Serviço macOS
```bash
cp com.brezscales.automation.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.brezscales.automation.plist
```

### Parar Serviço macOS
```bash
launchctl unload ~/Library/LaunchAgents/com.brezscales.automation.plist
```

### Ver Logs
```bash
tail -f agents/command-center/logs/scheduler.log
```

---

## Troubleshooting

### "Failed to fetch data"
- Verificar se `META_ACCESS_TOKEN` está válido
- Token expira após 60 dias - renovar no Business Manager
- Verificar permissões: `ads_read`, `ads_management`

### "No actions executed"
- Normal quando todos os KPIs estão em "good"
- Sistema só dispara ações quando há warning/critical/excellent

### "GitHub Action failed"
- Verificar se Secrets estão configurados
- Ver logs em Actions > workflow > run details

### Threshold não está disparando
- Verificar operador no `thresholds.yaml` (`<`, `<=`, `>`, `>=`)
- Conferir se o KPI está sendo calculado corretamente

---

## Arquivos do Sistema

```
agents/command-center/
├── automation_engine.py    # Engine principal
├── scheduler.py            # Agendador local
├── thresholds.yaml         # Config de thresholds
├── requirements.txt        # Dependências Python
├── setup.sh               # Script de setup
├── com.brezscales.automation.plist  # Serviço macOS
└── logs/                  # Logs do sistema

clients/brez-scales/
├── data/
│   ├── daily_metrics.csv  # Histórico de métricas
│   └── action_log.json    # Log de ações executadas
├── reports/
│   └── daily_pulse_*.md   # Relatórios diários
└── dashboards/
    ├── streamlit/         # Dashboard interativo
    └── dashboard.html     # Dashboard HTML estático

.github/workflows/
└── daily-automation.yml   # GitHub Actions config
```

---

## Próximos Passos

1. [ ] Configurar Slack notifications
2. [ ] Adicionar Google Ads ao sistema
3. [ ] Criar dashboard de histórico
4. [ ] Implementar ML para previsões
5. [ ] Expandir para outros clientes

---

*Documentação criada em 2026-01-02*
*Sistema desenvolvido para Rodrigo (CMO) - Marketing Automation Agents*
