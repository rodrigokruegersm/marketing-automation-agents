# Core - O Cerebro do Sistema

Esta pasta contem o **nucleo central** do Adlytics - a "celula" que conecta
todos os outros componentes.

---

## Estrutura

```
core/
├── __init__.py              # Exporta todos os modulos
├── adapters/                # Conectores para APIs externas
│   ├── meta_ads.py          # Meta Ads API
│   ├── hyros.py             # Hyros Attribution
│   ├── leonardo.py          # Leonardo.ai (imagens)
│   ├── elevenlabs.py        # ElevenLabs (voz)
│   ├── heygen.py            # HeyGen (videos)
│   ├── creatomate.py        # Creatomate (templates)
│   └── checkout/            # Plataformas de checkout
│       ├── whop.py
│       ├── stripe.py
│       ├── hotmart.py
│       └── kiwify.py
│
├── campaign_parser.py       # Interpreta dados de campanhas
├── client_registry.py       # Gerencia clientes/projetos
├── product_registry.py      # Gerencia produtos
├── funnel_registry.py       # Gerencia funis
└── data_aggregator.py       # Agrega dados de multiplas fontes
```

---

## O que cada arquivo faz

### Adapters (Conectores)

Os **adapters** sao responsaveis por conectar com APIs externas.
Cada adapter segue o mesmo padrao:

```python
class NomeAdapter:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_data(self, params):
        # Busca dados da API
        pass

    def send_action(self, action, params):
        # Envia acoes para a API
        pass
```

### Parsers

Os **parsers** transformam dados brutos em informacoes uteis:

- `campaign_parser.py` - Interpreta dados de campanhas do Meta Ads
- `data_aggregator.py` - Combina dados de multiplas fontes

### Registries

Os **registries** gerenciam entidades do sistema:

- `client_registry.py` - Clientes/Projetos
- `product_registry.py` - Produtos/Ofertas
- `funnel_registry.py` - Funis de vendas

---

## Como usar

```python
from core import MetaAdsAdapter, HyrosAdapter, CampaignParser

# Conectar com Meta Ads
meta = MetaAdsAdapter(api_key="seu_token")
campaigns = meta.get_campaigns()

# Conectar com Hyros
hyros = HyrosAdapter(api_key="sua_chave")
sales = hyros.get_sales()
```

---

## Adicionando novos Adapters

1. Crie um arquivo em `adapters/novo_adapter.py`
2. Siga o padrao dos adapters existentes
3. Exporte no `adapters/__init__.py`
4. Adicione ao `core/__init__.py`

---

**Dica:** Todos os adapters usam cache para evitar chamadas excessivas a APIs.
