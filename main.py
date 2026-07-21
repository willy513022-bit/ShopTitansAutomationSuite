from agent import ShopTitansAgent, WorldState, ScreenState, production_tasks

state = WorldState(
    screen=ScreenState("PRODUCTION", 0.98),
    queue_remaining=1,
    ready_count=3,
    customer_count=4,
    energy=5428,
    gold=2_340_000_000,
    guild_objective="CRAFT_TIERS",
)

result = ShopTitansAgent().run_once(state, production_tasks())
print(result)
