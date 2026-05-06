import tkinter as tk
from tkinter import scrolledtext, END, Button, Frame
import threading
import requests
import json
import base64
import pandas as pd
import os
from openai import OpenAI

# ==================== 1. 核心 Agent 类 (未改动你的核心逻辑) ====================
class ERPAgent:
    def __init__(self):
        self.round = 1
        self.history = []
        self.competitor_history = []
        self.data = {
            "现金": 100,
            "固定资产": 50,
            "库存": 0,
            "贷款": 0,
            "所有者权益": 100,
            "研发进度": {"P1": "完成", "P2": "未开始"},
            "广告费": 0,
            "生产线数量": 1,
            "每季度固定支出": 10
        }

    def calculate_equity(self):
        equity = (self.data["现金"] + self.data["固定资产"]
                  + self.data["库存"] - self.data["贷款"])
        self.data["所有者权益"] = equity
        return equity

    def update_data(self, updates: dict):
        self.data.update(updates)
        self.calculate_equity()
        return "数据已更新，当前所有者权益：" + str(self.data["所有者权益"])

    def show_status(self):
        lines = []
        lines.append("\n" + "="*45)
        lines.append(f"第 {self.round} 轮财务状态")
        lines.append("="*45)
        for k, v in self.data.items():
            lines.append(f" {k}: {v}")
        lines.append("="*45 + "\n")
        return "\n".join(lines)

    def cash_flow_deadline(self):
        cash = self.data["现金"]
        fixed_cost = self.data["每季度固定支出"]
        loan = self.data["贷款"]
        loan_interest = loan * 0.05
        total_cost_per_round = fixed_cost + loan_interest
        seasons = int(cash / total_cost_per_round) if total_cost_per_round > 0 else 999
        result = (
            f"\n现金流预警：\n"
            f" 当前现金：{cash}\n"
            f" 每季度支出（含利息）：{round(total_cost_per_round, 2)}\n"
            f" 若拿不到订单，还能撑：{seasons} 个季度\n"
        )
        if seasons <= 2:
            result += " !!!高危警告：现金流紧张，谨慎贷款和广告!!!\n"
        return result, seasons

    def competitor_analysis(self, competitor_ads):
        self.competitor_history.extend(competitor_ads)
        if not self.competitor_history:
            return "暂无对手数据", 0, 0
        avg = sum(self.competitor_history) / len(self.competitor_history)
        max_ad = max(self.competitor_history)
        suggestion_low = round(avg * 0.9, 1)
        suggestion_high = round(avg * 1.2, 1)
        result = (
            f"\n对手广告费分析：\n"
            f" 历史平均：{round(avg, 1)}\n"
            f" 历史最高：{max_ad}\n"
            f" 建议本轮广告费区间：{suggestion_low} ~ {suggestion_high}\n"
        )
        return result, suggestion_low, suggestion_high

    def get_strategic_advice(self, market_info):
        status_text = self.show_status()
        warning_text, seasons_left = self.cash_flow_deadline()
        
        # 这里是连接大模型的核心逻辑
        try:
            # --- 修改这里：配置你的模型连接 ---
            client = OpenAI(
                base_url='http://localhost:11434/v1/', # 如果是云端API，请改为此处的URL
                api_key='ollama' # 如果是云端API，请改为你的实际 Key
            )
            
            prompt = (
                f"你是ERP比赛CEO顾问，给出第{self.round}轮决策建议。\n"
                f"财务数据：{str(self.data)}\n"
                f"市场信息：{market_info}\n"
                f"现金流警告：还能撑{seasons_left}季度\n"
                f"核心规则：最终以所有者权益高低决定胜负，贷款有利息风险。\n\n"
                f"请给出：\n"
                f"1. 广告费建议金额及理由\n"
                f"2. 是否贷款，贷多少\n"
                f"3. 生产线调整建议\n"
                f"4. 研发投入建议\n"
                f"5. 本轮最优先事项"
            )

            response = client.chat.completions.create(
                model="qwen3-vl:8b", # --- 修改这里：确保模型名正确 ---
                messages=[{"role": "user", "content": prompt}],
                timeout=180
            )
            advice = response.choices[0].message.content
            
            # 记录历史
            self.history.append({
                "轮次": self.round,
                "市场": market_info,
                "权益": self.data["所有者权益"]
            })
            self.round += 1
            
            return status_text + warning_text + "\nAI建议：\n" + advice
            
        except Exception as e:
            return f"\n❌ 无法连接AI模型：{str(e)}\n请确保 Ollama 已运行，或检查网络设置。"

# ==================== 2. 桌面 GUI 界面 (使用 Tkinter 替换 ipywidgets) ====================
class ERPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ERP 沙盘 AI 助手 v1.0")
        self.root.geometry("800x600")
        self.agent = ERPAgent() # 实例化核心逻辑

        # --- 状态栏 ---
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = tk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # --- 聊天显示区 ---
        self.chat_area = scrolledtext.ScrolledText(root, state='disabled', wrap=tk.WORD)
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # --- 输入与按钮区 ---
        input_frame = Frame(root)
        input_frame.pack(padx=10, pady=5, fill=tk.X)

        self.input_box = scrolledtext.ScrolledText(input_frame, height=3)
        self.input_box.pack(side=tk.LEFT, fill=tk.X, expand=True)

        send_btn = Button(input_frame, text="🚀 发送 (Enter)", command=self.send_message)
        send_btn.pack(side=tk.RIGHT, padx=5)

        # 绑定回车键发送 (Shift+Enter 换行)
        self.input_box.bind("<Return>", lambda e: self.send_message() if not e.state & 0x1 else None)

        self.print_message("欢迎使用 ERP AI 助手！\n"
                          "💡 提示：输入市场信息（如'需求旺盛，对手广告费高'），点击发送获取建议。\n"
                          "----------------------------------------")

    def print_message(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(END, message + "\n\n")
        self.chat_area.config(state='disabled')
        self.chat_area.see(END)

    def send_message(self):
        user_text = self.input_box.get("1.0", END).strip()
        if not user_text:
            return

        # 显示用户输入
        self.print_message(f"👤 我: {user_text}")
        self.input_box.delete("1.0", END)
        self.status_var.set("AI 正在思考... (这可能需要 10-30 秒)")

        # 开启新线程防止界面卡死
        thread = threading.Thread(target=self.process_ai_response, args=(user_text,))
        thread.start()

    def process_ai_response(self, market_info):
        try:
            # 调用核心逻辑获取建议
            response = self.agent.get_strategic_advice(market_info)
            # 在主线程更新界面
            self.root.after(0, lambda: self.print_message(f"🤖 AI: {response}"))
        except Exception as e:
            self.root.after(0, lambda: self.print_message(f"❌ 错误: {e}"))
        finally:
            self.root.after(0, lambda: self.status_var.set("就绪"))

# ==================== 3. 启动程序 ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = ERPApp(root)
    root.mainloop()