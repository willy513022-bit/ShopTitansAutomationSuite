from vision.inventory_full_scanner import InventoryFullScanner

if __name__ == "__main__":
    print("Inventory Full Scanner 測試")
    print("=" * 70)
    try:
        summary = InventoryFullScanner(maximum_pages=150, no_new_page_limit=3).scan()
    except Exception as error:
        print("掃描失敗：", error)
    else:
        print("\n最終庫存")
        print("=" * 70)
        for item in summary.items:
            print(f"{item.item_name:<30} {item.quality.value:<10} × {item.quantity}")
        print("掃描頁數：", summary.pages_scanned)
        print("有效卡片：", summary.cards_scanned)
        print("物品種類/品質組合：", len(summary.items))
