# Adlytics - Arquitetura do Sistema

## Visao Geral

O Adlytics segue uma arquitetura **"Celula + Tentaculos"** - um nucleo central inteligente
com modulos plugaveis que podem ser adicionados ou removidos conforme necessario.

```
                              +------------------+
                              |    DASHBOARD     |
                              |   (Interface)    |
                              +--------+---------+
                                       |
                    +------------------+------------------+
                    |                  |                  |
              +-----+-----+      +-----+-----+      +-----+-----+
              |  TRAFFIC  |      |  CREATIVE |      |   VIDEO   |
              |   AGENT   |      |   AGENT   |      |   AGENT   |
              +-----------+      +-----------+      +-----------+
                    \                  |                  /
                     \                 |                 /
                      +----------------+-----------------+
                                       |
                              +--------+--------+
                              |      CORE       |
                              |   (A Celula)    |
                              |                 |
                              | - Adapters      |
                              | - Parsers       |
                              | - Registry      |
                              +-----------------+
                                       |
              +------------------------+------------------------+
              |            |           |           |            |
         +----+----+  +----+----+ +----+----+ +----+----+  +----+----+
         |  META   |  | HYROS   | |LEONARDO | |ELEVENLABS|  | HEYGEN  |
         |   ADS   |  |         | |   .AI   | |         |  |         |
         +---------+  +---------+ +---------+ +---------+  +---------+
                              APIs Externas
```

---

## A Celula (Core)

O **CORE** e o cerebro do sistema. Ele:

- **Conecta** com todas as APIs externas (Meta, Hyros, Leonardo, etc.)
- **Processa** os dados recebidos
- **Fornece** informacoes para os agentes
- **Armazena** configuracoes de clientes e projetos

### Componentes do Core:

| Pasta | O que faz |
|-------|-----------|
| `adapters/` | Conectores para APIs externas (Meta Ads, Hyros, Leonardo.ai, etc.) |
| `campaign_parser.py` | Interpreta dados de campanhas |
| `client_registry.py` | Gerencia clientes/projetos |
| `product_registry.py` | Gerencia produtos |
| `funnel_registry.py` | Gerencia funis de vendas |
| `data_aggregator.py` | Agrega dados de multiplas fontes |

---

## Os Tentaculos (Agents)

Cada **AGENTE** e um modulo independente que pode ser plugado ou removido.
Eles usam o Core para obter dados e executar acoes.

### Agentes Atuais:

| Agente | Funcao | Status |
|--------|--------|--------|
| **Traffic Agent** | Analisa campanhas, sugere otimizacoes | Ativo |
| **Creative Agent** | Gera imagens com Leonardo.ai | Ativo |
| **Video Agent** | Cria videos com ElevenLabs + HeyGen | Ativo |
| **Copy Agent** | Gera textos persuasivos | Em desenvolvimento |
| **Performance Agent** | Otimiza performance automaticamente | Planejado |
| **Audience Agent** | Constroi audiencias | Planejado |

### Como Adicionar um Novo Agente:

1. Crie uma pasta em `agents/seu_agente/`
2. Herde da classe `BaseAgent` em `agents/base.py`
3. Implemente os metodos `analyze()` e `execute()`
4. Registre no `agents/__init__.py`
5. Adicione a interface no Dashboard

---

## O Dashboard (Interface)

O **DASHBOARD** e a interface visual que o usuario interage.
Construido com Streamlit, ele:

- Mostra metricas em tempo real
- Permite alternar entre projetos
- Filtra dados por tags de campanha
- Controla campanhas (pausar, ativar, alterar budget)
- Exibe recomendacoes da IA

### Componentes do Dashboard:

| Arquivo | O que faz |
|---------|-----------|
| `app.py` | Aplicacao principal |
| `auth.py` | Sistema de login |
| `components/` | Componentes reutilizaveis da UI |

---

## Projetos (Clients)

Cada **PROJETO** representa um cliente ou negocio diferente.
Atualmente: **Brazz Scales**

### Estrutura de um Projeto:

```
projects/brazz-scales/
├── config.yaml          # Configuracoes do projeto
├── products/            # Produtos/Ofertas
├── funnels/             # Funis de vendas
└── data/                # Dados e logs
```

---

## Fluxo de Dados

```
1. Usuario acessa o Dashboard
          |
          v
2. Dashboard busca dados via Core
          |
          v
3. Core conecta com APIs (Meta, Hyros, etc.)
          |
          v
4. Dados sao processados e agregados
          |
          v
5. Agentes analisam e geram recomendacoes
          |
          v
6. Resultados exibidos no Dashboard
```

---

## APIs Integradas

| Plataforma | Para que serve | Adapter |
|------------|----------------|---------|
| **Meta Ads** | Metricas de anuncios, controle de campanhas | `meta_ads.py` |
| **Hyros** | Atribuicao de vendas | `hyros.py` |
| **Leonardo.ai** | Geracao de imagens | `leonardo.py` |
| **ElevenLabs** | Geracao de voz/audio | `elevenlabs.py` |
| **HeyGen** | Videos com avatares | `heygen.py` |
| **Creatomate** | Templates de video | `creatomate.py` |
| **Whop** | Vendas/checkout | `checkout/whop.py` |

---

## Escalando para SaaS

Para transformar em SaaS multi-tenant:

1. **Banco de Dados**: Adicionar PostgreSQL/Supabase para usuarios
2. **Autenticacao**: Integrar com Auth0 ou Supabase Auth
3. **Multi-tenancy**: Cada usuario ve apenas seus projetos
4. **Billing**: Integrar Stripe para cobrancas
5. **Deploy**: Usar Railway, Render ou AWS

### Proximos Passos Recomendados:

- [ ] Adicionar banco de dados para persistencia
- [ ] Implementar sistema de usuarios
- [ ] Criar API REST para acesso externo
- [ ] Adicionar webhooks para automacoes
- [ ] Implementar fila de tarefas (Celery/Redis)

---

## Tecnologias Utilizadas

- **Python 3.10+** - Linguagem principal
- **Streamlit** - Interface do Dashboard
- **Plotly** - Graficos interativos
- **Requests** - Chamadas de API
- **Pandas** - Manipulacao de dados

---

**Atualizado:** 2026-01-03
