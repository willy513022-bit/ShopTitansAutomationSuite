from core import *

def main():
    strategy=Strategy(mode=StrategyMode.EVENT,event_priority_enabled=True,lost_city_mode=LostCityMode.FULL,reserve_collection_parties=1,planner_modifiers={'lostcity':10},confidence_weight=2)
    decisions=[
        PlannerDecision('Collection','DONATE_ITEM',96,'Legendary item can be donated',.99,rule_ids=('COL-001',)),
        PlannerDecision('LostCity','START_BOSS_QUEST',90,'Boss first-clear is available',1.0,task_lock=True,interruptible=False,rule_ids=('LC-001','LC-003')),
        PlannerDecision('Craft','CRAFT_ITEM',72,'Two crafting slots are empty',.95),
        PlannerDecision('Customer','SELL_ITEM',55,'Customer can wait and will not leave automatically',1.0,rule_ids=('CUS-001','CUS-002'))]
    result=Scheduler().select(decisions,strategy)
    logger=DecisionLogger('logs/decision_history.jsonl'); logger.print_console(1,result,strategy); logger.append_jsonl(1,result,strategy)
if __name__=='__main__': main()
