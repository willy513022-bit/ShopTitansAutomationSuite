import customtkinter as ctk
from gui.pages.dashboard import DashboardPage

class ShopTitansApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("Shop Titans Automation Suite")
        self.geometry("1180x760")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        ctk.CTkLabel(
            self.sidebar,
            text="Shop Titans\nAutomation Suite",
            justify="left",
            font=ctk.CTkFont(family="Microsoft JhengHei", size=20, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(28, 34))
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        self.add_sidebar_button("控制中心", self.show_dashboard)
        for text in ["製作", "販售", "市場", "資料庫", "執行紀錄", "設定"]:
            self.add_sidebar_button(text, lambda name=text: self.show_placeholder(name))
        self.show_dashboard()

    def add_sidebar_button(self, text, command):
        ctk.CTkButton(self.sidebar, text=text, anchor="w", height=42, corner_radius=8, command=command).pack(fill="x", padx=14, pady=5)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_content()
        DashboardPage(self.content).grid(row=0, column=0, sticky="nsew")

    def show_placeholder(self, page_name):
        self.clear_content()
        frame = ctk.CTkFrame(self.content, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(frame, text=page_name, font=ctk.CTkFont(family="Microsoft JhengHei", size=28, weight="bold")).pack(anchor="w", padx=28, pady=(28, 10))

def start_ctk_app():
    ShopTitansApp().mainloop()
