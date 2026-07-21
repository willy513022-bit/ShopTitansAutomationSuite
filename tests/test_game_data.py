from services.game_data_service import game_data_service

if __name__ == "__main__":
    print("GameData 測試")
    print("=" * 50)
    for item in game_data_service.get_all():
        print(item.item_id, item.name, item.tier, item.item_type)
