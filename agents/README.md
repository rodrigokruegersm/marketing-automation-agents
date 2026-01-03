# Agents - Os Tentaculos do Sistema

Esta pasta contem os **agentes de IA** - modulos plugaveis que executam
tarefas especificas usando o Core do sistema.

---

## Conceito

Cada agente e como um "tentaculo" que pode ser:
- **Plugado** - Adicionar novas funcionalidades
- **Removido** - Desativar funcionalidades nao usadas
- **Substituido** - Trocar por versoes melhores

---

## Agentes Disponiveis

| Agente | Pasta | Funcao |
|--------|-------|--------|
| Traffic Agent | `traffic/` | Analisa campanhas de anuncios |
| Creative Agent | `creative_lab/` | Gera imagens com IA |
| Video Agent | `video_editor/` | Cria videos com voz e avatar |
| Copy Agent | `copy_forge/` | Gera textos persuasivos |
| Performance Agent | `performance_optimizer/` | Otimiza automaticamente |
| Audience Agent | `audience_builder/` | Constroi audiencias |

---

## Estrutura de um Agente

Cada agente segue esta estrutura:

```
agents/meu_agente/
├── __init__.py          # Exporta o agente
├── agent.py             # Logica principal
├── prompts/             # Prompts de IA (opcional)
└── templates/           # Templates (opcional)
```

---

## Base Agent

Todos os agentes herdam de `BaseAgent`:

```python
# agents/base.py

class BaseAgent:
    """Classe base para todos os agentes"""

    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config

    def analyze(self, data: dict) -> dict:
        """Analisa dados e retorna insights"""
        raise NotImplementedError

    def execute(self, action: str, params: dict) -> dict:
        """Executa uma acao"""
        raise NotImplementedError

    def get_recommendations(self) -> list:
        """Retorna lista de recomendacoes"""
        raise NotImplementedError
```

---

## Como Criar um Novo Agente

### 1. Criar a pasta

```bash
mkdir agents/meu_agente
touch agents/meu_agente/__init__.py
touch agents/meu_agente/agent.py
```

### 2. Implementar o agente

```python
# agents/meu_agente/agent.py

from agents.base import BaseAgent

class MeuAgente(BaseAgent):
    def __init__(self, config: dict = None):
        super().__init__(name="Meu Agente", config=config or {})

    def analyze(self, data: dict) -> dict:
        # Sua logica de analise aqui
        return {"status": "ok", "insights": [...]}

    def execute(self, action: str, params: dict) -> dict:
        # Sua logica de execucao aqui
        return {"success": True}

    def get_recommendations(self) -> list:
        return [
            {"tipo": "otimizacao", "mensagem": "Faca isso..."}
        ]
```

### 3. Exportar o agente

```python
# agents/meu_agente/__init__.py

from .agent import MeuAgente

__all__ = ['MeuAgente']
```

### 4. Registrar no init principal

```python
# agents/__init__.py

from .meu_agente import MeuAgente
```

### 5. Adicionar ao Dashboard (opcional)

Edite `dashboard/app.py` para adicionar a interface do agente.

---

## Thresholds do Traffic Agent (Jeremy Haines)

O Traffic Agent usa thresholds baseados no metodo Jeremy Haines:

| Metrica | Kill | Watch | Scale |
|---------|------|-------|-------|
| ROAS | < 1.0x | 1.0-1.5x | > 2.0x |
| CTR | < 0.8% | 0.8-1.5% | > 1.5% |
| Frequencia | > 3.5 | 2.5-3.5 | < 2.5 |

---

## Proximos Agentes Planejados

- [ ] **Scheduler Agent** - Agenda acoes automaticas
- [ ] **Report Agent** - Gera relatorios automaticos
- [ ] **Alert Agent** - Envia alertas em tempo real
- [ ] **AB Test Agent** - Gerencia testes A/B

---

**Dica:** Mantenha cada agente focado em UMA tarefa especifica.
Agentes menores e mais focados sao mais faceis de manter e testar.
