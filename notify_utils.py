import json

NOTIFS_PATH = "Your way to json with ppl to send notifs"
STOCK_PATH = "Your way to json with stock"

EVENT_ITEMS = {"Nectarine", "Hive", "Honey Sprinkler", "Bee Egg"}

async def notify_users_if_fruits_in_stock(bot):
    with open(NOTIFS_PATH, encoding="utf-8") as f:
        users = json.load(f)
    with open(STOCK_PATH, encoding="utf-8") as f:
        stocks = json.load(f)
    available = set()
    for shop in stocks:
        if shop["shop"] != "HONEY STOCK":
            for item in shop["items"]:
                if int(item.get("amount", 0)) > 0:
                    available.add(item["name"])
    for u in users:
        notify = [fruit for fruit in u.get("fruits_to_send_dm", []) if fruit not in EVENT_ITEMS and fruit in available]
        if notify:
            text = "В наличии: " + ", ".join(notify)
            try:
                await bot.send_message(u["user_id"], text)
            except Exception as e:
                print(f"Ошибка отправки {u['user_id']}: {e}")

async def notify_users_if_event_items_in_stock(bot):
    with open(NOTIFS_PATH, encoding="utf-8") as f:
        users = json.load(f)
    with open(STOCK_PATH, encoding="utf-8") as f:
        stocks = json.load(f)
    available = set()
    for shop in stocks:
        if shop["shop"] == "HONEY STOCK":
            for item in shop["items"]:
                if int(item.get("amount", 0)) > 0:
                    available.add(item["name"])
    for u in users:
        notify = [fruit for fruit in u.get("fruits_to_send_dm", []) if fruit in EVENT_ITEMS and fruit in available]
        if notify:
            text = "Ивент-магазин: " + ", ".join(notify)
            try:
                await bot.send_message(u["user_id"], text)
            except Exception as e:
                print(f"Ошибка отправки {u['user_id']}: {e}")
