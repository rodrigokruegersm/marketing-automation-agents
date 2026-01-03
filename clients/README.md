# Clients - Projetos de Clientes

Esta pasta contem os dados e configuracoes de cada projeto/cliente
gerenciado pelo Adlytics.

---

## Estrutura

Cada cliente tem sua propria pasta com:

```
clients/
└── nome-do-cliente/
    ├── config.yaml       # Configuracoes do projeto
    ├── products/         # Produtos/Ofertas
    │   └── main_offer.yaml
    ├── funnels/          # Funis de vendas
    │   └── vsl_challenge.yaml
    ├── data/             # Dados e logs
    │   └── action_log.json
    └── reports/          # Relatorios gerados
        └── daily_pulse_2026-01-03.md
```

---

## Projetos Atuais

| Projeto | Pasta | Descricao |
|---------|-------|-----------|
| Brazz Scales | `brazz-scales/` | E-commerce de balancas |

---

## config.yaml

Cada projeto tem um arquivo de configuracao:

```yaml
# clients/brazz-scales/config.yaml

project:
  id: "brazz-scales"
  name: "Brazz Scales"
  icon: "balance"
  description: "E-commerce de balancas"

# Conexoes
meta_ads:
  account_id: "act_xxxxx"

# Tags de campanha usadas
campaign_tags:
  - "[bsb]"
  - "[bs]"
  - "[brazz]"

# Metas
targets:
  monthly_revenue: 50000
  target_roas: 2.5
  target_cpa: 35
```

---

## Products (Produtos)

Cada produto e definido em um arquivo YAML:

```yaml
# products/main_offer.yaml

product:
  id: "balanca-precision-pro"
  name: "Balanca Precision Pro"
  price: 297.00
  cost: 89.00
  margin: 208.00

  # Funis onde e vendido
  funnels:
    - vsl_challenge
    - direct_offer

  # Metricas de conversao
  metrics:
    conversion_rate: 2.5
    average_order_value: 312.00
```

---

## Funnels (Funis)

Cada funil de vendas:

```yaml
# funnels/vsl_challenge.yaml

funnel:
  id: "vsl_challenge"
  name: "VSL + Challenge"
  type: "vsl"

  # Etapas do funil
  steps:
    - name: "Landing Page"
      url: "/lp"
      event: "landing_page_view"

    - name: "VSL"
      url: "/vsl"
      event: "view_content"

    - name: "Checkout"
      url: "/checkout"
      event: "initiate_checkout"

    - name: "Obrigado"
      url: "/obrigado"
      event: "purchase"
```

---

## Adicionando Novo Cliente

1. **Criar pasta:**
```bash
mkdir -p clients/novo-cliente/{products,funnels,data,reports}
```

2. **Criar config.yaml:**
```bash
touch clients/novo-cliente/config.yaml
```

3. **Registrar no Dashboard:**

Edite `dashboard/app.py` e adicione ao `PROJECTS`:

```python
PROJECTS = {
    'Brazz Scales': {...},
    'Novo Cliente': {
        'id': 'novo-cliente',
        'icon': 'emoji',
        'description': 'Descricao',
        'default_tags': ['[tag1]', '[tag2]']
    }
}
```

---

## Boas Praticas

- Cada cliente deve ter sua propria pasta
- Use nomes em kebab-case: `nome-do-cliente`
- Mantenha dados sensiveis fora do git (.gitignore)
- Documente as tags de campanha usadas
- Atualize os targets mensalmente

---

## Migrando para Multi-Tenant

Quando escalar para SaaS com multiplos usuarios:

1. Mover dados para banco de dados
2. Associar clientes a usuarios
3. Implementar permissoes de acesso
4. Separar dados por tenant_id

---

**Dica:** Mantenha um cliente de exemplo/template
para facilitar onboarding de novos projetos.
