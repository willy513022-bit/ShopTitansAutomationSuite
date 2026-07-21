from models.craft import StockTarget
from models.inventory import InventoryItemKey,InventorySnapshot,InventoryStack
from models.quality import Quality
from services.craft_planner import CraftPlanner
if __name__=="__main__":
    snapshot=InventorySnapshot((InventoryStack(InventoryItemKey("shortsword",Quality.NORMAL),"Squire Sword",20),InventoryStack(InventoryItemKey("cutlass",Quality.NORMAL),"Cutlass",0)))
    targets=[StockTarget("shortsword",20,Quality.NORMAL,5,10),StockTarget("cutlass",20,Quality.NORMAL,0,5)]
    for d in CraftPlanner().build_demands(snapshot,targets):print(f"{d.item_name:<20} required={d.required_quantity:<3} current={d.current_quantity:<3} shortage={d.shortage:<3} precraft={d.precraft_demand}")
