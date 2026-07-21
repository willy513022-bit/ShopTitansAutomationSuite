from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from .scheduler import SchedulerResult
from .strategy import Strategy

class DecisionLogger:
    def __init__(self,jsonl_path=None): self.path=Path(jsonl_path) if jsonl_path else None
    def format_console(self,loop_number:int,result:SchedulerResult,strategy:Strategy)->str:
        lines=['='*60,'Shop Titans AI Scheduler','='*60,f'Loop: {loop_number:03d}',f'Mode: {strategy.mode.value}',f'Lost City: {strategy.lost_city_mode.value}',f'Collection reserve: {strategy.effective_collection_reserve()}','-'*60]
        if not result.ranked: return '\n'.join(lines+['No eligible decisions.'])
        for i,s in enumerate(result.ranked,1):
            d=s.decision; lines += [f'#{i} {d.planner} -> {d.action}',f'Base: {d.base_priority:.2f} | Final: {s.final_score:.2f} | Confidence: {d.confidence:.2f}',f'Reason: {d.reason}']
            if d.rule_ids: lines.append('Rules: '+', '.join(d.rule_ids))
            lines.append('-'*60)
        w=result.winner; lines += ['WINNER',f'{w.decision.planner} -> {w.decision.action}',f'Final score: {w.final_score:.2f}',f'Reason: {w.decision.reason}','='*60]
        return '\n'.join(lines)
    def print_console(self,*args,**kwargs): print(self.format_console(*args,**kwargs))
    def append_jsonl(self,loop_number:int,result:SchedulerResult,strategy:Strategy):
        if not self.path: return
        self.path.parent.mkdir(parents=True,exist_ok=True)
        def s(x):
            if not x:return None
            d=x.decision
            return {'planner':d.planner,'action':d.action,'base_priority':d.base_priority,'final_score':x.final_score,'reason':d.reason,'confidence':d.confidence,'payload':dict(d.payload),'rule_ids':list(d.rule_ids),'modifiers':dict(x.modifiers)}
        rec={'timestamp':datetime.now().astimezone().isoformat(),'loop':loop_number,'mode':strategy.mode.value,'lost_city_mode':strategy.lost_city_mode.value,'winner':s(result.winner),'ranked':[s(x) for x in result.ranked]}
        with self.path.open('a',encoding='utf-8') as f:f.write(json.dumps(rec,ensure_ascii=False)+'\n')
