from models.quality import Quality
from vision.inventory_overlap import InventoryCardKey,InventoryOverlapMatcher
def key(name,q):return InventoryCardKey(name.lower().replace(" ",""),name,Quality.NORMAL,q)
if __name__=="__main__":
    previous=[key("Imbued Blade",3),key("Studded Gloves",2),key("Morning Star",1),key("Morning Star",1),key("Cutlass",2),key("Morning Star",1),key("Magic Potion",1),key("Magic Potion",1),key("Magic Potion",1)]
    current=[key("Cutlass",2),key("Morning Star",1),key("Magic Potion",1),key("Magic Potion",1),key("Magic Potion",1),key("Shiv",4),key("Iron Ring",2),key("Wooden Shield",1)]
    result=InventoryOverlapMatcher().find_overlap(previous,current);print("重疊數量：",result.overlap_count)
    for item in result.new_items:print(item.item_name,item.quality.value,item.quantity)
