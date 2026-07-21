from knowledge.knowledge_base import GameKnowledgeBase


knowledge = GameKnowledgeBase("data").load()

print("Game Knowledge Base Demo")
print("summary =", knowledge.summary())
print()
print("Interrupt Events")

for event in knowledge.events.interrupt_events():
    print(
        f"- {event['event_id']}: "
        f"priority={event['priority']}, "
        f"actions={[action['type'] for action in event['actions']]}"
    )

print()
print("Excluded systems: hot air balloon, train")
