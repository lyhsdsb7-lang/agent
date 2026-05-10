import threading
import tkinter as tk
from tkinter import Button, END, Frame, scrolledtext

from erp_agent_core import ERPAgent


class ERPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ERP 沙盘 AI 助手 v1.0")
        self.root.geometry("800x600")
        self.agent = ERPAgent()
        self.is_busy = False

        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = tk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.chat_area = scrolledtext.ScrolledText(root, state="disabled", wrap=tk.WORD)
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        input_frame = Frame(root)
        input_frame.pack(padx=10, pady=5, fill=tk.X)

        self.input_box = scrolledtext.ScrolledText(input_frame, height=3)
        self.input_box.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.send_btn = Button(input_frame, text="🚀 发送 (Enter)", command=self.send_message)
        self.send_btn.pack(side=tk.RIGHT, padx=5)

        self.input_box.bind("<Return>", self.handle_return)

        self.print_message(
            "欢迎使用 ERP AI 助手！\n"
            "💡 提示：输入市场信息（如'需求旺盛，对手广告费高'），点击发送获取建议。\n"
            "----------------------------------------"
        )

    def handle_return(self, event):
        if event.state & 0x1:
            return None
        self.send_message()
        return "break"

    def print_message(self, message):
        self.chat_area.config(state="normal")
        self.chat_area.insert(END, message + "\n\n")
        self.chat_area.config(state="disabled")
        self.chat_area.see(END)

    def set_busy(self, is_busy: bool):
        self.is_busy = is_busy
        self.send_btn.config(state=tk.DISABLED if is_busy else tk.NORMAL)
        self.status_var.set("AI 正在思考... (这可能需要 10-30 秒)" if is_busy else "就绪")

    def send_message(self):
        if self.is_busy:
            return

        user_text = self.input_box.get("1.0", END).strip()
        if not user_text:
            return

        self.print_message(f"👤 我: {user_text}")
        self.input_box.delete("1.0", END)
        self.set_busy(True)

        thread = threading.Thread(target=self.process_ai_response, args=(user_text,), daemon=True)
        thread.start()

    def process_ai_response(self, market_info):
        try:
            response = self.agent.get_strategic_advice(market_info)
            self.root.after(0, lambda: self.print_message(f"🤖 AI: {response}"))
        except Exception as exc:
            self.root.after(0, lambda: self.print_message(f"❌ 错误: {exc}"))
        finally:
            self.root.after(0, lambda: self.set_busy(False))
