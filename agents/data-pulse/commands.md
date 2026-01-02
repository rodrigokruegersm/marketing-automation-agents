# DATA PULSE - Comandos e Uso

## Comandos Disponíveis

### Análise Rápida

```
/dados [cliente] hoje
```
Retorna métricas do dia atual (ou mais recente disponível).

**Exemplo:**
```
/dados brez hoje

📊 BREZ SCALES - DAILY PULSE (02/Jan/2026)

INVESTIMENTO TOTAL: $847.32
├── Meta Ads: $612.15 (72%)
└── Google Ads: $235.17 (28%)

MÉTRICAS DE AQUISIÇÃO:
├── Impressões: 45,231
├── Cliques: 892 (CTR: 1.97%)
├── Leads: 34 (CPL: $24.92)
└── CPC Médio: $0.95

MÉTRICAS DE CONVERSÃO:
├── Calls Agendadas: 8 (23.5% dos leads)
├── Calls Realizadas: 6 (75% show-up)
├── Vendas: 2
└── CAC: $423.66

RECEITA:
├── Receita Bruta: $5,994
├── ROAS: 7.07x
└── Lucro Bruto: $5,146.68

📈 VS ONTEM:
├── Spend: +12% ↑
├── Leads: +8% ↑
├── CPL: +3% ↑ (pior)
└── ROAS: -5% ↓ (pior)
```

---

### Análise Semanal

```
/dados [cliente] semana
```
Retorna consolidado da semana atual.

---

### Comparativo

```
/dados [cliente] comparar [período]
```
Compara período atual com anterior.

**Períodos válidos:**
- `dia` - Hoje vs ontem
- `semana` - Esta semana vs semana passada
- `mes` - Este mês vs mês passado

---

### Análise de Campanha

```
/dados [cliente] campanha [nome_ou_id]
```
Retorna métricas detalhadas de uma campanha específica.

---

### Winners e Losers

```
/dados [cliente] winners
```
Retorna os 5 ads com melhor performance (por ROAS ou CPL).

```
/dados [cliente] losers
```
Retorna os 5 ads com pior performance (candidatos a pausar).

---

### Anomalias

```
/dados [cliente] anomalias
```
Identifica métricas fora do padrão esperado.

**Output exemplo:**
```
⚠️ ANOMALIAS DETECTADAS - BREZ SCALES

🔴 CRÍTICO:
- CPL da campanha "VSL-Cold-Jan" está 45% acima da média ($52 vs $36)
- CTR do adset "Interest-Business" caiu 60% vs semana passada

🟡 ATENÇÃO:
- Frequência do "Retargeting-7d" chegou a 4.2 (limite: 3)
- CPC do Google subiu 25% nos últimos 3 dias

🟢 POSITIVO:
- Campanha "LAL-Buyers" com ROAS 12x (3x acima da média)
```

---

### Oportunidades

```
/dados [cliente] oportunidades
```
Identifica onde escalar ou otimizar.

**Output exemplo:**
```
✅ OPORTUNIDADES - BREZ SCALES

ESCALAR (performance acima da média):
1. "LAL-Buyers-1%" - ROAS 12x, CPL $18
   → Recomendação: Aumentar budget 30%

2. "Retargeting-Video50%" - ROAS 8x
   → Recomendação: Criar variações de criativo

OTIMIZAR (potencial não realizado):
1. "Cold-Interest" - Alto volume, CPL médio
   → Recomendação: Testar novos hooks

PAUSAR (drenar budget):
1. "Cold-Broad" - ROAS 0.8x há 5 dias
   → Recomendação: Pausar ou reformular
```

---

## Formato de Alertas Automáticos

Alertas são enviados automaticamente quando:

### 🔴 Alerta Crítico (Notificação imediata)
- ROAS < 1.5 por mais de 24h
- CPL > 150% da meta
- Spend > 120% do budget diário
- Taxa de erro > 5%

### 🟡 Alerta de Atenção (Resumo diário)
- ROAS < 2.5
- CPL > 120% da meta
- CTR < 0.5%
- Frequência > 3

### 🟢 Alerta Positivo (Oportunidade)
- ROAS > 5x
- CPL < 80% da meta
- CTR > 2%

---

## Integrações de Dados

### Fontes Primárias
- **Meta Ads API** → Campanhas, adsets, ads, métricas
- **Google Ads API** → Campanhas, grupos, métricas

### Fontes Secundárias (quando disponíveis)
- **GoHighLevel** → Leads, appointments, opportunities
- **Whop** → Vendas, receita
- **Typeform** → Submissions de formulário

### Destinos
- **Google Sheets** → Tracker consolidado
- **Slack** → Alertas e relatórios

---

## Configuração por Cliente

Cada cliente tem thresholds personalizados em `/clients/[cliente]/config.yaml`:

```yaml
metrics:
  targets:
    daily_spend: 500      # Budget diário esperado
    cpl_target: 35        # CPL meta
    roas_target: 4        # ROAS meta
    calls_per_day: 5      # Calls agendadas/dia

  alerts:
    cpl_max: 50           # CPL máximo antes de alertar
    roas_min: 2           # ROAS mínimo antes de alertar
    ctr_min: 0.8          # CTR mínimo (%)
    frequency_max: 3      # Frequência máxima
```
