import asyncio
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import json
import os

from background_tasts import periodic_notify_task_regular, periodic_notify_task_event

TOKEN = "Your token here"

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

NOTIFS_PATH = "Your way here"
STOCK_PATH = "Your way here"

class UserStatment(StatesGroup):
    just_started = State()
    waiting_for_what_fruit_to_notify = State()
    waiting_for_what_gear_to_notify = State()
    waiting_for_what_event_item_to_notify = State()
    waiting_for_what_stock_to_get = State()
    waiting_for_what_to_subscribe_fruit_or_gear_or_event = State()

async def clear_user_fruits(user_id: int, filename=NOTIFS_PATH):
    user_id = str(user_id)
    if not os.path.exists(filename):
        return False
    with open(filename, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception:
            return False
    changed = False
    for entry in data:
        if entry.get("user_id") == user_id:
            entry["fruits_to_send_dm"] = []
            changed = True
    if changed:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    return changed

async def save_user_subscription(user_id: int, fruit, filename=NOTIFS_PATH):
    user_id = str(user_id)
    data = []
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = []
    updated = False
    for entry in data:
        if entry.get("user_id") == user_id:
            if fruit not in entry.get("fruits_to_send_dm", []):
                if not isinstance(entry["fruits_to_send_dm"], list):
                    entry["fruits_to_send_dm"] = [entry["fruits_to_send_dm"]]
                entry["fruits_to_send_dm"].append(fruit)
            updated = True
            break
    if not updated:
        data.append({
            "user_id": user_id,
            "sended_or_not": "False",
            "fruits_to_send_dm": [fruit]
        })
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def get_stock(shop_name):
    try:
        with open(STOCK_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        awd = ""
        for shop in data:
            if shop["shop"] == shop_name:
                for item in shop['items']:
                    awd += "  -  " + f"{item['emoji']}{item['name']}{item['emoji']} {item['amount']}\n"
        return awd if awd else "Нет данных."
    except Exception as e:
        return f"⚠️ Произошла ошибка: {e}"

def get_main_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="⚙Настройки⚙")
    builder.button(text="👀Посмотреть стоки👀")
    return builder.as_markup(resize_keyboard=True)

def get_stock_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🌱Узнать сток семян.🌱")
    builder.button(text="🔧Узнать сток предметов.🔧")
    builder.button(text="📅Узнать сток ивента.📅")
    builder.button(text="🥚Узнать сток яиц.🥚")
    builder.button(text="💄Узнать сток украшений.💄")
    builder.button(text="⬅ Назад")
    return builder.as_markup(resize_keyboard=True)

def get_notify_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🍊Уведомление на сток фрукта дракона.🐉")
    builder.button(text="🥭Уведомление на сток манго.🥭")
    builder.button(text="🍇Уведомление на сток винограда.🍇")
    builder.button(text="🍄Уведомление на сток грибов.🍄")
    builder.button(text="🌶Уведомление на сток перца.🌶")
    builder.button(text="☕Уведомление на сток какао.☕")
    builder.button(text="🥫Уведомление на сток бобов.🥫")
    builder.button(text="🌺Ember lily.🔥")
    builder.button(text="⬅ Назад")
    return builder.as_markup(resize_keyboard=True)

def get_event_notify_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🍑Нектарин🍑")
    builder.button(text="🏠Фрукт улей🐝")
    builder.button(text="🍯Медовый разбрызгиватель💦")
    builder.button(text="🐝Bee egg🥚"),
    builder.button(text="🍯Pollen Radar📻"),
    builder.button(text="⚕Nectar Staff🍯")
    builder.button(text="⬅ Назад")
    return builder.as_markup(resize_keyboard=True)

def get_gear_notify_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🚿Godly sprinkler🎇")
    builder.button(text="🚿Master sprinkler⚙")
    builder.button(text="⚡Lightning rod⚡")
    builder.button(text="👫Friendship pot👫")
    builder.button(text="⬅ Назад")
    return builder.as_markup(resize_keyboard=True)

def get_notifies_keyboard() -> ReplyKeyboardBuilder:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🏪Уведомления на Gear shop⚙")
    builder.button(text="📅Уведомления на ивент сток🍯")
    builder.button(text="🍇Уведомления на сток семян🏪")
    builder.button(text="⬅ Назад")
    builder.button(text="🧼Убрать уведомления на всё.🧼")
    return builder.as_markup(resize_keyboard=True)

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! Я бот и я могу подсказать тебе какой сейчас сток чего либо в игре Grow a garden!"
    )
    await message.answer("Выберите опцию:", reply_markup=get_main_keyboard())
    await state.set_state(UserStatment.just_started)

@router.message(StateFilter(UserStatment.just_started), F.text == "⚙Настройки⚙")
async def handle_settings(message: types.Message, state: FSMContext):
    await message.answer(
        "Здесь вы можете выбрать на что поставить уведомления",
        reply_markup=get_notifies_keyboard()
    )
    await state.set_state(UserStatment.waiting_for_what_to_subscribe_fruit_or_gear_or_event)

@router.message(StateFilter(UserStatment.waiting_for_what_to_subscribe_fruit_or_gear_or_event), F.text == "🧼Убрать уведомления на всё.🧼")
async def handle_clear_notifs(message: types.Message, state: FSMContext):
    await clear_user_fruits(message.from_user.id)
    await message.answer("Уведомления очищены.", reply_markup=get_notifies_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_fruit_to_notify), F.text == "🍊Уведомление на сток фрукта дракона.🐉")
async def handle_dragon(message: types.Message, state: FSMContext):
    await save_user_subscription(message.from_user.id, "Dragon Fruit")
    await message.answer("Уведомление на фрукт дракона добавлено!", reply_markup=get_notify_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_fruit_to_notify), F.text == "🥭Уведомление на сток манго.🥭")
async def handle_mango(message: types.Message, state: FSMContext):
    await save_user_subscription(message.from_user.id, "Mango")
    await message.answer("Уведомление на манго добавлено!", reply_markup=get_notify_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_fruit_to_notify), F.text == "🍇Уведомление на сток винограда.🍇")
async def handle_grape(message: types.Message, state: FSMContext):
    await save_user_subscription(message.from_user.id, "Grape")
    await message.answer("Уведомление на виноград добавлено!", reply_markup=get_notify_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_fruit_to_notify), F.text == "🍄Уведомление на сток грибов.🍄")
async def handle_mushroom(message: types.Message, state: FSMContext):
    await save_user_subscription(message.from_user.id, "Mushroom")
    await message.answer("Уведомление на гриб добавлено!", reply_markup=get_notify_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_fruit_to_notify), F.text == "🌶Уведомление на сток перца.🌶")
async def handle_pepper(message: types.Message, state: FSMContext):
    await save_user_subscription(message.from_user.id, "Pepper")
    await message.answer("Уведомление на перец добавлено!", reply_markup=get_notify_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_fruit_to_notify), F.text == "☕Уведомление на сток какао.☕")
async def handle_cacao(message: types.Message, state: FSMContext):
    await save_user_subscription(message.from_user.id, "Cacao")
    await message.answer("Уведомление на какао добавлено!", reply_markup=get_notify_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_fruit_to_notify), F.text == "🥫Уведомление на сток бобов.🥫")
async def handle_beanstalk(message: types.Message, state: FSMContext):
    await save_user_subscription(message.from_user.id, "Beanstalk")
    await message.answer("Уведомление на боб добавлено!", reply_markup=get_notify_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_fruit_to_notify), F.text == "🌺Ember lily.🔥")
async def handle_beanstalk(message: types.Message, state: FSMContext):
    await save_user_subscription(message.from_user.id, "Ember lily")
    await message.answer("Уведомление на Ember lily добавлено!", reply_markup=get_notify_keyboard()) 

@router.message(StateFilter(UserStatment.just_started), F.text == "👀Посмотреть стоки👀")
async def handle_view_stock(message: types.Message, state: FSMContext):
    await message.answer("Выберите какой сток показать:", reply_markup=get_stock_keyboard())
    await state.set_state(UserStatment.waiting_for_what_stock_to_get)

@router.message(StateFilter(UserStatment.waiting_for_what_stock_to_get), F.text == "🌱Узнать сток семян.🌱")
async def view_seed_stock(message: types.Message, state: FSMContext):
    text = await get_stock("SEEDS STOCK")
    await message.answer(text, reply_markup=get_stock_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_stock_to_get), F.text == "🔧Узнать сток предметов.🔧")
async def view_gear_stock(message: types.Message, state: FSMContext):
    text = await get_stock("GEAR STOCK")
    await message.answer(text, reply_markup=get_stock_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_stock_to_get), F.text == "📅Узнать сток ивента.📅")
async def view_event_stock(message: types.Message, state: FSMContext):
    text = await get_stock("HONEY STOCK")
    await message.answer(text, reply_markup=get_stock_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_stock_to_get), F.text == "🥚Узнать сток яиц.🥚")
async def view_egg_stock(message: types.Message, state: FSMContext):
    text = await get_stock("EGG STOCK")
    await message.answer(text, reply_markup=get_stock_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_stock_to_get), F.text == "💄Узнать сток украшений.💄")
async def view_cosmetic_stock(message: types.Message, state: FSMContext):
    text = await get_stock("COSMETICS STOCK")
    await message.answer(text, reply_markup=get_stock_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_to_subscribe_fruit_or_gear_or_event), F.text == "🍇Уведомления на сток семян🏪")
async def set_seed_subscribe(message: types.Message, state: FSMContext):
    text = "Здесь вы можете поставить уведомления на сток семян соотвественно только дорогих."
    await message.answer(text, reply_markup=get_notify_keyboard())
    await state.set_state(UserStatment.waiting_for_what_fruit_to_notify)

@router.message(StateFilter(UserStatment.waiting_for_what_to_subscribe_fruit_or_gear_or_event), F.text == "🏪Уведомления на Gear shop⚙")
async def set_gear_subscribe(message: types.Message, state: FSMContext):
    text = "Здесь вы можете поставить уведомления на сток предметов соотвественно только дорогих."
    await message.answer(text, reply_markup=get_gear_notify_keyboard())
    await state.set_state(UserStatment.waiting_for_what_gear_to_notify)

@router.message(StateFilter(UserStatment.waiting_for_what_to_subscribe_fruit_or_gear_or_event), F.text == "📅Уведомления на ивент сток🍯")
async def set_event_subscribe(message: types.Message, state: FSMContext):
    text = "Здесь вы можете поставить уведомления на сток ивент магазина соотвественно только дорогих."
    await message.answer(text, reply_markup=get_event_notify_keyboard())
    await state.set_state(UserStatment.waiting_for_what_event_item_to_notify)

@router.message(StateFilter(UserStatment.waiting_for_what_event_item_to_notify), F.text == "🍑Нектарин🍑")
async def set_nectarine_subscribe(message: types.Message, state: FSMContext):
    text = "Установлено уведомление на нектарин."
    await save_user_subscription(message.from_user.id, "Nectarine")
    await message.answer(text, reply_markup=get_event_notify_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_event_item_to_notify), F.text == "🏠Фрукт улей🐝")
async def set_hive_subscribe(message: types.Message, state: FSMContext):
    text = "Установлено уведомление на улей."
    await save_user_subscription(message.from_user.id, "Hive")
    await message.answer(text, reply_markup=get_event_notify_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_event_item_to_notify), F.text == "🍯Медовый разбрызгиватель💦")
async def set_hive_subscribe(message: types.Message, state: FSMContext):
    text = "Установлено уведомление на медовый разбрызгиватель."
    await save_user_subscription(message.from_user.id, "Honey Sprinkler")
    await message.answer(text, reply_markup=get_event_notify_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_event_item_to_notify), F.text == "🐝Bee egg🥚")
async def set_hive_subscribe(message: types.Message, state: FSMContext):
    text = "Установлено уведомление на пчелиное яйцо."
    await save_user_subscription(message.from_user.id, "Bee Egg")
    await message.answer(text, reply_markup=get_event_notify_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_event_item_to_notify), F.text == "🍯Pollen Radar📻")
async def set_hive_subscribe(message: types.Message, state: FSMContext):
    text = "Установлено уведомление на Pollen Radar."
    await save_user_subscription(message.from_user.id, "Pollen Radar")
    await message.answer(text, reply_markup=get_event_notify_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_event_item_to_notify), F.text == "⚕Nectar Staff🍯")
async def set_hive_subscribe(message: types.Message, state: FSMContext):
    text = "Установлено уведомление на Nectar Staff."
    await save_user_subscription(message.from_user.id, "Nectar Staff")
    await message.answer(text, reply_markup=get_event_notify_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_gear_to_notify), F.text == "🚿Godly sprinkler🎇")
async def set_hive_subscribe(message: types.Message, state: FSMContext):
    text = "Установлено уведомление на божественный разбрызгиватель."
    await save_user_subscription(message.from_user.id, "Godly Sprinkler")
    await message.answer(text, reply_markup=get_gear_notify_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_gear_to_notify), F.text == "🚿Master sprinkler⚙")
async def set_hive_subscribe(message: types.Message, state: FSMContext):
    text = "Установлено уведомление на мастер разбрызгиватель."
    await save_user_subscription(message.from_user.id, "Master Sprinkler")
    await message.answer(text, reply_markup=get_gear_notify_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_gear_to_notify), F.text == "⚡Lightning rod⚡")
async def set_hive_subscribe(message: types.Message, state: FSMContext):
    text = "Установлено уведомление на громоотвод."
    await save_user_subscription(message.from_user.id, "Lightning Rod")
    await message.answer(text, reply_markup=get_gear_notify_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_gear_to_notify), F.text == "👫Friendship pot👫")
async def set_hive_subscribe(message: types.Message, state: FSMContext):
    text = "Установлено уведомление на Friendship pot."
    await save_user_subscription(message.from_user.id, "Friendship pot")
    await message.answer(text, reply_markup=get_gear_notify_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_event_item_to_notify), F.text == "⬅ Назад")
async def back_to_menu(message: types.Message, state: FSMContext):
    await state.set_state(UserStatment.waiting_for_what_to_subscribe_fruit_or_gear_or_event)
    await message.answer("Уведомления.", reply_markup=get_notifies_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_gear_to_notify), F.text == "⬅ Назад")
async def back_to_menu(message: types.Message, state: FSMContext):
    await state.set_state(UserStatment.waiting_for_what_to_subscribe_fruit_or_gear_or_event)
    await message.answer("Уведомления.", reply_markup=get_notifies_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_to_subscribe_fruit_or_gear_or_event), F.text == "⬅ Назад")
async def back_to_menu(message: types.Message, state: FSMContext):
    await state.set_state(UserStatment.just_started)
    await message.answer("Уведомления.", reply_markup=get_main_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_fruit_to_notify), F.text == "⬅ Назад")
async def back_to_menu(message: types.Message, state: FSMContext):
    await state.set_state(UserStatment.waiting_for_what_to_subscribe_fruit_or_gear_or_event)
    await message.answer("Уведомления", reply_markup=get_notifies_keyboard())

@router.message(StateFilter(UserStatment.waiting_for_what_stock_to_get), F.text == "⬅ Назад")
async def back_to_menu(message: types.Message, state: FSMContext):
    await state.set_state(UserStatment.just_started)
    await message.answer("Главное меню", reply_markup=get_main_keyboard())


async def main():
    dp.include_router(router)
    # Запуск двух фоновых задач
    asyncio.create_task(periodic_notify_task_regular(bot, interval=5))
    asyncio.create_task(periodic_notify_task_event(bot))
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
