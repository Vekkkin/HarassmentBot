import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    InputMediaPhoto,
)
from aiogram.filters import Command, Text, ContentTypeFilter
from aiogram.types import ContentType
from aiohttp import web

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    exit("Error: BOT_TOKEN not set")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

ADMIN_IDS = [1864436178, 994450603]

AVITO_LINKS = {
    "Футболка": "https://www.avito.ru/moskva/odezhda_obuv_aksessuary/futbolka_antagonist_belaya_uniseks_print_hlopok_7422276736?utm_campaign=native&utm_medium=item_page_android&utm_source=soc_sharing_seller",
    "Дюраг": "https://www.avito.ru/moskva/odezhda_obuv_aksessuary/dyurag_kolchuga_iron_skin_organza_metall_7422565944?utm_campaign=native&utm_medium=item_page_android&utm_source=soc_sharing_seller",
    "Гольфы": "https://www.avito.ru/moskva/odezhda_obuv_aksessuary/golfy_leather_knee_socks_ekokozha_pod_zakaz_7422274055?utm_campaign=native&utm_medium=item_page_android&utm_source=soc_sharing_seller",
}

PRODUCTS = {
    "Футболка": {
        "photos": [
            "https://i.postimg.cc/8CQZSfsR/photo-5382065480904339414-y.jpg",
            "https://i.postimg.cc/rF7J1R1B/photo-5382065480904339415-y.jpg",
        ],
        "text": (
            "ANTAGONIST T-SHIRT\n\n"
            "БЕЛАЯ ФУТБОЛКА С ГРАФИЧЕСКИМ ПРИНТОМ\n\n"
            "100% хлопок.\n"
            "Плотность: 240 г/м²\n\n"
            "Цвет: Белый\n"
            "Стоимость: 2600₽\n"
            "Доставка: Авито доставка/СДЭК\n"
            "Самовывоз Москва (м.Селигерская/Речной вокзал)"
        ),
    },
    "Дюраг": {
        "photos": [
            "https://i.postimg.cc/VkBCJJDB/photo-5382065480904339417-y.jpg",
            "https://i.postimg.cc/7LHT0qRv/photo-5382065480904339416-y.jpg",
        ],
        "text": (
            'DURAG “IRON SKIN”\n\n'
            'ДЮРАГ-КОЛЬЧУГА ИЗ ОРГАНЗЫ С ДЕКОРАТИВНЫМИ КОЛЬЦАМИ.\n\n'
            'Гибрид ткани и металла.\n'
            'Унисекс.\n\n'
            'Цвет: Чёрный / Серебро\n'
            'Стоимость: 1500₽\n'
            'Доставка: Авито доставка/СДЭК\n'
            'Самовывоз Москва (м.Селигерская/Речной вокзал)'
        ),
    },
    "Гольфы": {
        "photos": [
            "https://i.postimg.cc/vmY0PgB3/photo-5379930577215550301-y.jpg",
            "https://i.postimg.cc/wvPFTwkG/photo-5382065480904339418-y.jpg",
        ],
        "text": (
            "LEATHER KNEE SOCKS\n\n"
            "ГОЛЬФЫ ИЗ МАТОВОЙ ЭКОКОЖИ.\n\n"
            "Изготавливается под заказ (3-5 дней)\n"
            "Возможность модификации\n\n"
            "Цвет: Чёрный\n"
            "Стоимость: 1500₽ (кастомные шипы +500₽)\n"
            "Доставка: Авито доставка/СДЭК\n"
            "Самовывоз Москва (м. Селигерская/Речной вокзал)"
        ),
    },
}

MANIFESTO_TEXT = (
    "HARASSMENT — это не бренд, а манифест. Наша философия строится на отрицании шаблонов, гедонизме и телесной свободе. "
    "Мы не украшаем реальность — мы её взламываем.\n\n"
    "DON’T IMITATE. DON’T OBEY. BEAT. FIGHT OUT. LOVE. ENJOY. DESTROY\n\n"
    "Мы создаём вещи для тех, кто отказывается подчиняться. Здесь нет массового, нет безопасного, нет просящегося в толпу. "
    "Каждая деталь — вызов.\n\n"
    "Носите это."
)

user_data = {}

def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Футболка "ANTAGONIST"', callback_data='product_Футболка')],
        [InlineKeyboardButton(text='Дюраг "IRON SKIN"', callback_data='product_Дюраг')],
        [InlineKeyboardButton(text='Гольфы "LEATHER KNEE SOCKS"', callback_data='product_Гольфы')],
    ])

def product_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Заказать", callback_data="order")],
        [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")],
    ])

def phone_request_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отправить номер телефона", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(text=MANIFESTO_TEXT, reply_markup=main_menu_keyboard())

@dp.callback_query(Text("main_menu"))
async def main_menu_handler(callback: CallbackQuery):
    await callback.message.edit_text(MANIFESTO_TEXT, reply_markup=main_menu_keyboard())
    await callback.answer()

@dp.callback_query(Text(startswith="product_"))
async def product_handler(callback: CallbackQuery):
    product_name = callback.data.split("_", 1)[1]
    user_data[callback.from_user.id] = product_name

    product = PRODUCTS.get(product_name)
    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return

    media = [InputMediaPhoto(media=url) for url in product["photos"]]
    await bot.send_media_group(chat_id=callback.from_user.id, media=media)
    await bot.send_message(callback.from_user.id, product["text"], reply_markup=product_menu_keyboard())
    await callback.answer()

@dp.callback_query(Text("order"))
async def order_handler(callback: CallbackQuery):
    await callback.message.answer(
        "Пожалуйста, отправьте свой номер телефона, используя кнопку ниже.\n\nПосле этого вы получите ссылку для заказа выбранного товара.",
        reply_markup=phone_request_keyboard())
    await callback.answer()

@dp.message(ContentTypeFilter(content_types=[ContentType.CONTACT]))
async def contact_handler(message: Message):
    user_id = message.from_user.id
    phone = message.contact.phone_number
    username = message.from_user.username or "не задан"
    product_name = user_data.get(user_id, "Неизвестный товар")

    admin_text = (
        f"Новый заказ!\n"
        f"Пользователь: @{username}\n"
        f"Телефон: {phone}\n"
        f"Товар: {product_name}"
    )

    for admin_id in ADMIN_IDS:
        await bot.send_message(chat_id=admin_id, text=admin_text)

    avito_link = AVITO_LINKS.get(product_name)
    if avito_link:
        await message.answer(f"Выбор сделан. Держите ссылку\n{avito_link}")
    else:
        await message.answer("Спасибо за заказ! Мы свяжемся с вами.")

    await message.answer("Ещё варианты?", reply_markup=main_menu_keyboard())

@dp.message()
async def fallback(message: Message):
    await message.answer("Пожалуйста, используйте меню или команду /start для начала.", reply_markup=main_menu_keyboard())

# --- Веб-сервер для мониторинга ---
async def handle_root(request):
    return web.Response(text="OK")

async def start_webserver():
    app = web.Application()
    app.add_routes([web.get('/', handle_root)])

    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")

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
