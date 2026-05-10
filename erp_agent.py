import tkinter as tk

from erp_agent_ui import ERPApp


def main():
    root = tk.Tk()
    ERPApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
