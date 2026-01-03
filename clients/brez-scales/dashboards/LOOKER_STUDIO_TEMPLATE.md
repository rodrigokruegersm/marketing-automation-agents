# Looker Studio Dashboard - Brez Scales
## Paid Challenge Funnel Performance

---

## Dashboard Structure

### Page 1: Executive Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  BREZ SCALES - PAID CHALLENGE FUNNEL                    [Date Range Picker] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   SPEND     │  │  REVENUE    │  │    ROAS     │  │  PURCHASES  │        │
│  │  $3,644.71  │  │  $9,095.86  │  │    2.50x    │  │     241     │        │
│  │   ▲ +12%    │  │   ▲ +18%    │  │   ▲ +5%     │  │   ▲ +15%    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                                             │
│  ┌────────────────────────────────────┐  ┌────────────────────────────────┐│
│  │     SPEND vs REVENUE (7 Days)      │  │      FUNNEL CONVERSION         ││
│  │                                    │  │                                ││
│  │  $5k ┤         ╭─────              │  │  Impressions    422,763        ││
│  │      │    ╭────╯                   │  │       │                        ││
│  │  $3k ┤────╯                        │  │       ▼  2.42%                 ││
│  │      │                             │  │  Clicks         10,231         ││
│  │  $1k ┤                             │  │       │                        ││
│  │      └────────────────────         │  │       ▼  46.1%                 ││
│  │       D1  D2  D3  D4  D5  D6  D7   │  │  LP Views       4,714          ││
│  │                                    │  │       │                        ││
│  │  ── Spend  ── Revenue              │  │       ▼  7.59%                 ││
│  └────────────────────────────────────┘  │  Checkouts      358            ││
│                                          │       │                        ││
│                                          │       ▼  67.3%                 ││
│                                          │  Purchases      241            ││
│                                          └────────────────────────────────┘│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Page 2: Media Buying Metrics

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  MEDIA BUYING KPIs                                      [Date Range Picker] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────┐ │
│  │   CPM    │ │   CPC    │ │   CTR    │ │  CPP     │ │  FREQ    │ │ REACH│ │
│  │  $8.62   │ │  $0.36   │ │  2.42%   │ │ $15.12   │ │  2.41    │ │ 175K │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────┘ │
│                                                                             │
│  ┌────────────────────────────────────┐  ┌────────────────────────────────┐│
│  │      COST METRICS TREND            │  │      EFFICIENCY METRICS        ││
│  │                                    │  │                                ││
│  │  $20 ┤                             │  │  CTR     ████████████  2.42%   ││
│  │      │                             │  │  CVR     ████████      2.35%   ││
│  │  $15 ┤ ─ ─ ─ ─ ─ ─ ─ ─ ─ CPP      │  │  ROAS    █████████████ 2.50x   ││
│  │      │                             │  │                                ││
│  │  $10 ┤ ─ ─ ─ ─ ─ ─ ─ ─ CPI        │  │  Target vs Actual:             ││
│  │      │                             │  │  ┌─────────────────────────┐   ││
│  │  $5  ┤                             │  │  │ ROAS   [====>    ] 2.50x│   ││
│  │      └────────────────────         │  │  │ Target [    |    ] 2.00x│   ││
│  │       D1  D2  D3  D4  D5  D6  D7   │  │  └─────────────────────────┘   ││
│  └────────────────────────────────────┘  └────────────────────────────────┘│
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  DAILY BREAKDOWN TABLE                                               │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  Date       │ Spend    │ Revenue  │ ROAS  │ Purch │ CPP    │ CTR    │  │
│  ├─────────────┼──────────┼──────────┼───────┼───────┼────────┼────────┤  │
│  │  2026-01-01 │ $1,850.80│ $4,217.86│ 2.28x │  116  │ $15.96 │ 2.24%  │  │
│  │  2025-12-31 │ $1,200.00│ $3,200.00│ 2.67x │   85  │ $14.12 │ 2.51%  │  │
│  │  2025-12-30 │ $593.91  │ $1,678.00│ 2.83x │   40  │ $14.85 │ 2.48%  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Page 3: Funnel Deep Dive

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  FUNNEL ANALYSIS - PAID CHALLENGE                       [Date Range Picker] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        CONVERSION FUNNEL                            │   │
│  │                                                                     │   │
│  │  ╔═══════════════════════════════════════════════════════════════╗  │   │
│  │  ║                    IMPRESSIONS: 422,763                       ║  │   │
│  │  ╚═══════════════════════════════════════════════════════════════╝  │   │
│  │                              │                                      │   │
│  │                         CTR: 2.42%                                  │   │
│  │                              ▼                                      │   │
│  │      ╔═══════════════════════════════════════════════════╗         │   │
│  │      ║              CLICKS: 10,231                       ║         │   │
│  │      ╚═══════════════════════════════════════════════════╝         │   │
│  │                              │                                      │   │
│  │                      LP Rate: 46.1%                                 │   │
│  │                              ▼                                      │   │
│  │          ╔═══════════════════════════════════════╗                 │   │
│  │          ║      LP VIEWS: 4,714                  ║                 │   │
│  │          ╚═══════════════════════════════════════╝                 │   │
│  │                              │                                      │   │
│  │                      IC Rate: 7.59%                                 │   │
│  │                              ▼                                      │   │
│  │              ╔═══════════════════════════════╗                     │   │
│  │              ║   INIT CHECKOUT: 358          ║                     │   │
│  │              ╚═══════════════════════════════╝                     │   │
│  │                              │                                      │   │
│  │                      Close Rate: 67.3%                              │   │
│  │                              ▼                                      │   │
│  │                  ╔═══════════════════════════╗                     │   │
│  │                  ║   PURCHASES: 241          ║                     │   │
│  │                  ╚═══════════════════════════╝                     │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────────┐  │
│  │   COST PER STAGE            │  │   CONVERSION RATES BY DAY           │  │
│  │                             │  │                                     │  │
│  │   CPM:     $8.62            │  │   100% ┤                            │  │
│  │   CPC:     $0.36            │  │        │  ── CTR                    │  │
│  │   CPLPV:   $0.77            │  │    10% ┤  ── LP Rate                │  │
│  │   CPIC:    $10.18           │  │        │  ── IC Rate                │  │
│  │   CPP:     $15.12           │  │     1% ┤  ── Close Rate             │  │
│  │                             │  │        └────────────────────        │  │
│  │   Revenue/Purchase: $37.74  │  │         D1  D2  D3  D4  D5          │  │
│  └─────────────────────────────┘  └─────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Page 4: Financial & Agency Metrics

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  FINANCIAL DASHBOARD                                    [Date Range Picker] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     PROFIT & COMMISSION                             │   │
│  │                                                                     │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐        │   │
│  │  │   REVENUE      │  │   AD SPEND     │  │   GROSS PROFIT │        │   │
│  │  │   $9,095.86    │  │   $3,644.71    │  │   $5,451.15    │        │   │
│  │  │   ████████████ │  │   █████        │  │   ███████      │        │   │
│  │  └────────────────┘  └────────────────┘  └────────────────┘        │   │
│  │                                                                     │   │
│  │  ┌────────────────────────────────────────────────────────────┐    │   │
│  │  │  AGENCY COMMISSION (20% of Profit)                         │    │   │
│  │  │                                                            │    │   │
│  │  │  This Period:  $1,090.23                                   │    │   │
│  │  │  Weekly Proj:  $2,543.87                                   │    │   │
│  │  │  Monthly Proj: $10,902.02                                  │    │   │
│  │  └────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌────────────────────────────────────┐  ┌────────────────────────────────┐│
│  │      REVENUE vs AD SPEND           │  │      PROFIT MARGIN %           ││
│  │                                    │  │                                ││
│  │  $10k┤      ╭──── Revenue          │  │   80% ┤                        ││
│  │      │  ╭───╯                      │  │       │                        ││
│  │  $5k ┤──╯     ╭──── Spend          │  │   60% ┤  ─────────────────     ││
│  │      │    ╭───╯                    │  │       │                        ││
│  │  $0  ┤────╯                        │  │   40% ┤                        ││
│  │      └────────────────────         │  │       └────────────────────    ││
│  │       D1  D2  D3  D4  D5  D6  D7   │  │        D1  D2  D3  D4  D5      ││
│  └────────────────────────────────────┘  └────────────────────────────────┘│
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  PROJECTION TABLE                                                    │  │
│  ├───────────────┬───────────┬───────────┬───────────┬─────────────────┤  │
│  │  Period       │ Spend     │ Revenue   │ Profit    │ Commission (20%)│  │
│  ├───────────────┼───────────┼───────────┼───────────┼─────────────────┤  │
│  │  Daily Avg    │ $1,214.90 │ $3,031.95 │ $1,817.05 │ $363.41         │  │
│  │  Weekly       │ $8,504.32 │ $21,223.68│ $12,719.36│ $2,543.87       │  │
│  │  Monthly      │ $36,448.53│ $90,958.65│ $54,510.12│ $10,902.02      │  │
│  │  Quarterly    │ $109,345  │ $272,875  │ $163,530  │ $32,706         │  │
│  └───────────────┴───────────┴───────────┴───────────┴─────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## KPIs Definition

### Primary KPIs (Scorecards)

| KPI | Formula | Target | Alert |
|-----|---------|--------|-------|
| **ROAS** | Revenue / Spend | > 2.0x | < 1.8x |
| **CPP** | Spend / Purchases | < $25 | > $30 |
| **Revenue** | Sum of Purchase Values | Growing | Declining 3d |
| **Purchases** | Count of Conversions | Growing | Declining 3d |

### Secondary KPIs

| KPI | Formula | Target | Alert |
|-----|---------|--------|-------|
| **CTR** | Clicks / Impressions | > 1.5% | < 1.0% |
| **CPC** | Spend / Clicks | < $0.50 | > $0.75 |
| **CPM** | (Spend / Impressions) × 1000 | < $12 | > $15 |
| **Frequency** | Impressions / Reach | < 3.0 | > 4.0 |
| **LP View Rate** | LP Views / Clicks | > 40% | < 30% |
| **IC Rate** | Init Checkout / LP Views | > 5% | < 3% |
| **Close Rate** | Purchases / Init Checkout | > 50% | < 40% |

### Financial KPIs

| KPI | Formula | Target |
|-----|---------|--------|
| **Gross Profit** | Revenue - Spend | Positive |
| **Profit Margin** | Profit / Revenue | > 50% |
| **Agency Commission** | Profit × 20% | Tracking |
| **AOV** | Revenue / Purchases | Stable |

---

## Data Source Configuration

### Google Sheets Structure

Create a Google Sheet with these tabs:

#### Tab 1: Daily_Data
```
date | spend | revenue | impressions | reach | clicks | link_clicks | lp_views | init_checkout | add_payment | purchases | purchase_value
```

#### Tab 2: Calculated_Metrics
```
date | roas | cpm | cpc | ctr | cpp | lp_rate | ic_rate | close_rate | profit | margin | commission
```

#### Tab 3: Targets
```
metric | target_value | alert_low | alert_high
```

---

## Looker Studio Setup Steps

### 1. Create Data Source
1. Open Looker Studio → Create → Data Source
2. Select Google Sheets
3. Connect your spreadsheet
4. Import both tabs

### 2. Create Calculated Fields

```sql
-- ROAS
revenue / spend

-- Profit
revenue - spend

-- Profit Margin
(revenue - spend) / revenue * 100

-- Commission (20%)
(revenue - spend) * 0.20

-- LP View Rate
lp_views / clicks * 100

-- IC Rate
init_checkout / lp_views * 100

-- Close Rate
purchases / init_checkout * 100

-- AOV
revenue / purchases
```

### 3. Create Dashboard Pages
- Follow the layouts above
- Use Scorecards for primary KPIs
- Use Time Series for trends
- Use Tables for detailed data
- Use Bar Charts for comparisons

### 4. Add Conditional Formatting
- Green: Above target
- Yellow: Near target
- Red: Below alert threshold

---

## Quick Access Link

To create this dashboard:
1. Copy the Google Sheet template (next file)
2. Go to: https://lookerstudio.google.com
3. Create new report
4. Connect to your Google Sheet
5. Follow the layout templates above

---

## Automation Options

### Option 1: Manual Update
- Export CSV from Meta Ads Manager daily
- Paste into Google Sheets
- Dashboard updates automatically

### Option 2: Supermetrics (Recommended)
- Install Supermetrics for Google Sheets
- Connect Meta Ads account
- Schedule automatic daily refresh

### Option 3: API Integration
- Use Meta Marketing API
- Custom script to populate sheet
- Run via cron or scheduled function

---

*Template created: 2026-01-02*
*Client: Brez Scales*
*Preset: Meta Ads Sales Columns*
