"""
PerformanceOptimizer Agent
Analyzes campaign performance and suggests optimizations
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ..base import BaseAgent, AgentConfig, AgentResult


@dataclass
class OptimizationAction:
    """Recommended optimization action"""
    priority: str  # critical, high, medium, low
    action_type: str  # pause, scale, adjust, test
    target: str  # campaign, adset, ad
    target_id: str
    target_name: str
    reason: str
    expected_impact: str
    risk_level: str


class PerformanceOptimizerAgent(BaseAgent):
    """
    AI Agent for campaign performance optimization.

    Capabilities:
    - Analyze campaign, adset, and ad performance
    - Identify underperformers to pause
    - Find scaling opportunities
    - Suggest budget reallocation
    - Predict performance trends
    - Generate daily optimization reports

    Usage:
        agent = PerformanceOptimizerAgent()
        result = agent.run({
            'action': 'analyze',
            'campaigns': campaigns_data,
            'thresholds': {
                'roas_min': 2.0,
                'cpp_max': 25
            }
        })
    """

    def _default_config(self) -> AgentConfig:
        return AgentConfig(
            name="PerformanceOptimizer",
            description="AI-powered campaign performance optimization",
            version="1.0.0",
            model="claude-3-opus",
            temperature=0.3,  # Low for analytical precision
            settings={
                'default_thresholds': {
                    'roas_min': 2.0,
                    'roas_excellent': 3.0,
                    'cpp_max': 25,
                    'cpp_excellent': 12,
                    'frequency_max': 3.0,
                    'ctr_min': 1.0
                }
            }
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Execute performance optimization analysis.

        Args:
            context: Dictionary with:
                - action: analyze, optimize, report
                - campaigns: Campaign data
                - thresholds: Performance thresholds

        Returns:
            AgentResult with optimization recommendations
        """
        action = context.get('action', 'analyze')

        if action == 'analyze':
            return self._analyze_performance(context)
        elif action == 'get_actions':
            return self._get_optimization_actions(context)
        elif action == 'budget_reallocation':
            return self._suggest_budget_reallocation(context)
        elif action == 'daily_report':
            return self._generate_daily_report(context)
        else:
            return AgentResult(
                success=False,
                data=None,
                message=f"Unknown action: {action}"
            )

    def _analyze_performance(self, context: Dict[str, Any]) -> AgentResult:
        """Analyze overall performance"""
        campaigns = context.get('campaigns', [])
        thresholds = context.get('thresholds', self.config.settings['default_thresholds'])

        analysis = {
            'total_campaigns': len(campaigns),
            'active_campaigns': 0,
            'paused_campaigns': 0,
            'critical_issues': [],
            'opportunities': [],
            'overall_health': 'healthy'
        }

        for campaign in campaigns:
            status = campaign.get('effective_status', campaign.get('status', 'UNKNOWN'))
            if status == 'ACTIVE':
                analysis['active_campaigns'] += 1
            else:
                analysis['paused_campaigns'] += 1

            # Analyze metrics
            insights = campaign.get('insights', {}).get('data', [{}])[0] if campaign.get('insights') else {}

            if insights:
                spend = float(insights.get('spend', 0))
                roas_data = insights.get('purchase_roas', [{}])
                roas = float(roas_data[0].get('value', 0)) if roas_data else 0

                if spend > 50 and roas < thresholds['roas_min']:
                    analysis['critical_issues'].append({
                        'campaign': campaign.get('name', 'Unknown'),
                        'issue': f"Low ROAS: {roas:.2f}x (min: {thresholds['roas_min']}x)",
                        'action': 'Review and potentially pause'
                    })

                if roas >= thresholds.get('roas_excellent', 3.0):
                    analysis['opportunities'].append({
                        'campaign': campaign.get('name', 'Unknown'),
                        'opportunity': f"High ROAS: {roas:.2f}x - Scale opportunity",
                        'action': 'Increase budget by 20-30%'
                    })

        # Determine overall health
        if analysis['critical_issues']:
            analysis['overall_health'] = 'critical' if len(analysis['critical_issues']) > 2 else 'warning'

        return AgentResult(
            success=True,
            data=analysis,
            message=f"Analyzed {len(campaigns)} campaigns"
        )

    def _get_optimization_actions(self, context: Dict[str, Any]) -> AgentResult:
        """Get specific optimization actions"""
        campaigns = context.get('campaigns', [])
        thresholds = context.get('thresholds', self.config.settings['default_thresholds'])

        actions = []

        for campaign in campaigns:
            insights = campaign.get('insights', {}).get('data', [{}])[0] if campaign.get('insights') else {}

            if not insights:
                continue

            spend = float(insights.get('spend', 0))
            roas_data = insights.get('purchase_roas', [{}])
            roas = float(roas_data[0].get('value', 0)) if roas_data else 0

            # Pause recommendations
            if spend > 100 and roas < 1.0:
                actions.append({
                    'priority': 'critical',
                    'action_type': 'pause',
                    'target': 'campaign',
                    'target_id': campaign.get('id'),
                    'target_name': campaign.get('name'),
                    'reason': f'Negative ROAS: {roas:.2f}x with ${spend:.0f} spend',
                    'expected_impact': 'Stop losses immediately',
                    'risk_level': 'low'
                })

            # Scale recommendations
            elif roas >= thresholds.get('roas_excellent', 3.0) and spend > 50:
                actions.append({
                    'priority': 'high',
                    'action_type': 'scale',
                    'target': 'campaign',
                    'target_id': campaign.get('id'),
                    'target_name': campaign.get('name'),
                    'reason': f'Excellent ROAS: {roas:.2f}x - ready for scale',
                    'expected_impact': 'Increase revenue with maintained efficiency',
                    'risk_level': 'medium'
                })

        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        actions.sort(key=lambda x: priority_order.get(x['priority'], 4))

        return AgentResult(
            success=True,
            data={'actions': actions},
            message=f"Generated {len(actions)} optimization actions"
        )

    def _suggest_budget_reallocation(self, context: Dict[str, Any]) -> AgentResult:
        """Suggest budget reallocation across campaigns"""
        campaigns = context.get('campaigns', [])
        total_budget = context.get('total_budget', 0)

        # Calculate performance scores
        scored = []
        for campaign in campaigns:
            insights = campaign.get('insights', {}).get('data', [{}])[0] if campaign.get('insights') else {}
            roas_data = insights.get('purchase_roas', [{}])
            roas = float(roas_data[0].get('value', 0)) if roas_data else 0
            spend = float(insights.get('spend', 0))
            current_budget = float(campaign.get('daily_budget', 0)) / 100

            scored.append({
                'campaign': campaign.get('name'),
                'id': campaign.get('id'),
                'roas': roas,
                'current_budget': current_budget,
                'current_spend': spend,
                'score': roas * 10  # Simple scoring
            })

        # Calculate suggested allocation
        total_score = sum(c['score'] for c in scored if c['score'] > 0) or 1

        suggestions = []
        for c in scored:
            if c['score'] > 0:
                suggested_allocation = (c['score'] / total_score) * total_budget
                change = suggested_allocation - c['current_budget']
                suggestions.append({
                    'campaign': c['campaign'],
                    'current_budget': c['current_budget'],
                    'suggested_budget': suggested_allocation,
                    'change': change,
                    'change_percent': (change / c['current_budget'] * 100) if c['current_budget'] > 0 else 0,
                    'roas': c['roas']
                })

        return AgentResult(
            success=True,
            data={'reallocation_suggestions': suggestions},
            message="Budget reallocation suggestions generated"
        )

    def _generate_daily_report(self, context: Dict[str, Any]) -> AgentResult:
        """Generate daily performance report"""
        campaigns = context.get('campaigns', [])
        metrics = context.get('account_metrics', {})

        report = {
            'date': context.get('date', 'Today'),
            'summary': {
                'total_spend': metrics.get('spend', 0),
                'total_revenue': metrics.get('revenue', 0),
                'roas': metrics.get('roas', 0),
                'purchases': metrics.get('purchases', 0)
            },
            'highlights': [],
            'concerns': [],
            'action_items': []
        }

        # Generate highlights and concerns
        if metrics.get('roas', 0) >= 2.5:
            report['highlights'].append(f"Strong ROAS at {metrics.get('roas', 0):.2f}x")
        elif metrics.get('roas', 0) < 1.5:
            report['concerns'].append(f"ROAS below target at {metrics.get('roas', 0):.2f}x")

        return AgentResult(
            success=True,
            data=report,
            message="Daily report generated"
        )
