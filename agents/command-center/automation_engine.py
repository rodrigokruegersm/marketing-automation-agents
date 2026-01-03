"""
=============================================================================
COMMAND CENTER - Automation Engine
=============================================================================
Monitors KPIs, evaluates thresholds, and triggers agent actions automatically.

Usage:
    python automation_engine.py --mode=check      # Single threshold check
    python automation_engine.py --mode=daemon     # Continuous monitoring
    python automation_engine.py --mode=report     # Generate daily report
=============================================================================
"""

import os
import sys
import yaml
import json
import requests
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time
import argparse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = Path(__file__).parent.parent.parent
THRESHOLDS_FILE = Path(__file__).parent / "thresholds.yaml"
DATA_DIR = BASE_DIR / "clients" / "brez-scales" / "data"
REPORTS_DIR = BASE_DIR / "clients" / "brez-scales" / "reports"

# Meta Ads Configuration
META_ACCESS_TOKEN = os.getenv(
    'META_ACCESS_TOKEN',
    'EAARxSEanVtUBQfauZBuy1WI8Luaq4A9pj4pD7N6dUvaL9aPCorg8W2G5dDpdyze2OtLVc8RnGxNazo1ri1mHNwNY54Dk1AE6HTLBFxQnIwl6j9qU3eFzhzxHT9k08Qx2E5lopXDmcfNPcZCdWobZC4j0wuHjNsd2ONMTLQu2XU0q9iaZClBjtAl16CGYYgZDZD'
)
META_AD_ACCOUNT_ID = os.getenv('META_AD_ACCOUNT_ID', 'act_1202800550735727')

# =============================================================================
# DATA CLASSES
# =============================================================================

class Urgency(Enum):
    IMMEDIATE = "immediate"
    WITHIN_24H = "within_24h"
    OPPORTUNITY = "opportunity"
    NONE = "none"

@dataclass
class ThresholdResult:
    kpi: str
    value: float
    threshold_level: str
    action: str
    urgency: Urgency
    message: str

@dataclass
class ActionTrigger:
    agent: str
    command: str
    params: Dict[str, Any]
    notify: bool
    escalate_to_human: bool
    next_agent: Optional[str] = None
    next_command: Optional[str] = None

# =============================================================================
# META ADS DATA FETCHER
# =============================================================================

class MetaAdsFetcher:
    """Fetches data from Meta Ads API"""

    def __init__(self, access_token: str, account_id: str):
        self.access_token = access_token
        self.account_id = account_id
        self.base_url = "https://graph.facebook.com/v18.0"

    def fetch_insights(self, date_preset: str = "last_7d") -> Optional[Dict]:
        """Fetch account-level insights"""
        url = f"{self.base_url}/{self.account_id}/insights"
        params = {
            'fields': 'spend,impressions,reach,frequency,cpm,clicks,cpc,ctr,actions,action_values,cost_per_action_type,purchase_roas',
            'date_preset': date_preset,
            'access_token': self.access_token
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()

            if 'data' in data and len(data['data']) > 0:
                return data['data'][0]
            return None

        except Exception as e:
            logger.error(f"Error fetching Meta data: {e}")
            return None

    def parse_metrics(self, raw_data: Dict) -> Dict[str, float]:
        """Parse raw API data into clean metrics"""
        if not raw_data:
            return {}

        def extract_action(actions: List, action_type: str) -> float:
            if not actions:
                return 0
            for action in actions:
                if action.get('action_type') == action_type:
                    return float(action.get('value', 0))
            return 0

        actions = raw_data.get('actions', [])
        action_values = raw_data.get('action_values', [])
        cost_per_action = raw_data.get('cost_per_action_type', [])

        spend = float(raw_data.get('spend', 0))
        impressions = int(raw_data.get('impressions', 0))
        clicks = int(raw_data.get('clicks', 0))
        lp_views = extract_action(actions, 'landing_page_view')
        checkouts = extract_action(actions, 'initiate_checkout')
        purchases = extract_action(actions, 'purchase')
        revenue = extract_action(action_values, 'purchase')

        # Calculate derived metrics
        metrics = {
            'spend': spend,
            'revenue': revenue,
            'impressions': impressions,
            'reach': int(raw_data.get('reach', 0)),
            'frequency': float(raw_data.get('frequency', 0)),
            'cpm': float(raw_data.get('cpm', 0)),
            'clicks': clicks,
            'cpc': float(raw_data.get('cpc', 0)),
            'ctr': float(raw_data.get('ctr', 0)),
            'lp_views': lp_views,
            'checkouts': checkouts,
            'purchases': purchases,

            # Calculated KPIs
            'roas': revenue / spend if spend > 0 else 0,
            'cpp': spend / purchases if purchases > 0 else 0,
            'lp_view_rate': (lp_views / clicks * 100) if clicks > 0 else 0,
            'checkout_rate': (checkouts / lp_views * 100) if lp_views > 0 else 0,
            'close_rate': (purchases / checkouts * 100) if checkouts > 0 else 0,
            'profit': revenue - spend,
            'margin': ((revenue - spend) / revenue * 100) if revenue > 0 else 0
        }

        return metrics

# =============================================================================
# THRESHOLD EVALUATOR
# =============================================================================

class ThresholdEvaluator:
    """Evaluates KPIs against defined thresholds"""

    def __init__(self, config_path: Path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.kpis = self.config.get('kpis', {})
        self.composite_rules = self.config.get('composite_rules', [])

    def evaluate_kpi(self, kpi_name: str, value: float) -> Optional[ThresholdResult]:
        """Evaluate a single KPI against its thresholds"""
        if kpi_name not in self.kpis:
            return None

        kpi_config = self.kpis[kpi_name]
        thresholds = kpi_config.get('thresholds', {})

        # Check thresholds in order of severity
        for level in ['critical', 'warning', 'good', 'excellent', 'healthy', 'optimal']:
            if level not in thresholds:
                continue

            threshold = thresholds[level]
            threshold_value = threshold['value']
            operator = threshold['operator']

            # Evaluate condition
            triggered = False
            if operator == '<' and value < threshold_value:
                triggered = True
            elif operator == '<=' and value <= threshold_value:
                triggered = True
            elif operator == '>' and value > threshold_value:
                triggered = True
            elif operator == '>=' and value >= threshold_value:
                triggered = True

            if triggered:
                return ThresholdResult(
                    kpi=kpi_name,
                    value=value,
                    threshold_level=level,
                    action=threshold.get('action', 'NONE'),
                    urgency=Urgency(threshold.get('urgency', 'none')),
                    message=f"{kpi_name.upper()}: {value:.2f} triggered {level.upper()} threshold ({operator} {threshold_value})"
                )

        return None

    def evaluate_all(self, metrics: Dict[str, float]) -> List[ThresholdResult]:
        """Evaluate all KPIs and return triggered thresholds"""
        results = []

        kpi_mapping = {
            'roas': metrics.get('roas', 0),
            'cpp': metrics.get('cpp', 0),
            'ctr': metrics.get('ctr', 0),
            'frequency': metrics.get('frequency', 0),
            'lp_view_rate': metrics.get('lp_view_rate', 0),
            'checkout_rate': metrics.get('checkout_rate', 0),
            'close_rate': metrics.get('close_rate', 0)
        }

        for kpi_name, value in kpi_mapping.items():
            result = self.evaluate_kpi(kpi_name, value)
            if result:
                results.append(result)

        return results

    def evaluate_composite(self, metrics: Dict[str, float], threshold_results: List[ThresholdResult]) -> List[Dict]:
        """Evaluate composite rules that depend on multiple KPIs"""
        triggered_rules = []

        # Create lookup of triggered levels
        triggered_levels = {r.kpi: r.threshold_level for r in threshold_results}

        for rule in self.composite_rules:
            conditions = rule.get('conditions', [])
            all_met = True

            for condition in conditions:
                kpi = condition['kpi']
                required_level = condition['threshold']

                if kpi not in triggered_levels or triggered_levels[kpi] != required_level:
                    all_met = False
                    break

            if all_met:
                triggered_rules.append(rule)

        return triggered_rules

    def get_action_config(self, kpi_name: str, action_name: str) -> Optional[Dict]:
        """Get action configuration for a KPI"""
        if kpi_name not in self.kpis:
            return None

        actions = self.kpis[kpi_name].get('actions', {})
        return actions.get(action_name)

# =============================================================================
# ACTION EXECUTOR
# =============================================================================

class ActionExecutor:
    """Executes triggered actions by calling appropriate agents"""

    def __init__(self, evaluator: ThresholdEvaluator):
        self.evaluator = evaluator
        self.action_log = []

    def execute(self, threshold_result: ThresholdResult) -> Dict:
        """Execute action for a threshold result"""
        action_config = self.evaluator.get_action_config(
            threshold_result.kpi,
            threshold_result.action
        )

        if not action_config:
            return {"status": "no_action", "reason": "Action config not found"}

        trigger = ActionTrigger(
            agent=action_config.get('agent'),
            command=action_config.get('command'),
            params=action_config.get('params', {}),
            notify=action_config.get('notify', False),
            escalate_to_human=action_config.get('escalate_to_human', False),
            next_agent=action_config.get('next_agent'),
            next_command=action_config.get('next_command')
        )

        # Log the action
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "kpi": threshold_result.kpi,
            "value": threshold_result.value,
            "level": threshold_result.threshold_level,
            "action": threshold_result.action,
            "agent": trigger.agent,
            "command": trigger.command,
            "urgency": threshold_result.urgency.value
        }
        self.action_log.append(log_entry)

        # Execute based on agent type
        if trigger.agent == "ad-launcher":
            return self._execute_ad_launcher(trigger)
        elif trigger.agent == "data-pulse":
            return self._execute_data_pulse(trigger)
        elif trigger.agent == "copy-forge":
            return self._execute_copy_forge(trigger)
        elif trigger.agent is None:
            return {"status": "logged", "message": threshold_result.message}

        return {"status": "unknown_agent", "agent": trigger.agent}

    def _execute_ad_launcher(self, trigger: ActionTrigger) -> Dict:
        """Execute Ad Launcher commands"""
        logger.info(f"🚀 AD LAUNCHER: {trigger.command}")
        logger.info(f"   Params: {trigger.params}")

        # Here we would call the actual MCP or API
        # For now, we log and return the intended action
        return {
            "status": "executed",
            "agent": "ad-launcher",
            "command": trigger.command,
            "params": trigger.params,
            "notify": trigger.notify
        }

    def _execute_data_pulse(self, trigger: ActionTrigger) -> Dict:
        """Execute Data Pulse commands"""
        logger.info(f"📊 DATA PULSE: {trigger.command}")
        logger.info(f"   Params: {trigger.params}")

        return {
            "status": "executed",
            "agent": "data-pulse",
            "command": trigger.command,
            "params": trigger.params
        }

    def _execute_copy_forge(self, trigger: ActionTrigger) -> Dict:
        """Execute Copy Forge commands"""
        logger.info(f"✍️ COPY FORGE: {trigger.command}")
        logger.info(f"   Params: {trigger.params}")

        return {
            "status": "executed",
            "agent": "copy-forge",
            "command": trigger.command,
            "params": trigger.params
        }

# =============================================================================
# DATA LOGGER (Spreadsheet Updates)
# =============================================================================

class DataLogger:
    """Logs metrics to files for historical tracking"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def log_daily_metrics(self, metrics: Dict[str, float], date: str = None):
        """Append daily metrics to CSV"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        csv_path = self.data_dir / "daily_metrics.csv"

        # Create header if file doesn't exist
        if not csv_path.exists():
            headers = ['date'] + list(metrics.keys())
            with open(csv_path, 'w') as f:
                f.write(','.join(headers) + '\n')

        # Append data
        values = [date] + [str(round(v, 2)) for v in metrics.values()]
        with open(csv_path, 'a') as f:
            f.write(','.join(values) + '\n')

        logger.info(f"📝 Logged metrics for {date}")
        return csv_path

    def log_action(self, action_log: List[Dict]):
        """Log executed actions"""
        json_path = self.data_dir / "action_log.json"

        existing = []
        if json_path.exists():
            with open(json_path, 'r') as f:
                existing = json.load(f)

        existing.extend(action_log)

        with open(json_path, 'w') as f:
            json.dump(existing, f, indent=2)

        logger.info(f"📝 Logged {len(action_log)} actions")

# =============================================================================
# REPORT GENERATOR
# =============================================================================

class ReportGenerator:
    """Generates daily and weekly reports"""

    def __init__(self, reports_dir: Path):
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_daily_pulse(self, metrics: Dict, threshold_results: List[ThresholdResult]) -> str:
        """Generate daily pulse report"""
        date = datetime.now().strftime('%Y-%m-%d')
        report_path = self.reports_dir / f"daily_pulse_{date}.md"

        # Determine overall status
        critical_count = sum(1 for r in threshold_results if r.threshold_level == 'critical')
        warning_count = sum(1 for r in threshold_results if r.threshold_level == 'warning')

        if critical_count > 0:
            status = "🔴 CRITICAL"
        elif warning_count > 0:
            status = "🟡 WARNING"
        else:
            status = "🟢 HEALTHY"

        # Build report
        report = f"""# Daily Pulse - {date}
## Status: {status}

---

## Key Metrics

| KPI | Value | Status |
|-----|-------|--------|
| ROAS | {metrics.get('roas', 0):.2f}x | {'🟢' if metrics.get('roas', 0) >= 2 else '🔴'} |
| Revenue | ${metrics.get('revenue', 0):,.2f} | - |
| Spend | ${metrics.get('spend', 0):,.2f} | - |
| Profit | ${metrics.get('profit', 0):,.2f} | {'🟢' if metrics.get('profit', 0) > 0 else '🔴'} |
| CPP | ${metrics.get('cpp', 0):.2f} | {'🟢' if metrics.get('cpp', 0) < 20 else '🔴'} |
| CTR | {metrics.get('ctr', 0):.2f}% | {'🟢' if metrics.get('ctr', 0) >= 2 else '🟡'} |
| Frequency | {metrics.get('frequency', 0):.2f} | {'🟢' if metrics.get('frequency', 0) < 2.5 else '🔴'} |
| Purchases | {int(metrics.get('purchases', 0))} | - |

---

## Threshold Alerts

"""

        if threshold_results:
            for result in threshold_results:
                emoji = {'critical': '🔴', 'warning': '🟡', 'good': '🟢', 'excellent': '🌟'}.get(result.threshold_level, '⚪')
                report += f"- {emoji} **{result.kpi.upper()}**: {result.message}\n"
                report += f"  - Action: `{result.action}`\n"
                report += f"  - Urgency: {result.urgency.value}\n\n"
        else:
            report += "*No alerts - all metrics within healthy ranges*\n"

        report += f"""
---

## Financial Summary

- **Gross Profit**: ${metrics.get('profit', 0):,.2f}
- **Margin**: {metrics.get('margin', 0):.1f}%
- **Commission (20%)**: ${metrics.get('profit', 0) * 0.20:,.2f}

---

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        with open(report_path, 'w') as f:
            f.write(report)

        logger.info(f"📄 Generated daily pulse: {report_path}")
        return str(report_path)

# =============================================================================
# MAIN AUTOMATION ENGINE
# =============================================================================

class AutomationEngine:
    """Main orchestrator for the automation system"""

    def __init__(self):
        self.fetcher = MetaAdsFetcher(META_ACCESS_TOKEN, META_AD_ACCOUNT_ID)
        self.evaluator = ThresholdEvaluator(THRESHOLDS_FILE)
        self.executor = ActionExecutor(self.evaluator)
        self.data_logger = DataLogger(DATA_DIR)
        self.report_generator = ReportGenerator(REPORTS_DIR)

    def run_check(self, date_preset: str = "last_3d") -> Dict:
        """Run a single threshold check"""
        logger.info("=" * 60)
        logger.info("🤖 COMMAND CENTER - Automation Check")
        logger.info("=" * 60)

        # 1. Fetch data
        logger.info("📡 Fetching Meta Ads data...")
        raw_data = self.fetcher.fetch_insights(date_preset)

        if not raw_data:
            logger.error("❌ Failed to fetch data")
            return {"status": "error", "reason": "data_fetch_failed"}

        # 2. Parse metrics
        metrics = self.fetcher.parse_metrics(raw_data)
        logger.info(f"📊 ROAS: {metrics['roas']:.2f}x | Revenue: ${metrics['revenue']:,.0f} | Spend: ${metrics['spend']:,.0f}")

        # 3. Evaluate thresholds
        logger.info("\n🎯 Evaluating thresholds...")
        threshold_results = self.evaluator.evaluate_all(metrics)

        # 4. Check composite rules
        composite_triggers = self.evaluator.evaluate_composite(metrics, threshold_results)

        # 5. Execute actions
        logger.info("\n⚡ Executing actions...")
        executed_actions = []

        for result in threshold_results:
            if result.urgency in [Urgency.IMMEDIATE, Urgency.WITHIN_24H, Urgency.OPPORTUNITY]:
                action_result = self.executor.execute(result)
                executed_actions.append(action_result)

        # 6. Log data
        self.data_logger.log_daily_metrics(metrics)
        self.data_logger.log_action(self.executor.action_log)

        # 7. Generate report
        report_path = self.report_generator.generate_daily_pulse(metrics, threshold_results)

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("✅ CHECK COMPLETE")
        logger.info(f"   Thresholds triggered: {len(threshold_results)}")
        logger.info(f"   Actions executed: {len(executed_actions)}")
        logger.info(f"   Report: {report_path}")
        logger.info("=" * 60)

        return {
            "status": "success",
            "metrics": metrics,
            "threshold_results": [
                {
                    "kpi": r.kpi,
                    "value": r.value,
                    "level": r.threshold_level,
                    "action": r.action
                }
                for r in threshold_results
            ],
            "actions_executed": executed_actions,
            "report_path": report_path
        }

    def run_daemon(self, interval_minutes: int = 60):
        """Run continuous monitoring"""
        logger.info("🔄 Starting daemon mode...")
        logger.info(f"   Check interval: {interval_minutes} minutes")

        while True:
            try:
                self.run_check()
                logger.info(f"\n💤 Sleeping for {interval_minutes} minutes...\n")
                time.sleep(interval_minutes * 60)

            except KeyboardInterrupt:
                logger.info("\n👋 Daemon stopped by user")
                break

            except Exception as e:
                logger.error(f"❌ Error in daemon loop: {e}")
                time.sleep(60)  # Wait 1 minute before retry

# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Command Center Automation Engine')
    parser.add_argument('--mode', choices=['check', 'daemon', 'report'],
                        default='check', help='Operation mode')
    parser.add_argument('--period', default='last_3d',
                        help='Date preset for data (yesterday, last_3d, last_7d)')
    parser.add_argument('--interval', type=int, default=60,
                        help='Check interval in minutes (daemon mode)')

    args = parser.parse_args()

    engine = AutomationEngine()

    if args.mode == 'check':
        result = engine.run_check(args.period)
        print(json.dumps(result, indent=2, default=str))

    elif args.mode == 'daemon':
        engine.run_daemon(args.interval)

    elif args.mode == 'report':
        result = engine.run_check(args.period)
        print(f"\nReport generated: {result.get('report_path')}")

if __name__ == "__main__":
    main()
