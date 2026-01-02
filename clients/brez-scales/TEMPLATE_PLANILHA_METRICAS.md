# TEMPLATE: Planilha de Métricas - Brez Scales

## Estrutura da Planilha Google Sheets

### Aba 1: DASHBOARD (Visão Geral)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BREZ SCALES - DASHBOARD                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PERÍODO: [Dropdown: Hoje | 7 dias | 30 dias | Mês atual | Custom]          │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   SPEND     │  │   LEADS     │  │   VENDAS    │  │   RECEITA   │        │
│  │  $12,450    │  │    423      │  │     28      │  │  $83,720    │        │
│  │   +15%      │  │    +22%     │  │    +8%      │  │   +12%      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    CPL      │  │    CAC      │  │    ROAS     │  │   MARGEM    │        │
│  │   $29.43    │  │   $444.64   │  │    6.72x    │  │    85%      │        │
│  │   -5% ✅    │  │   +3% ⚠️   │  │   -2% ⚠️   │  │   +1% ✅    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                                             │
│  [GRÁFICO: Spend vs Revenue - Últimos 30 dias]                             │
│                                                                             │
│  [GRÁFICO: Funil - Leads → Calls → Vendas]                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Aba 2: DAILY TRACKER (Dados Diários)

| Data | Spend Meta | Spend Google | Spend Total | Impressões | Cliques | CTR | Leads | CPL | Calls Agendadas | Calls Realizadas | Show-up % | Vendas | Receita | CAC | ROAS |
|------|------------|--------------|-------------|------------|---------|-----|-------|-----|-----------------|------------------|-----------|--------|---------|-----|------|
| 2026-01-01 | $500 | $200 | $700 | 35000 | 720 | 2.06% | 28 | $25.00 | 7 | 5 | 71% | 2 | $5994 | $350 | 8.56x |
| 2026-01-02 | $612 | $235 | $847 | 45231 | 892 | 1.97% | 34 | $24.91 | 8 | 6 | 75% | 2 | $5994 | $423 | 7.08x |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Colunas calculadas automaticamente:**
- CTR = Cliques ÷ Impressões
- CPL = Spend Total ÷ Leads
- Show-up % = Calls Realizadas ÷ Calls Agendadas
- CAC = Spend Total ÷ Vendas
- ROAS = Receita ÷ Spend Total

---

### Aba 3: CAMPAIGN TRACKER (Por Campanha)

| Campanha | Tipo | Status | Spend | Impressões | Cliques | CTR | Leads | CPL | Conversões | CPA | ROAS | Dias Ativo | Notas |
|----------|------|--------|-------|------------|---------|-----|-------|-----|------------|-----|------|------------|-------|
| Brez - Cold - VSL Jan | Cold | Active | $1,200 | 82,000 | 1,640 | 2.0% | 52 | $23.08 | 4 | $300 | 10x | 5 | Winner |
| Brez - RTG - 7d | RTG | Active | $450 | 15,000 | 890 | 5.9% | 28 | $16.07 | 3 | $150 | 20x | 12 | Escalar |
| Brez - Cold - Hook2 | Cold | Paused | $380 | 28,000 | 420 | 1.5% | 8 | $47.50 | 0 | - | 0x | 3 | CPL alto |

---

### Aba 4: AD TRACKER (Por Anúncio)

| Ad ID | Campanha | Criativo | Copy | Formato | Spend | Impressões | CTR | Leads | CPL | Status | Observações |
|-------|----------|----------|------|---------|-------|------------|-----|-------|-----|--------|-------------|
| 123456 | Cold VSL Jan | video_hook1.mp4 | Copy A | Video 9:16 | $320 | 18,000 | 2.3% | 14 | $22.86 | Active | Top performer |
| 123457 | Cold VSL Jan | video_hook2.mp4 | Copy A | Video 9:16 | $280 | 16,000 | 1.8% | 10 | $28.00 | Active | OK |
| 123458 | Cold VSL Jan | image_static1.jpg | Copy B | Image 1:1 | $150 | 12,000 | 1.2% | 4 | $37.50 | Paused | Baixo CTR |

---

### Aba 5: FUNIL DETALHADO

#### Estágios do Funil Brez Scales:

| Estágio | Métrica | Meta | Atual | Status | Ação |
|---------|---------|------|-------|--------|------|
| **1. Impressão → Clique** | CTR | >1.5% | 1.97% | ✅ | - |
| **2. Clique → Lead** | Conv. Rate | >3% | 3.81% | ✅ | - |
| **3. Lead → Call Agendada** | Taxa Agend. | >25% | 23.5% | ⚠️ | Melhorar copy follow-up |
| **4. Call Agend. → Realizada** | Show-up | >75% | 75% | ✅ | - |
| **5. Call → Venda** | Close Rate | >25% | 33% | ✅ | - |

#### Métricas de Funil (Semana Atual)

```
TOPO DO FUNIL (Ads):
├── Impressões: 180,924
├── Cliques: 3,564 (CTR: 1.97%)
└── Custo: $3,388

MEIO DO FUNIL (Leads):
├── Leads gerados: 136
├── CPL: $24.91
├── Leads qualificados: 98 (72%)
└── Calls agendadas: 32 (23.5%)

FUNDO DO FUNIL (Vendas):
├── Calls realizadas: 24 (75% show-up)
├── Vendas: 8 (33% close rate)
├── Ticket médio: $2,997
└── Receita: $23,976

RESUMO:
├── CAC: $423.50
├── ROAS: 7.08x
└── LTV projetado: $8,991 (3 compras)
```

---

### Aba 6: METAS E PROJEÇÕES

| Métrica | Meta Diária | Meta Semanal | Meta Mensal | Atual (MTD) | % da Meta | Projeção |
|---------|-------------|--------------|-------------|-------------|-----------|----------|
| Spend | $800 | $5,600 | $24,000 | $1,547 | 6.4% | $24,752 |
| Leads | 40 | 280 | 1,200 | 62 | 5.2% | $992 |
| Vendas | 3 | 21 | 90 | 4 | 4.4% | 64 |
| Receita | $9,000 | $63,000 | $270,000 | $11,988 | 4.4% | $191,808 |

---

### Aba 7: ALERTAS E LOG

| Data | Hora | Tipo | Métrica | Valor | Threshold | Ação Tomada |
|------|------|------|---------|-------|-----------|-------------|
| 2026-01-02 | 14:30 | 🔴 Crítico | CPL Campanha X | $58 | $50 | Pausada |
| 2026-01-02 | 09:00 | 🟡 Atenção | CTR Adset Y | 0.7% | 0.8% | Monitorando |
| 2026-01-01 | 16:45 | 🟢 Positivo | ROAS Campanha Z | 12x | >5x | Escalada +20% |

---

## Fórmulas Importantes

### CPL (Custo por Lead)
```
=Spend/Leads
```

### CAC (Custo de Aquisição)
```
=Spend/Vendas
```

### ROAS (Return on Ad Spend)
```
=Receita/Spend
```

### Taxa de Conversão
```
=Leads/Cliques
```

### Show-up Rate
```
=CallsRealizadas/CallsAgendadas
```

### Close Rate
```
=Vendas/CallsRealizadas
```

### Projeção Mensal
```
=ValorAtualMTD/DiasPassados*DiasNoMês
```

---

## Automação com Data Pulse

O agente Data Pulse irá:

1. **Diariamente às 7am:**
   - Puxar dados do Meta Ads e Google Ads
   - Atualizar aba DAILY TRACKER
   - Recalcular métricas do DASHBOARD
   - Enviar Daily Pulse no Slack

2. **Em tempo real:**
   - Monitorar thresholds
   - Registrar alertas na aba ALERTAS
   - Notificar via Slack quando crítico

3. **Semanalmente:**
   - Gerar resumo comparativo
   - Atualizar projeções
   - Identificar trends

---

## Próximo Passo

Quando você definir as **métricas específicas do funil do Brez Scales**, eu atualizo este template com:
1. Os estágios exatos do seu funil
2. As metas específicas de cada etapa
3. Os eventos de conversão corretos
4. As integrações necessárias (GHL, Whop, etc.)

**Me diga:**
- Quais são os estágios do funil?
- Qual o ticket médio?
- Quais eventos você tracka no pixel?
- Quais metas você quer bater?
