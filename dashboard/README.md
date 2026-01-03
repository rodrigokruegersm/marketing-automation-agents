# Dashboard - A Interface do Usuario

Esta pasta contem o **dashboard visual** construido com Streamlit.
E a "cara" do sistema que o usuario interage.

---

## Arquivos

| Arquivo | O que faz |
|---------|-----------|
| `app.py` | Aplicacao principal (toda a UI) |
| `auth.py` | Sistema de autenticacao/login |
| `components/` | Componentes reutilizaveis |

---

## Como Executar

### Localmente

```bash
cd /caminho/para/projeto
streamlit run dashboard/app.py
```

Acesse: http://localhost:8501

### Na Nuvem (Streamlit Cloud)

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Conecte seu repositorio GitHub
3. Configure o caminho: `dashboard/app.py`
4. Adicione os secrets (API keys)
5. Deploy!

---

## Estrutura do app.py

O arquivo `app.py` esta organizado em secoes:

```python
# 1. IMPORTS E CONFIG
import streamlit as st
...

# 2. ESTILOS CSS
st.markdown("""<style>...</style>""")

# 3. SESSION STATE
if 'variavel' not in st.session_state:
    st.session_state.variavel = valor

# 4. CONFIGURACAO DE PROJETOS
PROJECTS = {...}

# 5. FUNCOES DE API
@st.cache_data
def fetch_data():
    ...

# 6. SIDEBAR (Menu lateral)
with st.sidebar:
    ...

# 7. PAGINAS
if st.session_state.current_page == 'dashboard':
    ...
elif st.session_state.current_page == 'traffic':
    ...
```

---

## Paginas Disponiveis

| Pagina | Icone | Descricao |
|--------|-------|-----------|
| Dashboard | Hone | KPIs principais, funil de conversao |
| Traffic Agent | Chart | Analise de campanhas, AI Analysis |
| Design Agent | Art | Geracao de imagens |
| Video Editor | Film | Criacao de videos |
| Copywriter | Pencil | Geracao de textos |
| Settings | Gear | Configuracoes |

---

## Sistema de Autenticacao

O `auth.py` implementa login simples com senha:

```python
# Senha definida em:
# 1. Streamlit Secrets (producao)
# 2. Variavel de ambiente DASHBOARD_PASSWORD
# 3. Fallback: "adlytics2026"
```

Para alterar a senha:
1. Acesse Streamlit Cloud → Settings → Secrets
2. Edite `DASHBOARD_PASSWORD = "nova_senha"`

---

## Filtros Disponiveis

### Filtro de Data
- Presets: Hoje, Ontem, 3/7/14/30 dias
- Personalizado: Data inicial e final

### Filtro de Tag
- Digite qualquer tag: `[bsb]`, `[promo]`
- Filtra campanhas que contem a tag no nome
- Botoes rapidos para tags frequentes

### Filtro de Projeto
- Alterna entre diferentes projetos/clientes
- Cada projeto tem suas proprias tags default

---

## Componentes Reutilizaveis

A pasta `components/` contem componentes que podem ser
reutilizados em diferentes partes do dashboard:

```python
# Exemplo de uso
from dashboard.components.metrics_cards import render_kpi_card

render_kpi_card(
    label="Faturamento",
    value="$10,000",
    color="green"
)
```

---

## Customizacao Visual

Os estilos CSS estao no inicio de `app.py`:

```css
/* Cores principais */
--bg-primary: #0F172A;     /* Fundo escuro */
--bg-secondary: #1E293B;   /* Cards */
--accent: #0066FF;         /* Azul Adlytics */
--text-primary: #F8FAFC;   /* Texto branco */
--text-secondary: #94A3B8; /* Texto cinza */
--success: #10B981;        /* Verde */
--warning: #F59E0B;        /* Amarelo */
--danger: #EF4444;         /* Vermelho */
```

---

## Cache de Dados

O dashboard usa cache para melhorar performance:

```python
@st.cache_data(ttl=120)  # Cache por 2 minutos
def fetch_campaigns():
    ...
```

Para limpar o cache:
- Clique no botao "Atualizar"
- Ou use `st.cache_data.clear()`

---

## Adicionando Nova Pagina

1. Adicione entrada no menu (SIDEBAR):
```python
pages = [
    ...,
    ('nova_pagina', 'Emoji', 'Nome da Pagina'),
]
```

2. Crie a secao da pagina:
```python
elif st.session_state.current_page == 'nova_pagina':
    st.markdown("## Nova Pagina")
    # Seu codigo aqui
```

---

**Dica:** Use `st.rerun()` para forcar atualizacao da pagina
apos acoes que mudam o estado.
