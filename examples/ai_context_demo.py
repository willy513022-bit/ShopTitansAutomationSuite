from core.ai_context import AIContext
ctx=AIContext(screen_state="TOWN",settings={"auto_craft":True},statistics={"quests":12})
print("AIContext Demo")
print(ctx.summary())
