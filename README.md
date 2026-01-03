# Adlytics - Intelligence for Scale

Sistema de automacao de marketing digital com agentes de IA.

---

## O que e o Adlytics?

O Adlytics e uma plataforma modular para gerenciar campanhas de anuncios
com inteligencia artificial. Ele segue uma arquitetura **"Celula + Tentaculos"**
onde um nucleo central (Core) conecta multiplos agentes plugaveis.

```
    [Traffic Agent] --- [Creative Agent] --- [Video Agent]
           \                  |                  /
            \                 |                 /
             +----------------+-----------------+
                              |
                         [  CORE  ]
                              |
              +---------------+---------------+
              |       |       |       |       |
           [Meta] [Hyros] [Leonardo] [Eleven] [HeyGen]
```

---

## Inicio Rapido

### 1. Executar Localmente

```bash
# Clonar repositorio
git clone https://github.com/rodrigokruegersm/marketing-automation-agents.git
cd marketing-automation-agents

# Instalar dependencias
pip install -r requirements.txt

# Configurar credenciais
cp .env.example .env
# Edite o .env com suas API keys

# Executar
streamlit run dashboard/app.py
```

### 2. Deploy no Streamlit Cloud

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Conecte o repositorio GitHub
3. Configure:
   - **Main file path:** `dashboard/app.py`
4. Adicione os Secrets (Settings → Secrets):
   ```toml
   DASHBOARD_PASSWORD = "sua_senha"
   META_ACCESS_TOKEN = "seu_token"
   META_AD_ACCOUNT_ID = "act_xxxxx"
   WHOP_API_KEY = "sua_chave"
   HYROS_API_KEY = "sua_chave"
   ```
5. Deploy!

---

## Estrutura do Projeto

```
Adlytics/
├── dashboard/          # Interface visual (Streamlit)
│   ├── app.py          # Aplicacao principal
│   ├── auth.py         # Autenticacao
│   └── components/     # Componentes reutilizaveis
│
├── core/               # Nucleo central (A Celula)
│   ├── adapters/       # Conectores para APIs
│   └── *.py            # Parsers e Registries
│
├── agents/             # Agentes de IA (Os Tentaculos)
│   ├── base.py         # Classe base
│   ├── traffic/        # Traffic Agent
│   ├── creative_lab/   # Creative Agent
│   ├── video_editor/   # Video Agent
│   └── copy_forge/     # Copy Agent
│
├── clients/            # Projetos de clientes
│   └── brazz-scales/   # Exemplo de projeto
│
├── config/             # Configuracoes
│   ├── settings.yaml   # Config geral
│   └── thresholds.yaml # Thresholds de performance
│
├── ARCHITECTURE.md     # Documentacao de arquitetura
└── requirements.txt    # Dependencias Python
```

---

## Funcionalidades

### Dashboard Principal
- KPIs em tempo real (Faturamento, Gastos, ROAS, Lucro)
- Funil de conversao visual
- Filtro por data e tag de campanha
- Seletor de projetos

### Traffic Agent
- Analise de campanhas com metricas completas
- Controle de campanhas (pausar, ativar, budget)
- AI Analysis baseado no metodo Jeremy Haines
- Funil visual com taxas de conversao

### Proximos Agentes
- **Creative Agent** - Geracao de imagens com Leonardo.ai
- **Video Agent** - Videos com ElevenLabs + HeyGen
- **Copy Agent** - Textos persuasivos com IA

---

## Integracoes

| Plataforma | Status | Para que serve |
|------------|--------|----------------|
| Meta Ads | Ativo | Metricas e controle de campanhas |
| Hyros | Ativo | Atribuicao de vendas |
| Leonardo.ai | Ativo | Geracao de imagens |
| ElevenLabs | Ativo | Geracao de voz |
| HeyGen | Ativo | Videos com avatar |
| Whop | Ativo | Vendas/checkout |

---

## Metodo Jeremy Haines

O Traffic Agent usa thresholds baseados no metodo Jeremy Haines:

| Metrica | Kill | Watch | Scale |
|---------|------|-------|-------|
| ROAS | < 1.0x | 1.0-1.5x | > 2.0x |
| CTR | < 0.8% | 0.8-1.5% | > 1.5% |
| Frequencia | > 3.5 | 2.5-3.5 | < 2.5 |

**Regra de ouro:** Nunca tome decisoes com dados do dia atual.
Compare sempre 3 dias vs 7 dias.

---

## Documentacao

| Documento | Descricao |
|-----------|-----------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Como o sistema funciona |
| [core/README.md](core/README.md) | Documentacao do Core |
| [agents/README.md](agents/README.md) | Como funcionam os Agentes |
| [dashboard/README.md](dashboard/README.md) | Documentacao do Dashboard |
| [config/README.md](config/README.md) | Configuracoes |
| [clients/README.md](clients/README.md) | Gerenciamento de projetos |

---

## Escalando para SaaS

O Adlytics esta preparado para se tornar um SaaS multi-tenant:

1. Adicionar banco de dados (PostgreSQL/Supabase)
2. Implementar autenticacao com Auth0
3. Criar sistema de billing com Stripe
4. Separar dados por tenant
5. Deploy em Railway/Render/AWS

---

## Contribuindo

1. Fork o repositorio
2. Crie uma branch: `git checkout -b feature/nova-feature`
3. Commit: `git commit -m "feat: descricao"`
4. Push: `git push origin feature/nova-feature`
5. Abra um Pull Request

---

## Licenca

Este projeto e privado. Todos os direitos reservados.

---

**Desenvolvido por:** Rodrigo Krueger
**Atualizado:** 2026-01-03
**Versao:** 3.2.0
