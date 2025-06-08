import requests
from bs4 import BeautifulSoup
import json

# Список всех интересующих предметов (для справки)
all_items = [
    "Watering Can", "Trowel", "Recall Wrench", "Basic Sprinkler", "Advanced Sprinkler", "Godly Sprinkler",
    "Lightning rod", "Master Sprinkler", "Favorite Tool", "Harvest Tool", "Flower Seed Pack", "Nectarine",
    "Hive Fruit", "Honey Sprinkler", "Bee egg", "Bee crate", "Honey comb", "Bee chair", "Honey Torch", "Honey Walkway", "Lavender", "Nectar Staff", "Ember Lily", "Nectarshade"
]

# Соответствие эмоджи
item_emojis = {
    "Watering Can": "💧",
    "Trowel": "🪴",
    "Recall Wrench": "🔧",
    "Basic Sprinkler": "🚿",
    "Advanced Sprinkler": "💦",
    "Godly Sprinkler": "✨",
    "Lightning rod": "⚡",
    "Master Sprinkler": "🌊",
    "Favorite Tool": "🛠️",
    "Harvest Tool": "🔨",
    "Flower Seed Pack": "🌸",
    "Nectarine": "🍑",
    "Hive Fruit": "🍯",
    "Honey Sprinkler": "🍯🚿",
    "Bee egg": "🐝🥚",
    "Bee Сrate": "📦🐝",
    "Honey Сomb": "🍯🧩",
    "Bee Сhair": "🪑🐝",
    "Honey Torch": "🔥🍯",
    "Honey Walkway": "🚶🍯",
    "Apple": "🍎",
    "Orange": "🍊",
    "Banana": "🍌",
    "Strawberry": "🍓",
    "Grape": "🍇",
    "Watermelon": "🍉",
    "Mango": "🥭",
    "Pineapple": "🍍",
    "Lemon": "🍋",
    "Blueberry": "🫐",
    "Coconut": "🥥",
    "Dragon Fruit": "🐉🍈",
    "Nectarine": "🍑",
    "Cacao": "🍫",
    "Pumpkin": "🎃",
    "Carrot": "🥕",
    "Corn": "🌽",
    "Tomato": "🍅",
    "Cucumber": "🥒",
    "Mushroom": "🍄",
    "Pepper": "🫑",
    "Bamboo": "🎋",
    "Beanstalk": "🫘",
    "Daffodil": "🌼",
    "Tulip": "🌷",
    "Cactus": "🌵",
    "Nectar staff": "🍯⚕",
    "Pollen Radar": "📻",
    "Lavender": "🌷",
    "Nectarshade": "🍯",
    "Ember Lily": "",
    "Friendship pot": "🥣👫"
    # Добавь еще при необходимости
}

url = "https://vulcanvalues.com/grow-a-garden/stock"
response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

shops = []
grid_blocks = soup.select("div.grid > div")

for block in grid_blocks:
    shop = {}
    title_tag = block.find("h2")
    if not title_tag:
        continue
    shop_name = title_tag.get_text(strip=True)
    shop["shop"] = shop_name
    shop["items"] = []

    ul = block.find("ul")
    if not ul:
        continue
    for li in ul.find_all("li"):
        span = li.find("span")
        if not span:
            continue
        name_part = span.find(text=True, recursive=False)
        qty_part = span.find("span", class_="text-gray-400")
        if name_part and qty_part:
            name = name_part.strip()
            qty = qty_part.get_text().strip().replace('x', '')
            emoji = item_emojis.get(name, "")  # Пусто если эмоджи не задано
            shop["items"].append({
                "name": name,
                "amount": int(qty) if qty.isdigit() else qty,
                "emoji": emoji
            })
    shops.append(shop)

with open("Your way to stock json", "w", encoding="utf-8") as f:
    json.dump(shops, f, ensure_ascii=False, indent=2)

print(f"Обновлено: {len(shops)} магазинов, файл all_stocks.json с эмоджи")
