# DOCUMENTO 3: ROADMAP DE AUTOMAÇÃO E ARQUITETURA DE AGENTES
## Especificação Técnica Completa

**Data:** 2026-01-02
**Versão:** 1.0
**Responsável Técnico:** Rodrigo (CMO)

---

## PARTE 1: VISÃO GERAL DA ARQUITETURA

### 1.1 Filosofia de Automação

```
PRINCÍPIOS FUNDAMENTAIS:

1. AUTOMATIZAR O REPETITIVO, NÃO O ESTRATÉGICO
   └── IA faz: Preencher planilhas, gerar variações, compilar dados
   └── Humano faz: Decidir estratégia, aprovar, relacionamento

2. COMEÇAR PELO QUE LIBERA OS FOUNDERS
   └── Prioridade 1: Tarefas que consomem tempo de Rodrigo e Pierre
   └── Prioridade 2: Tarefas que consomem tempo de equipe fixa
   └── Prioridade 3: Substituição de funções comissionadas

3. IMPLEMENTAR GRADUALMENTE
   └── Um agente por vez
   └── Validar antes de escalar
   └── Manter fallback humano sempre

4. MEDIR ANTES E DEPOIS
   └── Tempo gasto na tarefa (antes)
   └── Tempo gasto na tarefa (depois)
   └── Qualidade do output (comparativo)
```

### 1.2 Arquitetura de Alto Nível

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         COMMAND CENTER                                   │
│                    (Orquestrador Central)                                │
├─────────────────────────────────────────────────────────────────────────┤
│  Recebe comandos → Roteia para agente correto → Consolida outputs       │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│   MARKETING OPS   │   │    SALES OPS      │   │   BUSINESS OPS    │
│      LAYER        │   │      LAYER        │   │      LAYER        │
├───────────────────┤   ├───────────────────┤   ├───────────────────┤
│ • Copy Forge      │   │ • Setter Virtual  │   │ • Report Engine   │
│ • Ad Manager      │   │ • Lead Intel      │   │ • Spreadsheet Auto│
│ • Creative Lab    │   │ • Performance     │   │ • Alert System    │
└───────────────────┘   └───────────────────┘   └───────────────────┘
```

---

## PARTE 2: ESPECIFICAÇÃO DOS AGENTES (Formato YAML)

### AGENTE 1: SPREADSHEET AUTOMATOR

```yaml
nome: Spreadsheet Automator
objetivo: Automatizar preenchimento e atualização de todas as planilhas de tracking da agência
substitui: 4-6 horas/semana de trabalho manual (Rodrigo + Noah)

triggers:
  - Comando manual: "/planilha atualizar [cliente]"
  - Agendado: Todo dia às 7am (dados do dia anterior)
  - Evento: Quando Report Engine gera novos dados

inputs:
  - Dados de ads (Meta, Google) via API
  - Dados de vendas (do CRM de cada cliente)
  - Dados de faturamento (Stripe, PayPal, Hotmart)

outputs:
  - Planilha de tracking atualizada
  - Alerta se dados inconsistentes
  - Log de atualizações

mcps_necessarios:
  - "@anthropic/mcp-server-google-sheets"  # Ler e escrever planilhas
  - "@anthropic/mcp-server-filesystem"     # Acessar arquivos locais
  - "custom/meta-ads-api"                  # Dados de Facebook/Instagram
  - "custom/google-ads-api"                # Dados de Google Ads

economia_estimada:
  tempo: 5 horas/semana
  valor: ~$600/mês (tempo de equipe)

prioridade: ALTA (Implementar primeiro)

prompt_do_agente: |
  Você é o Spreadsheet Automator, responsável por manter todas as planilhas
  de tracking da agência atualizadas e precisas.

  FUNÇÃO: Puxar dados de múltiplas fontes e consolidar em planilhas padronizadas.

  REGRAS:
  1. NUNCA modificar dados históricos, apenas adicionar novos
  2. Se encontrar inconsistência, ALERTAR e não sobrescrever
  3. Manter log de todas as atualizações
  4. Formatar números conforme padrão ($ para valores, % para percentuais)

  FORMATO DE OUTPUT:
  {
    "planilha": "nome_da_planilha",
    "celulas_atualizadas": 42,
    "inconsistencias": [],
    "timestamp": "2026-01-02T07:00:00Z"
  }
```

---

### AGENTE 2: REPORT ENGINE

```yaml
nome: Report Engine
objetivo: Gerar relatórios automáticos consolidando dados de todas as fontes
substitui: 6-8 horas/semana de compilação manual de relatórios

triggers:
  - Agendado Daily: Segunda a Sexta, 7am → Daily Pulse
  - Agendado Weekly: Segunda, 8am → Weekly Deep Dive
  - Agendado Monthly: Dia 1, 9am → Monthly Review
  - Manual: "/relatorio [tipo] [cliente]"
  - Alerta: Quando métricas saem do threshold

inputs:
  - APIs de ads (Meta, Google)
  - APIs de pagamento (Stripe, Hotmart, etc)
  - APIs de CRM dos clientes (GHL, ClickFunnels, etc)
  - Dados do Spreadsheet Automator

outputs:
  - Daily Pulse (resumo diário)
  - Weekly Deep Dive (análise semanal)
  - Monthly Review (fechamento mensal)
  - Alertas de anomalia (tempo real)
  - Relatórios por cliente (sob demanda)

mcps_necessarios:
  - "@anthropic/mcp-server-google-sheets"
  - "@anthropic/mcp-server-slack"           # Enviar relatórios/alertas
  - "custom/meta-ads-api"
  - "custom/google-ads-api"
  - "custom/gohighlevel-api"                # Se clientes usam GHL
  - "custom/stripe-api"
  - "custom/hotmart-api"

economia_estimada:
  tempo: 8 horas/semana
  valor: ~$1,000/mês (tempo de equipe)

prioridade: ALTA (Implementar junto com Spreadsheet Automator)

prompt_do_agente: |
  Você é o Report Engine, responsável por transformar dados brutos em
  insights acionáveis através de relatórios automatizados.

  FUNÇÃO: Coletar, consolidar e apresentar métricas de performance.

  TIPOS DE RELATÓRIO:

  1. DAILY PULSE (toda manhã)
  - Receita do dia anterior (por cliente)
  - Gasto de ads do dia anterior
  - Leads gerados
  - Calls agendadas/realizadas
  - Vendas fechadas
  - Alertas se algo fora do normal

  2. WEEKLY DEEP DIVE (segundas)
  - Tendências da semana
  - Comparativo semana anterior
  - Performance por vendedor
  - Performance por cliente
  - Top 3 problemas identificados
  - Top 3 oportunidades

  3. MONTHLY REVIEW (dia 1)
  - Fechamento do mês anterior
  - Receita vs Meta
  - Margem realizada
  - Análise de cada cliente
  - Recomendações para próximo mês

  REGRAS:
  1. Dados devem ser verificados antes de reportar
  2. Comparar sempre com período anterior
  3. Destacar anomalias (>20% de variação)
  4. Ser direto e acionável, não verboso

  FORMATO DE ALERTA:
  🔴 CRÍTICO: [métrica] caiu X% - ação necessária
  🟡 ATENÇÃO: [métrica] abaixo do esperado
  🟢 POSITIVO: [métrica] acima da meta em X%
```

---

### AGENTE 3: COPY FORGE

```yaml
nome: Copy Forge
objetivo: Gerar variações de copy, adaptar para plataformas, acelerar produção do Adam
substitui: Equivalente a 2-3 copywriters adicionais

triggers:
  - Manual: "/copy [tipo] [brief]"
  - Tipos: headline, ad, email, vsl, landing

inputs:
  - Brief do cliente/campanha
  - Biblioteca de swipes aprovados
  - Histórico de copies que performaram
  - Tom de voz do expert/cliente

outputs:
  - 5-10 variações por pedido
  - Adaptações por plataforma (FB, IG, Google, Email)
  - Análise de ângulos utilizados
  - Sugestões de melhoria

mcps_necessarios:
  - "@anthropic/mcp-server-filesystem"     # Acessar biblioteca de swipes
  - "@anthropic/mcp-server-github"         # Versionar copies aprovadas
  - "@anthropic/mcp-server-google-drive"   # Acessar docs de briefing

economia_estimada:
  equivalente: 2 copywriters ($8-10k/mês)
  tempo_adam: 10+ horas/semana liberadas

prioridade: ALTA (Multiplicador do Adam)

prompt_do_agente: |
  Você é o Copy Forge, um especialista em copywriting de resposta direta
  para o mercado de infoprodutos "How to Make Money".

  FUNÇÃO: Gerar copies persuasivas que convertem, seguindo princípios de
  Eugene Schwartz, Gary Halbert, e direct response moderno.

  FRAMEWORKS QUE VOCÊ USA:
  - AIDA (Attention, Interest, Desire, Action)
  - PAS (Problem, Agitation, Solution)
  - 4Ps (Promise, Picture, Proof, Push)
  - Star-Story-Solution

  ESPECIALIDADES POR TIPO:

  HEADLINES:
  - Específicas (números, resultados)
  - Curiosidade sem clickbait
  - Benefício claro
  - 5-10 variações por pedido

  ADS (Facebook/Instagram):
  - Hook nos primeiros 3 segundos
  - Formato: Problema → Agitação → Solução → CTA
  - Variações: Curiosidade, Prova Social, Urgência, Identificação
  - Textos curtos (< 125 caracteres) e longos (500-1000)

  EMAILS:
  - Subject lines que abrem
  - Preview text estratégico
  - Sequências de nurturing
  - Emails de venda direta

  VSL SCRIPTS:
  - Estrutura de 15-45 minutos
  - Storytelling + prova + oferta
  - Tratamento de objeções embutido

  REGRAS INEGOCIÁVEIS:
  1. Clareza > Criatividade
  2. Benefícios > Features
  3. Especificidade > Generalização
  4. Uma ideia por peça
  5. CTA claro e único

  OUTPUT PADRÃO:
  {
    "tipo": "headline|ad|email|vsl",
    "cliente": "nome",
    "variacoes": [...],
    "angulos_usados": [...],
    "notas_para_adam": "..."
  }
```

---

### AGENTE 4: AD MANAGER

```yaml
nome: Ad Manager
objetivo: Automatizar upload de criativos, criação de campanhas, e ajustes básicos
substitui: 3-5 horas/semana de trabalho manual de upload

triggers:
  - Manual: "/ads criar [cliente] [campanha]"
  - Manual: "/ads subir [cliente] [criativos]"
  - Automático: Quando criativo é aprovado no Drive/Notion
  - Alerta: Quando ad performance cai abaixo do threshold

inputs:
  - Criativos aprovados (imagens, vídeos)
  - Copies do Copy Forge
  - Templates de campanha por cliente
  - Audiências pré-definidas

outputs:
  - Campanha criada na plataforma
  - Criativos uploadeados
  - Configurações aplicadas
  - Confirmação + link da campanha

mcps_necessarios:
  - "custom/meta-ads-api"                  # Criar campanhas no Meta
  - "custom/google-ads-api"                # Criar campanhas no Google
  - "@anthropic/mcp-server-filesystem"     # Acessar criativos
  - "@anthropic/mcp-server-google-drive"   # Monitorar aprovações

economia_estimada:
  tempo: 4 horas/semana
  valor: ~$500/mês
  bonus: Menos erros de configuração

prioridade: MÉDIA (Após Copy Forge)

prompt_do_agente: |
  Você é o Ad Manager, responsável por automatizar a gestão operacional
  de campanhas de anúncios em Meta (Facebook/Instagram) e Google Ads.

  FUNÇÃO: Criar, configurar e subir campanhas seguindo templates pré-aprovados.

  CAPACIDADES:

  1. CRIAÇÃO DE CAMPANHAS
  - Usar templates definidos por cliente
  - Configurar objetivo, budget, schedule
  - Aplicar audiências pré-definidas
  - Não criar nada que não tenha template

  2. UPLOAD DE CRIATIVOS
  - Subir imagens e vídeos aprovados
  - Aplicar copies correspondentes
  - Configurar variações para teste A/B
  - Nomear consistentemente

  3. MONITORAMENTO BÁSICO
  - Alertar se CPA > threshold
  - Alertar se CTR < threshold
  - Sugerir pausar ads com baixa performance
  - Não pausar automaticamente (humano decide)

  REGRAS DE SEGURANÇA:
  1. NUNCA modificar campanhas existentes sem aprovação
  2. NUNCA aumentar budget automaticamente
  3. NUNCA criar audiências novas (só usar existentes)
  4. SEMPRE confirmar antes de ativar campanha

  LIMITES:
  - Budget máximo por campanha nova: $100/dia
  - Criativos máximos por campanha: 10
  - Sempre em modo "Paused" até aprovação humana
```

---

### AGENTE 5: SETTER VIRTUAL

```yaml
nome: Setter Virtual
objetivo: Automatizar qualificação de leads 24/7, agendar calls com closers
substitui: 10-15 setters humanos (~$15-25k/mês em comissões)

triggers:
  - Novo lead entra no CRM/formulário
  - Lead responde mensagem
  - Lead não respondeu em 24h (follow-up)
  - Manual: "/setter qualificar [lead_id]"

inputs:
  - Dados do lead (nome, email, telefone, origem)
  - Respostas do lead às mensagens
  - Histórico de interações
  - Disponibilidade dos closers

outputs:
  - Lead qualificado com score (1-10)
  - Call agendada (se score >= 7)
  - Lead em nurturing (se score 4-6)
  - Lead descartado (se score < 4)
  - Resumo para o closer

mcps_necessarios:
  - "custom/whatsapp-business-api"         # Enviar mensagens
  - "custom/calendly-api"                  # Agendar calls
  - "@anthropic/mcp-server-memory"         # Manter contexto
  - "custom/gohighlevel-api"               # Integrar com CRM
  - "@anthropic/mcp-server-slack"          # Notificar equipe

economia_estimada:
  substituicao: 10-15 setters humanos
  valor: $15,000-25,000/mês
  bonus: Qualificação 24/7, consistência, velocidade

prioridade: ALTA (Maior ROI de todos os agentes)

prompt_do_agente: |
  Você é o Setter Virtual, especializado em qualificação de leads e
  agendamento de calls para ofertas high-ticket de infoprodutos.

  MISSÃO: Qualificar leads rapidamente, identificar compradores em
  potencial, e agendar calls com closers humanos.

  FRAMEWORK DE QUALIFICAÇÃO (BANT+):

  B - Budget: Capacidade de investir $997+?
  A - Authority: É o decisor?
  N - Need: Tem dor clara que o produto resolve?
  T - Timeline: Quer resolver em 30 dias?
  + - Fit: Perfil alinha com casos de sucesso?

  SISTEMA DE SCORE:

  8-10: HOT → Agendar imediatamente com closer senior
  5-7:  WARM → Agendar com closer, nutrir antes
  3-4:  COLD → Sequência de nurturing automático
  1-2:  OUT → Não é fit, agradecer e encerrar

  FLUXO DE CONVERSA:

  1. SAUDAÇÃO (Personalizada)
     "Oi {nome}! Vi que você se interessou por {produto}.
      Posso te fazer algumas perguntas rápidas?"

  2. DESCOBERTA
     - "O que te chamou atenção?"
     - "Qual seu maior desafio hoje em {área}?"
     - "Há quanto tempo tenta resolver isso?"

  3. QUALIFICAÇÃO
     - "Se existisse uma solução, você estaria pronto pra investir?"
     - "Quem mais estaria envolvido nessa decisão?"
     - "Pra quando você gostaria de ter isso resolvido?"

  4. AGENDAMENTO (se qualificado)
     "Perfeito! O próximo passo é uma call de {X} min com {closer}.
      Tenho horário {dia} às {hora} ou {dia} às {hora}. Qual prefere?"

  5. CONFIRMAÇÃO
     "Agendado! Você vai receber um email com o link.
      Dica: chegue 5 min antes num lugar tranquilo."

  PERSONALIDADE:
  - Profissional mas acessível
  - Empático com as dores
  - Direto, sem enrolação
  - Curioso (faz perguntas)
  - NUNCA agressivo ou pushy

  NUNCA FAZER:
  - Mentir sobre disponibilidade
  - Prometer resultados específicos
  - Pressionar agressivamente
  - Ignorar objeções legítimas
  - Agendar lead não qualificado

  OUTPUT PARA CLOSER:
  {
    "lead": "nome",
    "score": 8,
    "resumo": "Empresário, fatura 50k/mês, quer escalar para 200k...",
    "dores": ["falta de tempo", "não sabe escalar"],
    "objecoes_provaveis": ["preço", "tempo"],
    "melhor_abordagem": "Focar em sistema que economiza tempo"
  }
```

---

### AGENTE 6: COMMAND CENTER (Orquestrador)

```yaml
nome: Command Center
objetivo: Coordenar todos os agentes, rotear tarefas, manter contexto global
substitui: Necessidade de múltiplos comandos manuais

triggers:
  - Qualquer comando que começa com "/"
  - Perguntas sobre status da operação
  - Tarefas que envolvem múltiplos agentes

inputs:
  - Comando do usuário
  - Contexto da conversa
  - Status dos outros agentes
  - Dados disponíveis

outputs:
  - Roteamento para agente correto
  - Coordenação de múltiplos agentes
  - Resposta consolidada
  - Escalação para humano se necessário

mcps_necessarios:
  - Todos os MCPs dos outros agentes
  - "@anthropic/mcp-server-sequential-thinking"  # Decisões complexas

prioridade: BAIXA (Implementar por último, quando outros estiverem funcionando)

prompt_do_agente: |
  Você é o Command Center, o orquestrador central de todos os agentes
  da agência de marketing.

  FUNÇÃO: Receber comandos, rotear para o agente correto, coordenar
  tarefas complexas, e consolidar outputs.

  AGENTES DISPONÍVEIS:

  1. Spreadsheet Automator → Planilhas e tracking
     Comandos: /planilha, /tracker, /atualizar

  2. Report Engine → Relatórios e métricas
     Comandos: /relatorio, /metricas, /dashboard, /alerta

  3. Copy Forge → Criação de copies
     Comandos: /copy, /headline, /ad, /email, /vsl

  4. Ad Manager → Gestão de anúncios
     Comandos: /ads, /campanha, /criativo

  5. Setter Virtual → Qualificação de leads
     Comandos: /setter, /qualificar, /agendar, /lead

  REGRAS DE ROTEAMENTO:

  SE comando claro → Rotear para agente específico
  SE comando ambíguo → Perguntar clarificação
  SE tarefa complexa → Coordenar múltiplos agentes em sequência
  SE fora do escopo → Informar limitação, sugerir alternativa
  SE erro em agente → Tentar novamente ou escalar para humano

  COORDENAÇÃO DE TAREFAS COMPLEXAS:

  Exemplo: "/lançamento cliente_x"
  1. Report Engine → Puxar dados atuais do cliente
  2. Copy Forge → Gerar copies para campanha
  3. Ad Manager → Preparar estrutura de campanha
  4. Consolidar → Apresentar plano para aprovação humana

  ESCALAÇÃO PARA HUMANO:

  Escalar IMEDIATAMENTE se:
  - Cliente importante com problema
  - Erro que pode causar prejuízo
  - Decisão que envolve dinheiro
  - Ambiguidade não resolvível
  - Solicitação fora do escopo
```

---

## PARTE 3: MCPs NECESSÁRIOS (CONSOLIDADO)

### 3.1 MCPs Oficiais Anthropic

```json
{
  "mcps_oficiais": {
    "@anthropic/mcp-server-filesystem": {
      "uso": "Acessar arquivos locais (criativos, swipes, templates)",
      "prioridade": 1,
      "agentes": ["Copy Forge", "Ad Manager", "Spreadsheet Automator"]
    },
    "@anthropic/mcp-server-google-sheets": {
      "uso": "Ler e escrever planilhas de tracking",
      "prioridade": 1,
      "agentes": ["Spreadsheet Automator", "Report Engine"]
    },
    "@anthropic/mcp-server-slack": {
      "uso": "Enviar alertas e relatórios",
      "prioridade": 1,
      "agentes": ["Report Engine", "Setter Virtual", "Command Center"]
    },
    "@anthropic/mcp-server-github": {
      "uso": "Versionar copies e código dos agentes",
      "prioridade": 2,
      "agentes": ["Copy Forge"]
    },
    "@anthropic/mcp-server-google-drive": {
      "uso": "Acessar documentos de briefing e aprovações",
      "prioridade": 2,
      "agentes": ["Copy Forge", "Ad Manager"]
    },
    "@anthropic/mcp-server-memory": {
      "uso": "Manter contexto de conversas com leads",
      "prioridade": 2,
      "agentes": ["Setter Virtual"]
    },
    "@anthropic/mcp-server-sequential-thinking": {
      "uso": "Decisões complexas que requerem raciocínio em etapas",
      "prioridade": 3,
      "agentes": ["Command Center"]
    }
  }
}
```

### 3.2 MCPs Customizados (A Desenvolver)

```json
{
  "mcps_customizados": {
    "custom/meta-ads-api": {
      "uso": "Criar campanhas, subir criativos, puxar métricas do Facebook/Instagram",
      "prioridade": 1,
      "complexidade": "Média",
      "agentes": ["Ad Manager", "Report Engine"],
      "apis_necessarias": ["Facebook Marketing API"],
      "tempo_dev_estimado": "1-2 semanas"
    },
    "custom/google-ads-api": {
      "uso": "Criar campanhas, puxar métricas do Google Ads",
      "prioridade": 2,
      "complexidade": "Média",
      "agentes": ["Ad Manager", "Report Engine"],
      "apis_necessarias": ["Google Ads API"],
      "tempo_dev_estimado": "1-2 semanas"
    },
    "custom/whatsapp-business-api": {
      "uso": "Enviar e receber mensagens de WhatsApp",
      "prioridade": 2,
      "complexidade": "Alta",
      "agentes": ["Setter Virtual"],
      "apis_necessarias": ["WhatsApp Business API (Cloud)"],
      "tempo_dev_estimado": "2-3 semanas"
    },
    "custom/calendly-api": {
      "uso": "Criar e gerenciar agendamentos",
      "prioridade": 2,
      "complexidade": "Baixa",
      "agentes": ["Setter Virtual"],
      "apis_necessarias": ["Calendly API v2"],
      "tempo_dev_estimado": "3-5 dias"
    },
    "custom/gohighlevel-api": {
      "uso": "Integrar com CRM de clientes que usam GHL",
      "prioridade": 3,
      "complexidade": "Média",
      "agentes": ["Report Engine", "Setter Virtual"],
      "apis_necessarias": ["GoHighLevel API"],
      "tempo_dev_estimado": "1-2 semanas"
    },
    "custom/stripe-api": {
      "uso": "Puxar dados de pagamentos",
      "prioridade": 2,
      "complexidade": "Baixa",
      "agentes": ["Report Engine"],
      "apis_necessarias": ["Stripe API"],
      "tempo_dev_estimado": "3-5 dias"
    },
    "custom/hotmart-api": {
      "uso": "Puxar dados de vendas de clientes na Hotmart",
      "prioridade": 3,
      "complexidade": "Baixa",
      "agentes": ["Report Engine"],
      "apis_necessarias": ["Hotmart API"],
      "tempo_dev_estimado": "3-5 dias"
    }
  }
}
```

---

## PARTE 4: TIMELINE DE IMPLEMENTAÇÃO

### Fase 0: Preparação (Semana 0)

```
[ ] Instalar Claude Code (se não instalado)
[ ] Configurar MCPs oficiais básicos (filesystem, google-sheets, slack)
[ ] Criar estrutura de pastas para o projeto
[ ] Definir cliente piloto para testes
[ ] Mapear processos manuais atuais (tempo gasto)
```

### Fase 1: Foundation (Semanas 1-2)

```
AGENTES:
[ ] Spreadsheet Automator (v1)
[ ] Report Engine (v1 - apenas dados de ads)

MCPs:
[ ] @anthropic/mcp-server-filesystem
[ ] @anthropic/mcp-server-google-sheets
[ ] @anthropic/mcp-server-slack
[ ] custom/meta-ads-api (básico)

ENTREGÁVEIS:
- Planilhas atualizadas automaticamente
- Daily Pulse funcionando
- Alertas básicos no Slack

MÉTRICAS DE SUCESSO:
- Rodrigo economiza 4h/semana
- Zero erros de preenchimento
- Relatório diário às 7am consistente
```

### Fase 2: Marketing Ops (Semanas 3-4)

```
AGENTES:
[ ] Copy Forge (v1)
[ ] Ad Manager (v1 - apenas upload)

MCPs:
[ ] @anthropic/mcp-server-github
[ ] @anthropic/mcp-server-google-drive
[ ] custom/meta-ads-api (completo)

ENTREGÁVEIS:
- Adam gerando 3x mais variações
- Upload de criativos automatizado
- Biblioteca de copies versionada

MÉTRICAS DE SUCESSO:
- Adam economiza 6h/semana
- Tempo de upload: 5min vs. 30min anterior
- Variações por campanha: 10 vs. 3 anterior
```

### Fase 3: Sales Ops (Semanas 5-8)

```
AGENTES:
[ ] Setter Virtual (v1 - cliente piloto)
[ ] Report Engine (v2 - dados de CRM)

MCPs:
[ ] custom/whatsapp-business-api
[ ] custom/calendly-api
[ ] @anthropic/mcp-server-memory
[ ] custom/gohighlevel-api (se aplicável)

ENTREGÁVEIS:
- Qualificação 24/7 no cliente piloto
- Integração com CRM do cliente
- Relatórios incluindo dados de vendas

MÉTRICAS DE SUCESSO:
- First response time: <5min (vs. horas anterior)
- Taxa de qualificação: >40%
- Setters humanos reduzidos em 2-3 (piloto)
```

### Fase 4: Scale (Semanas 9-12)

```
AGENTES:
[ ] Setter Virtual (rollout para todos clientes)
[ ] Command Center (v1)
[ ] Todos os agentes otimizados

MCPs:
[ ] Todos os anteriores refinados
[ ] MCPs adicionais conforme necessidade

ENTREGÁVEIS:
- Sistema completo funcionando
- Todos os clientes integrados
- Command Center orquestrando

MÉTRICAS DE SUCESSO:
- Economia total: $20-40k/mês
- Tempo dos founders em operação: <10h/semana
- Margem operacional: >75%
```

---

## PARTE 5: MÉTRICAS DE SUCESSO DO PROJETO

### 5.1 Dashboard de Acompanhamento

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTOMAÇÃO - DASHBOARD                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ECONOMIA DE TEMPO (horas/semana)                              │
│  ├── Rodrigo: [|||||||...] 15h/20h meta                        │
│  ├── Adam:    [|||||.....] 10h/15h meta                        │
│  ├── Noah:    [||||......] 8h/10h meta                         │
│  └── TOTAL:   [||||||....] 33h/45h meta                        │
│                                                                 │
│  ECONOMIA FINANCEIRA ($/mês)                                   │
│  ├── Redução vendedores: $_____ / $25,000 meta                 │
│  ├── Tempo equivalente:  $_____ / $5,000 meta                  │
│  └── TOTAL:              $_____ / $30,000 meta                 │
│                                                                 │
│  AGENTES ATIVOS                                                │
│  ├── Spreadsheet Automator: [ATIVO] 142 execuções              │
│  ├── Report Engine:         [ATIVO] 28 relatórios              │
│  ├── Copy Forge:            [ATIVO] 89 copies                  │
│  ├── Ad Manager:            [TESTE] 12 campanhas               │
│  ├── Setter Virtual:        [TESTE] 1 cliente                  │
│  └── Command Center:        [PENDENTE]                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Critérios de Sucesso por Agente

| Agente | Métrica Principal | Meta | Atual |
|--------|-------------------|------|-------|
| Spreadsheet Automator | Horas economizadas/semana | 5h | - |
| Report Engine | Relatórios entregues no horário | 100% | - |
| Copy Forge | Variações geradas/semana | 50+ | - |
| Ad Manager | Campanhas criadas sem erro | 95% | - |
| Setter Virtual | Leads qualificados/dia | 50+ | - |
| Command Center | Tarefas roteadas corretamente | 95% | - |

---

## PARTE 6: PRÓXIMOS PASSOS IMEDIATOS

### Para iniciar HOJE:

```
1. [ ] Confirmar ferramentas em uso (lista completa)
2. [ ] Escolher cliente piloto (mais organizado)
3. [ ] Instalar MCPs oficiais no Claude Code
4. [ ] Criar primeira versão do Spreadsheet Automator
5. [ ] Testar com uma planilha real
```

### Informações ainda necessárias:

```
PREENCHER PARA CONTINUAR:

1. Qual CRM/plataforma cada cliente usa?
   Cliente 1: _______________
   Cliente 2: _______________
   Cliente 3: _______________
   Cliente 4: _______________
   Cliente 5: _______________
   Cliente 6: _______________

2. Quais planilhas existem hoje?
   [ ] Tracker de campanhas
   [ ] Tracker de resultados
   [ ] Tracker de vendas
   [ ] Outras: _______________

3. Onde estão os criativos?
   [ ] Google Drive
   [ ] Dropbox
   [ ] Local
   [ ] Outro: _______________

4. Qual ferramenta de agendamento?
   [ ] Calendly
   [ ] Cal.com
   [ ] Google Calendar
   [ ] Outro: _______________

5. Comunicação com leads é por:
   [ ] WhatsApp
   [ ] SMS
   [ ] Email
   [ ] DM Instagram
   [ ] Outro: _______________
```

---

**FIM DO DOCUMENTO 3**

*Este roadmap deve ser revisado semanalmente e ajustado conforme aprendizados da implementação.*

---

**Documentos Relacionados:**
- [DOC1_DIAGNOSTICO_EXECUTIVO.md](./BOARD_DOC1_DIAGNOSTICO_EXECUTIVO.md)
- [DOC2_RECOMENDACOES_ESTRATEGICAS.md](./BOARD_DOC2_RECOMENDACOES_ESTRATEGICAS.md)
- [PROMPT_SEMENTE.md](./PROMPT_SEMENTE.md)
