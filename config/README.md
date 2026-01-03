# Config - Configuracoes do Sistema

Esta pasta contem arquivos de configuracao que controlam
o comportamento do Adlytics.

---

## Arquivos

| Arquivo | O que configura |
|---------|-----------------|
| `settings.yaml` | Configuracoes gerais do sistema |
| `thresholds.yaml` | Limites de performance (metodo Jeremy Haines) |

---

## settings.yaml

Configuracoes principais:

```yaml
# Ambiente
app:
  environment: "production"

# Cache do dashboard
dashboard:
  cache_ttl: 120  # segundos

# Configuracao de APIs
api:
  timeout: 30
  max_retries: 3
```

---

## thresholds.yaml

Define quando uma campanha deve ser pausada, monitorada ou escalada:

### ROAS
| Acao | Valor |
|------|-------|
| Kill (pausar) | < 1.0x |
| Watch (monitorar) | 1.0 - 1.5x |
| Scale (escalar) | > 2.0x |

### Frequencia
| Status | Valor |
|--------|-------|
| OK | < 2.5 |
| Warning | 2.5 - 3.5 |
| Critical | > 3.5 |

### CTR
| Status | Valor |
|--------|-------|
| Fraco | < 0.8% |
| Normal | 0.8 - 1.5% |
| Bom | > 1.5% |

---

## Variaves de Ambiente

Alem dos arquivos YAML, algumas configuracoes vem de variaveis:

```bash
# .env ou Streamlit Secrets

DASHBOARD_PASSWORD=sua_senha
META_ACCESS_TOKEN=seu_token
META_AD_ACCOUNT_ID=act_xxxxx
WHOP_API_KEY=sua_chave
HYROS_API_KEY=sua_chave
LEONARDO_API_KEY=sua_chave
ELEVENLABS_API_KEY=sua_chave
HEYGEN_API_KEY=sua_chave
```

---

## Personalizando Thresholds

Voce pode ajustar os thresholds baseado no seu negocio:

1. Abra `thresholds.yaml`
2. Ajuste os valores conforme sua realidade
3. Reinicie o dashboard

**Exemplo:** Se seu CPA target e $50, ajuste:

```yaml
cpa:
  target: 50
  max: 75  # 1.5x do target
```

---

## Boas Praticas

- Nunca commite API keys nos arquivos YAML
- Use `.env` ou Streamlit Secrets para credenciais
- Mantenha um `.env.example` com as variaveis necessarias
- Documente alteracoes nos thresholds

---

**Dica:** Os thresholds sao baseados no metodo Jeremy Haines,
mas ajuste conforme sua experiencia e nicho de mercado.
