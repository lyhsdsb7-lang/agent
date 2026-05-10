import customtkinter as ctk

from erp_agent_ui import ERPApp


def main():
    root = ctk.CTk()
    ERPApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
