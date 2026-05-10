from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Protocol


def load_env_file() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    load_dotenv()


class AdvisorClient(Protocol):
    def get_advice(self, prompt: str) -> str:
        """Return strategic advice for the supplied prompt."""


@dataclass
class LLMConfig:
    base_url: str = "http://localhost:11434/v1/"
    api_key: str = "ollama"
    model: str = "qwen3-vl:8b"
    timeout: float = 180

    @classmethod
    def from_env(cls) -> "LLMConfig":
        load_env_file()

        timeout_value = os.getenv("ERP_AGENT_TIMEOUT", "180")
        try:
            timeout = float(timeout_value)
        except ValueError:
            timeout = 180

        return cls(
            base_url=os.getenv("ERP_AGENT_BASE_URL", "http://localhost:11434/v1/"),
            api_key=os.getenv("ERP_AGENT_API_KEY", "ollama"),
            model=os.getenv("ERP_AGENT_MODEL", "qwen3-vl:8b"),
            timeout=timeout,
        )


class OpenAIAdvisorClient:
    def __init__(self, config: LLMConfig | None = None):
        self.config = config or LLMConfig.from_env()

    def get_advice(self, prompt: str) -> str:
        from openai import OpenAI

        client = OpenAI(
            base_url=self.config.base_url,
            api_key=self.config.api_key,
        )
        response = client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            timeout=self.config.timeout,
        )
        return response.choices[0].message.content or ""


@dataclass
class FinancialState:
    cash: float = 100
    fixed_assets: float = 50
    inventory: float = 0
    loan: float = 0
    owner_equity: float = 100
    research_progress: dict[str, str] = field(
        default_factory=lambda: {"P1": "完成", "P2": "未开始"}
    )
    ad_budget: float = 0
    production_lines: int = 1
    fixed_cost_per_quarter: float = 10

    FIELD_MAP = {
        "现金": "cash",
        "固定资产": "fixed_assets",
        "库存": "inventory",
        "贷款": "loan",
        "所有者权益": "owner_equity",
        "研发进度": "research_progress",
        "广告费": "ad_budget",
        "生产线数量": "production_lines",
        "每季度固定支出": "fixed_cost_per_quarter",
    }

    def calculate_equity(self) -> float:
        self.owner_equity = self.cash + self.fixed_assets + self.inventory - self.loan
        return self.owner_equity

    def update(self, updates: dict[str, Any]) -> None:
        for key, value in updates.items():
            if key not in self.FIELD_MAP:
                raise KeyError(f"未知财务字段：{key}")
            setattr(self, self.FIELD_MAP[key], value)
        self.calculate_equity()

    def to_display_dict(self) -> dict[str, Any]:
        self.calculate_equity()
        return {
            "现金": self.cash,
            "固定资产": self.fixed_assets,
            "库存": self.inventory,
            "贷款": self.loan,
            "所有者权益": self.owner_equity,
            "研发进度": self.research_progress,
            "广告费": self.ad_budget,
            "生产线数量": self.production_lines,
            "每季度固定支出": self.fixed_cost_per_quarter,
        }


class ERPAgent:
    def __init__(
        self,
        advisor_client: AdvisorClient | None = None,
        state: FinancialState | None = None,
    ):
        self.round = 1
        self.history: list[dict[str, Any]] = []
        self.competitor_history: list[float] = []
        self.state = state or FinancialState()
        self.advisor_client = advisor_client or OpenAIAdvisorClient()

    @property
    def data(self) -> dict[str, Any]:
        return self.state.to_display_dict()

    def calculate_equity(self) -> float:
        return self.state.calculate_equity()

    def update_data(self, updates: dict[str, Any]) -> str:
        self.state.update(updates)
        return f"数据已更新，当前所有者权益：{self.state.owner_equity}"

    def show_status(self) -> str:
        lines = ["\n" + "=" * 45]
        lines.append(f"第 {self.round} 轮财务状态")
        lines.append("=" * 45)
        for key, value in self.data.items():
            lines.append(f" {key}: {value}")
        lines.append("=" * 45 + "\n")
        return "\n".join(lines)

    def cash_flow_deadline(self) -> tuple[str, int]:
        cash = self.state.cash
        fixed_cost = self.state.fixed_cost_per_quarter
        loan_interest = self.state.loan * 0.05
        total_cost_per_round = fixed_cost + loan_interest
        seasons = int(cash / total_cost_per_round) if total_cost_per_round > 0 else 999
        result = (
            "\n现金流预警：\n"
            f" 当前现金：{cash}\n"
            f" 每季度支出（含利息）：{round(total_cost_per_round, 2)}\n"
            f" 若拿不到订单，还能撑：{seasons} 个季度\n"
        )
        if seasons <= 2:
            result += " !!!高危警告：现金流紧张，谨慎贷款和广告!!!\n"
        return result, seasons

    def competitor_analysis(
        self, competitor_ads: list[float]
    ) -> tuple[str, float, float]:
        self.competitor_history.extend(competitor_ads)
        if not self.competitor_history:
            return "暂无对手数据", 0, 0

        avg = sum(self.competitor_history) / len(self.competitor_history)
        max_ad = max(self.competitor_history)
        suggestion_low = round(avg * 0.9, 1)
        suggestion_high = round(avg * 1.2, 1)
        result = (
            "\n对手广告费分析：\n"
            f" 历史平均：{round(avg, 1)}\n"
            f" 历史最高：{max_ad}\n"
            f" 建议本轮广告费区间：{suggestion_low} ~ {suggestion_high}\n"
        )
        return result, suggestion_low, suggestion_high

    def build_prompt(self, market_info: str, seasons_left: int) -> str:
        return (
            f"你是ERP比赛CEO顾问，给出第{self.round}轮决策建议。\n"
            f"财务数据：{self.data}\n"
            f"市场信息：{market_info}\n"
            f"历史决策：{self.history[-3:] if self.history else '暂无'}\n"
            f"现金流警告：还能撑{seasons_left}季度\n"
            "核心规则：最终以所有者权益高低决定胜负，贷款有利息风险。\n\n"
            "请给出：\n"
            "1. 广告费建议金额及理由\n"
            "2. 是否贷款，贷多少\n"
            "3. 生产线调整建议\n"
            "4. 研发投入建议\n"
            "5. 本轮最优先事项"
        )

    def get_strategic_advice(self, market_info: str) -> str:
        status_text = self.show_status()
        warning_text, seasons_left = self.cash_flow_deadline()

        try:
            prompt = self.build_prompt(market_info, seasons_left)
            advice = self.advisor_client.get_advice(prompt)
            self.history.append(
                {
                    "轮次": self.round,
                    "市场": market_info,
                    "权益": self.state.owner_equity,
                }
            )
            self.round += 1

            return status_text + warning_text + "\nAI建议：\n" + advice
        except Exception as exc:
            return f"\n❌ 无法连接AI模型：{exc}\n请确保 Ollama 已运行，或检查网络设置。"
