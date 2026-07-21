import customtkinter as ctk
class DashboardPage(ctk.CTkFrame):
    def __init__(self,parent):
        super().__init__(parent,fg_color="transparent");ctk.CTkLabel(self,text="控制中心",font=ctk.CTkFont(family="Microsoft JhengHei",size=28,weight="bold")).pack(anchor="w",padx=28,pady=(28,10));ctk.CTkLabel(self,text="Inventory Vision + GameData v2 + Craft Planner",text_color="gray70").pack(anchor="w",padx=28)
