import threading
import tkinter as tk

import customtkinter as ctk

from erp_agent_core import ERPAgent


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ERPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ERP 沙盘 AI 决策助手")
        self.root.geometry("1180x760")
        self.root.minsize(1040, 680)

        self.agent = ERPAgent()
        self.is_busy = False
        self.metric_vars = {}

        self.bg = "#0b1120"
        self.panel = "#111827"
        self.panel_soft = "#172033"
        self.border = "#263244"
        self.text = "#e5e7eb"
        self.muted = "#94a3b8"
        self.blue = "#3b82f6"
        self.green = "#22c55e"
        self.red = "#ef4444"

        self.status_var = tk.StringVar(value="就绪")
        self.round_var = tk.StringVar()
        self.model_var = tk.StringVar(value=self.get_model_label())

        self.root.configure(fg_color=self.bg)
        self.build_layout()
        self.refresh_metrics()
        self.print_message(
            "欢迎使用 ERP 沙盘 AI 决策助手。\n\n"
            "把本轮市场需求、竞争对手广告费、原材料价格、订单压力等信息写在下方，"
            "系统会结合当前财务状态生成经营建议。",
            role="assistant",
        )

    def build_layout(self):
        shell = ctk.CTkFrame(self.root, fg_color=self.bg, corner_radius=0)
        shell.pack(fill="both", expand=True, padx=18, pady=18)
        shell.grid_columnconfigure(1, weight=1)
        shell.grid_rowconfigure(1, weight=1)

        self.build_sidebar(shell)
        self.build_header(shell)
        self.build_workspace(shell)
        self.build_status(shell)

    def build_sidebar(self, parent):
        sidebar = ctk.CTkFrame(parent, fg_color="#0f172a", corner_radius=24, border_width=1, border_color=self.border)
        sidebar.grid(row=0, column=0, rowspan=3, sticky="nsew", padx=(0, 18))
        sidebar.grid_rowconfigure(2, weight=1)

        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=18, pady=(20, 16))
        ctk.CTkLabel(
            brand,
            text="ERP Agent",
            text_color="#ffffff",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=22, weight="bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            brand,
            text="沙盘经营决策面板",
            text_color=self.muted,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        ).pack(anchor="w", pady=(4, 0))

        nav = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 14))
        self.add_nav_item(nav, "经营建议", active=True)
        self.add_nav_item(nav, "财务监控")
        self.add_nav_item(nav, "风险预警")
        self.add_nav_item(nav, "历史复盘")

        guide = ctk.CTkFrame(sidebar, fg_color="#14213a", corner_radius=18, border_width=1, border_color="#20314f")
        guide.grid(row=3, column=0, sticky="ew", padx=14, pady=(14, 16))
        ctk.CTkLabel(
            guide,
            text="输入建议",
            text_color="#dbeafe",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=14, weight="bold"),
        ).pack(anchor="w", padx=14, pady=(14, 4))
        ctk.CTkLabel(
            guide,
            text="描述市场变化、对手投放、资金压力和你想尝试的策略，AI 会按本轮经营目标给出建议。",
            text_color="#bfdbfe",
            justify="left",
            wraplength=210,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        ).pack(anchor="w", padx=14, pady=(0, 14))

    def add_nav_item(self, parent, text, active=False):
        item = ctk.CTkFrame(parent, fg_color="#1d4ed8" if active else "transparent", corner_radius=14)
        item.pack(fill="x", pady=4)
        ctk.CTkLabel(
            item,
            text=text,
            text_color="#ffffff" if active else self.muted,
            anchor="w",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=13, weight="bold" if active else "normal"),
        ).pack(fill="x", padx=14, pady=10)

    def build_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color=self.bg, corner_radius=0)
        header.grid(row=0, column=1, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="本轮经营决策",
            text_color="#ffffff",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=28, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header,
            textvariable=self.model_var,
            text_color=self.muted,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

        round_badge = ctk.CTkFrame(header, fg_color="#172554", corner_radius=16, border_width=1, border_color="#1d4ed8")
        round_badge.grid(row=0, column=1, rowspan=2, sticky="e")
        ctk.CTkLabel(
            round_badge,
            textvariable=self.round_var,
            text_color="#bfdbfe",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=14, weight="bold"),
        ).pack(padx=18, pady=12)

    def build_workspace(self, parent):
        workspace = ctk.CTkFrame(parent, fg_color=self.bg, corner_radius=0)
        workspace.grid(row=1, column=1, sticky="nsew", pady=(18, 0))
        workspace.grid_columnconfigure(0, weight=0)
        workspace.grid_columnconfigure(1, weight=1)
        workspace.grid_rowconfigure(1, weight=1)

        self.build_metrics(workspace)
        self.build_advice_panel(workspace)
        self.build_input_panel(workspace)

    def build_metrics(self, parent):
        metrics = ctk.CTkFrame(parent, fg_color="transparent")
        metrics.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        for index in range(4):
            metrics.grid_columnconfigure(index, weight=1)

        cards = [
            ("现金", "cash", self.blue),
            ("所有者权益", "owner_equity", self.green),
            ("贷款", "loan", "#f97316"),
            ("现金可撑季度", "cash_runway", "#a855f7"),
        ]
        for index, (label, key, color) in enumerate(cards):
            self.add_metric_card(metrics, label, key, color, index)

    def add_metric_card(self, parent, label, key, color, column):
        card = ctk.CTkFrame(parent, fg_color=self.panel, corner_radius=20, border_width=1, border_color=self.border)
        card.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 10, 0 if column == 3 else 10))

        value_var = tk.StringVar(value="-")
        self.metric_vars[key] = value_var

        ctk.CTkLabel(
            card,
            text=label,
            text_color=self.muted,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        ).pack(anchor="w", padx=18, pady=(16, 4))
        ctk.CTkLabel(
            card,
            textvariable=value_var,
            text_color="#ffffff",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=26, weight="bold"),
        ).pack(anchor="w", padx=18)
        ctk.CTkFrame(card, fg_color=color, corner_radius=8, height=4).pack(fill="x", padx=18, pady=(14, 16))

    def build_advice_panel(self, parent):
        panel = ctk.CTkFrame(parent, fg_color=self.panel, corner_radius=24, border_width=1, border_color=self.border)
        panel.grid(row=1, column=1, sticky="nsew")
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        head = ctk.CTkFrame(panel, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 8))
        head.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            head,
            text="AI 决策建议",
            text_color="#ffffff",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            head,
            text="保留历史输出，方便赛后复盘",
            text_color=self.muted,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        ).grid(row=0, column=1, sticky="e")

        self.chat_area = ctk.CTkTextbox(
            panel,
            fg_color="#0f172a",
            text_color=self.text,
            border_width=1,
            border_color="#1f2937",
            corner_radius=18,
            wrap="word",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=13),
        )
        self.chat_area.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self.chat_area.configure(state="disabled")

    def build_input_panel(self, parent):
        panel = ctk.CTkFrame(parent, fg_color=self.panel, corner_radius=24, border_width=1, border_color=self.border)
        panel.grid(row=1, column=0, sticky="nsew", padx=(0, 16))
        panel.grid_rowconfigure(2, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel,
            text="市场情报",
            text_color="#ffffff",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 4))
        ctk.CTkLabel(
            panel,
            text="Shift+Enter 换行，Enter 发送",
            text_color=self.muted,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        ).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 12))

        self.input_box = ctk.CTkTextbox(
            panel,
            width=310,
            height=250,
            fg_color="#0f172a",
            text_color=self.text,
            border_width=1,
            border_color="#1f2937",
            corner_radius=18,
            wrap="word",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=13),
        )
        self.input_box.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 14))

        actions = ctk.CTkFrame(panel, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 18))
        actions.grid_columnconfigure(0, weight=1)
        self.clear_btn = ctk.CTkButton(
            actions,
            text="清空",
            width=92,
            fg_color="#1f2937",
            hover_color="#374151",
            command=self.clear_input,
        )
        self.clear_btn.grid(row=0, column=0, sticky="w")
        self.send_btn = ctk.CTkButton(
            actions,
            text="生成建议",
            width=132,
            height=40,
            fg_color=self.blue,
            hover_color="#2563eb",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=13, weight="bold"),
            command=self.send_message,
        )
        self.send_btn.grid(row=0, column=1, sticky="e")
        self.input_box.bind("<Return>", self.handle_return)

    def build_status(self, parent):
        status = ctk.CTkFrame(parent, fg_color="transparent")
        status.grid(row=2, column=1, sticky="ew", pady=(12, 0))
        ctk.CTkLabel(
            status,
            textvariable=self.status_var,
            text_color=self.muted,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        ).pack(anchor="w")

    def get_model_label(self):
        config = getattr(self.agent.advisor_client, "config", None) if hasattr(self, "agent") else None
        if not config:
            return "模型未配置"
        return f"{config.model}  ·  {config.base_url}"

    def handle_return(self, event):
        if event.state & 0x1:
            return None
        self.send_message()
        return "break"

    def clear_input(self):
        self.input_box.delete("1.0", "end")

    def print_message(self, message, role="assistant"):
        prefix = {"user": "我", "error": "错误"}.get(role, "AI 建议")
        color = {"user": "#93c5fd", "error": "#fca5a5"}.get(role, "#86efac")
        self.chat_area.configure(state="normal")
        self.chat_area.insert("end", f"{prefix}\n")
        self.chat_area.insert("end", message + "\n\n")
        self.chat_area.configure(state="disabled")
        self.chat_area.see("end")
        self.chat_area._textbox.tag_add(prefix, "end-3l linestart", "end-3l lineend")
        self.chat_area._textbox.tag_config(prefix, foreground=color)

    def set_busy(self, is_busy: bool):
        self.is_busy = is_busy
        state = "disabled" if is_busy else "normal"
        self.send_btn.configure(state=state)
        self.clear_btn.configure(state=state)
        self.status_var.set("AI 正在生成建议，请稍候..." if is_busy else "就绪")

    def refresh_metrics(self):
        data = self.agent.data
        _, cash_runway = self.agent.cash_flow_deadline()
        values = {
            "cash": data["现金"],
            "owner_equity": data["所有者权益"],
            "loan": data["贷款"],
            "cash_runway": cash_runway,
        }
        for key, value in values.items():
            self.metric_vars[key].set(str(value))
        self.round_var.set(f"第 {self.agent.round} 轮")

    def send_message(self):
        if self.is_busy:
            return

        user_text = self.input_box.get("1.0", "end").strip()
        if not user_text:
            self.status_var.set("请输入本轮市场情报")
            return

        self.print_message(user_text, role="user")
        self.input_box.delete("1.0", "end")
        self.set_busy(True)

        thread = threading.Thread(target=self.process_ai_response, args=(user_text,), daemon=True)
        thread.start()

    def process_ai_response(self, market_info):
        try:
            response = self.agent.get_strategic_advice(market_info)
            self.root.after(0, lambda: self.print_message(response, role="assistant"))
        except Exception as exc:
            self.root.after(0, lambda: self.print_message(str(exc), role="error"))
        finally:
            self.root.after(0, self.refresh_metrics)
            self.root.after(0, lambda: self.set_busy(False))
