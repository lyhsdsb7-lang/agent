import os
import unittest
from unittest.mock import patch

from erp_agent_core import ERPAgent, FinancialState, LLMConfig


class FakeAdvisorClient:
    def __init__(self):
        self.prompts = []

    def get_advice(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return "建议：控制现金流，谨慎投放广告。"


class ERPAgentCoreTests(unittest.TestCase):
    def test_update_data_recalculates_equity(self):
        agent = ERPAgent(advisor_client=FakeAdvisorClient())

        message = agent.update_data({"现金": 120, "固定资产": 80, "库存": 20, "贷款": 50})

        self.assertEqual(agent.state.owner_equity, 170)
        self.assertIn("170", message)

    def test_unknown_financial_field_is_rejected(self):
        agent = ERPAgent(advisor_client=FakeAdvisorClient())

        with self.assertRaises(KeyError):
            agent.update_data({"现金余额": 100})

    def test_cash_flow_deadline_includes_loan_interest(self):
        state = FinancialState(cash=100, loan=100, fixed_cost_per_quarter=10)
        agent = ERPAgent(advisor_client=FakeAdvisorClient(), state=state)

        message, seasons = agent.cash_flow_deadline()

        self.assertEqual(seasons, 6)
        self.assertIn("15.0", message)

    def test_competitor_analysis_returns_suggestion_range(self):
        agent = ERPAgent(advisor_client=FakeAdvisorClient())

        message, low, high = agent.competitor_analysis([15, 20, 18])

        self.assertEqual(low, 15.9)
        self.assertEqual(high, 21.2)
        self.assertIn("历史最高：20", message)

    def test_get_strategic_advice_records_history_and_uses_client(self):
        advisor = FakeAdvisorClient()
        agent = ERPAgent(advisor_client=advisor)

        response = agent.get_strategic_advice("市场需求旺盛")

        self.assertIn("AI建议", response)
        self.assertEqual(agent.round, 2)
        self.assertEqual(len(agent.history), 1)
        self.assertEqual(agent.history[0]["市场"], "市场需求旺盛")
        self.assertEqual(len(advisor.prompts), 1)
        self.assertIn("市场需求旺盛", advisor.prompts[0])

    def test_llm_config_reads_environment(self):
        env = {
            "ERP_AGENT_BASE_URL": "http://localhost:11434/v1/",
            "ERP_AGENT_API_KEY": "test-key",
            "ERP_AGENT_MODEL": "qwen3:8b",
            "ERP_AGENT_TIMEOUT": "30",
        }
        with patch.dict(os.environ, env, clear=False):
            config = LLMConfig.from_env()

        self.assertEqual(config.api_key, "test-key")
        self.assertEqual(config.model, "qwen3:8b")
        self.assertEqual(config.timeout, 30)


if __name__ == "__main__":
    unittest.main()
