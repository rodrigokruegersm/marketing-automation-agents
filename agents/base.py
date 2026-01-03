"""
Base Agent Class
Foundation for all marketing automation AI agents
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_INPUT = "waiting_input"


@dataclass
class AgentConfig:
    """Configuration for an agent"""
    name: str
    description: str
    version: str = "1.0.0"
    enabled: bool = True

    # LLM configuration
    model: str = "claude-3-opus"  # or gpt-4, etc.
    temperature: float = 0.7
    max_tokens: int = 4096

    # Execution settings
    max_retries: int = 3
    timeout_seconds: int = 300

    # Custom settings
    settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result from agent execution"""
    success: bool
    data: Any
    message: str = ""
    execution_time: float = 0.0
    tokens_used: int = 0
    cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            'success': self.success,
            'data': self.data,
            'message': self.message,
            'execution_time': self.execution_time,
            'tokens_used': self.tokens_used,
            'cost': self.cost,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }


class BaseAgent(ABC):
    """
    Base class for all marketing automation agents.

    Agents are specialized AI modules that perform specific tasks:
    - CopyForge: Generate ad copy and headlines
    - CreativeLab: Generate creative concepts and variations
    - AudienceBuilder: Build and optimize audiences
    - PerformanceOptimizer: Analyze and optimize campaign performance

    Usage:
        class MyAgent(BaseAgent):
            def execute(self, context):
                # Agent logic here
                return AgentResult(success=True, data=result)

        agent = MyAgent(config)
        result = agent.run(context)
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or self._default_config()
        self.status = AgentStatus.IDLE
        self.last_result: Optional[AgentResult] = None
        self.execution_history: List[AgentResult] = []

    @abstractmethod
    def _default_config(self) -> AgentConfig:
        """Return default configuration for this agent"""
        pass

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Execute the agent's main task.

        Args:
            context: Dictionary with input data and parameters

        Returns:
            AgentResult with execution results
        """
        pass

    def run(self, context: Dict[str, Any]) -> AgentResult:
        """
        Run the agent with error handling and logging.

        Args:
            context: Dictionary with input data and parameters

        Returns:
            AgentResult with execution results
        """
        if not self.config.enabled:
            return AgentResult(
                success=False,
                data=None,
                message=f"Agent {self.config.name} is disabled"
            )

        self.status = AgentStatus.RUNNING
        start_time = datetime.now()

        try:
            result = self.execute(context)
            result.execution_time = (datetime.now() - start_time).total_seconds()
            self.status = AgentStatus.COMPLETED

        except Exception as e:
            result = AgentResult(
                success=False,
                data=None,
                message=f"Agent execution failed: {str(e)}",
                execution_time=(datetime.now() - start_time).total_seconds()
            )
            self.status = AgentStatus.FAILED

        self.last_result = result
        self.execution_history.append(result)

        return result

    def validate_context(self, context: Dict[str, Any], required_keys: List[str]) -> bool:
        """Validate that context contains required keys"""
        missing = [k for k in required_keys if k not in context]
        if missing:
            raise ValueError(f"Missing required context keys: {missing}")
        return True

    def get_stats(self) -> Dict:
        """Get agent execution statistics"""
        if not self.execution_history:
            return {'total_runs': 0}

        successful = [r for r in self.execution_history if r.success]

        return {
            'total_runs': len(self.execution_history),
            'successful_runs': len(successful),
            'failed_runs': len(self.execution_history) - len(successful),
            'success_rate': len(successful) / len(self.execution_history) * 100,
            'total_tokens': sum(r.tokens_used for r in self.execution_history),
            'total_cost': sum(r.cost for r in self.execution_history),
            'avg_execution_time': sum(r.execution_time for r in self.execution_history) / len(self.execution_history)
        }
