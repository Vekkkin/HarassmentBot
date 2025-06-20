import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    InputMediaPhoto,
)
from aiogram.filters import Command
from aiohttp import web

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    exit("Error: BOT_TOKEN not set")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

ADMIN_IDS = [1864436178, 994450603]

AVITO_LINKS = {
    "Футболка": "https://www.avito.ru/...",
    "Дюраг": "https://www.avito.ru/...",
    "Гольфы": "https://www.avito.ru/..."
}

PRODUCTS = {
    "Футболка": {
        "photos": [
            "https://i.postimg.cc/...",
            "https://i.postimg.cc/..."
        ],
        "text": "Описание футболки..."
    },
    "Дюраг": {
        "photos": [
            "https://i.postimg.cc/...",
            "https://i.postimg.cc/..."
        ],
        "text": "Описание дюрага..."
    },
    "Гольфы": {
        "photos": [
            "https://i.postimg.cc/...",
            "https://i.postimg.cc/..."
        ],
        "text": "Описание гольфов..."
    }
}

MANIFESTO_TEXT = (
    "HARASSMENT — это не бренд, а манифест..."
)

user_data = {}

def main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Футболка "ANTAGONIST"', callback_data='product_Футболка')],
        [InlineKeyboardButton(text='Дюраг "IRON SKIN"', callback_data='product_Дюраг')],
        [InlineKeyboardButton(text='Гольфы "LEATHER KNEE SOCKS"', callback_data='product_Гольфы')],
    ])

def product_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Заказать", callback_data="order")],
        [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")],
    ])

def phone_request_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отправить номер телефона", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(text=MANIFESTO_TEXT, reply_markup=main_menu_keyboard())

@dp.callback_query(lambda c: c.data == "main_menu")
async def main_menu_handler(callback: CallbackQuery):
    await callback.message.edit_text(MANIFESTO_TEXT, reply_markup=main_menu_keyboard())
    await callback.answer()

@dp.callback_query(lambda c: c.data and c.data.startswith("product_"))
async def product_handler(callback: CallbackQuery):
    product_name = callback.data.split("_")[1]
    user_data[callback.from_user.id] = product_name
    product = PRODUCTS[product_name]
    media = [InputMediaPhoto(media=url) for url in product["photos"]]
    await bot.send_media_group(chat_id=callback.from_user.id, media=media)
    await bot.send_message(callback.from_user.id, product["text"], reply_markup=product_menu_keyboard())
    await callback.answer()

@dp.callback_query(lambda c: c.data == "order")
async def order_handler(callback: CallbackQuery):
    await callback.message.answer("Пожалуйста, отправьте свой номер телефона:", reply_markup=phone_request_keyboard())
    await callback.answer()

@dp.message(lambda m: m.contact is not None)
async def contact_handler(message: Message):
    user_id = message.from_user.id
    phone = message.contact.phone_number
    username = message.from_user.username or "не задан"
    product_name = user_data.get(user_id, "Неизвестный товар")
    admin_text = f"Новый заказ!
@{username}
Телефон: {phone}
Товар: {product_name}"
    for admin_id in ADMIN_IDS:
        await bot.send_message(chat_id=admin_id, text=admin_text)
    avito_link = AVITO_LINKS.get(product_name)
    if avito_link:
        await message.answer(f"Вот ссылка на оплату:
{avito_link}")
    else:
        await message.answer("Мы свяжемся с вами.")
    await message.answer("Вернуться в меню", reply_markup=main_menu_keyboard())

@dp.message()
async def fallback(message: Message):
    await message.answer("Пожалуйста, используйте меню или команду /start.", reply_markup=main_menu_keyboard())

# --- Web Server для Render ---
async def handle_root(request):
    return web.Response(text="OK")

async def start_webserver():
    app = web.Application()
    app.add_routes([web.get("/", handle_root)])
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    while True:
        await asyncio.sleep(3600)

async def start_bot():
    await dp.start_polling(bot)

async def main():
    await asyncio.gather(
        start_webserver(),
        start_bot()
    )

if __name__ == "__main__":
    asyncio.run(main())
