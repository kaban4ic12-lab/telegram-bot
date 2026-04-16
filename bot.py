import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

logging.basicConfig(level=logging.INFO)

TOKEN = "8738794640:AAGF2-7dZPtcX2dJuBisFwGmg7W51eZuSmA"
ADMIN_ID = 1264199887
USD_TO_UAH = 45

# =========================
# ✏️ РЕДАГУЄШ ВСЕ ТУТ
# =========================
SHOP = {
    "start_text": """Если ты здесь ты в темe 
    Контент 18+ без фильтров 
    Никакого фейка-только real 
    Сливи ТТ блогерш, ДП, школьници 
    Строго 18+ контент без блюра""",

    "info_text": """Здесь ти сможеш приобрести ексклюзивние видео Есть 3 категории видео (про категории ниже ) 
    За приобретения 1 категории у вас откоеться доступ к тг каналу в котором будет собрано слив 1 из блогерш 
    там будет много видео как и на 1мин так и на 20мин 
    
    За приобретения 2категории у вас откриваеться доступ к тг канало в котором будет собрано сливи 4 блогерш 
    видео также могут отличаться по времени (более 40 бидео ) 
    
    За приобретения випки тоесть 3 категории у вас будет доступ ко всем видео блогерш ( более 10 разних блогерш )
     также сливи школьниц , ДП (+ доступ к тгк 1 и 2 категории)""",
    "about_text": """Информация про бота 
    Здесь ти преобретаеш все анонимно любая информация о тебе остаёться строго между нами 
    оплата и видача материала проходит моментально бот полностю легальний и безопасний будем
     ради сотрудничать с вами """,

    "payment_text": """💳 Реквизиты

💳 Карта:
4874070020502314

💰 Крипто кошелек:
UQCXQ5gKftBpbd8SToXynLboUHtcErln5YTjcfnIrqBSXWfx""",

    "start_image": "https://i.postimg.cc/wTHVjrJJ/photo-2026-04-14-18-53-26.jpg",

    "products": [
        {
            "id": "p1",
            "name": "🎬 Материал 1",
            "price": 1,
            "desc": "📦 1 видео",
            "image": "https://i.postimg.cc/8502SSsn/photo-2026-04-09-20-32-48.jpg",
            "link": "https://t.me/+LCM8hn7QwXtlNWIy"
        },
        {
            "id": "p2",
            "name": "🎬 Материал 2",
            "price": 2,
            "desc": "📦 3 видео",
            "image": "https://i.postimg.cc/wBfq7n7Y/photo-2026-04-14-18-52-58.jpg",
            "link": "https://t.me/+WyZVj-R7RO1kMjY6"
        },
        {
            "id": "p3",
            "name": "👑 Полный доступ",
            "price": 5,
            "desc": "📦 Все видео",
            "image": "https://i.postimg.cc/HW7YkZHW/photo-2026-04-14-18-53-41.jpg",
            "link": "https://t.me/+qwy6GO2zT2hkNzcy"
        }
    ]
}

payments = {}
pending = {}
purchased = {}

# ================= МЕНЮ =================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Каталог", callback_data="catalog")],
        [InlineKeyboardButton("📂 Мои покупки", callback_data="my")],
        [
            InlineKeyboardButton("ℹ️ Информация", callback_data="info"),
            InlineKeyboardButton("📦 О нас", callback_data="about")
        ]
    ])

def back_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Назад", callback_data="back")]
    ])

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=SHOP["start_image"],
        caption=SHOP["start_text"],
        reply_markup=main_menu()
    )

# ================= КАТАЛОГ =================
async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = []

    for product in SHOP["products"]:
        price_uah = product["price"] * USD_TO_UAH

        keyboard.append([
            InlineKeyboardButton(
                f"{product['name']} ({price_uah} грн / {product['price']} USDT)",
                callback_data=product["id"]
            )
        ])

    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back")])

    await query.message.reply_text(
        "🛒 Выбери товар:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= ТОВАР =================
async def product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    product = next((p for p in SHOP["products"] if p["id"] == query.data), None)

    if not product:
        await query.message.reply_text("❌ Ошибка товара")
        return

    payments[user_id] = product["id"]

    price_uah = product["price"] * USD_TO_UAH

    await query.message.reply_photo(
        photo=product["image"],
        caption=f"""{product['name']}

{product['desc']}

💳 {price_uah} грн
💰 {product['price']} USDT

{SHOP['payment_text']}""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📤 Я оплатил", callback_data="pay")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="catalog")]
        ])
    )

# ================= ОПЛАТА =================
async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id in payments:
        pending[user_id] = payments[user_id]

    await query.message.reply_text(
        "📸 Відправ скрін оплати і чекай підтвердження",
        reply_markup=back_button()
    )

# ================= ФОТО =================
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in pending:
        return

    product_id = pending[user_id]
    product = next((p for p in SHOP["products"] if p["id"] == product_id), None)

    if not product:
        return

    await context.bot.send_photo(
        ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=f"💸 Оплата\nID: {user_id}\nТовар: {product['name']}",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Подтвердить", callback_data=f"ok_{user_id}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"no_{user_id}")
            ]
        ])
    )

    await update.message.reply_text(
        "⏳ Ожидай подтверждение",
        reply_markup=back_button()
    )

# ================= ПІДТВЕРДЖЕННЯ =================
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = int(query.data.split("_")[1])

    if user_id not in pending:
        await query.message.reply_text("❌ Пользователь не найден")
        return

    product_id = pending[user_id]
    product = next((p for p in SHOP["products"] if p["id"] == product_id), None)

    if not product:
        return

    purchased.setdefault(user_id, []).append(product_id)

    # ✅ ВИДАЧА ТОВАРУ
    await context.bot.send_message(
        user_id,
        f"✅ Оплата подтверждена!\n\n🎬 Ссылка:\n{product['link']}"
    )

    pending.pop(user_id, None)
    payments.pop(user_id, None)

    await query.message.reply_text("✅ Подтверждено")

# ================= ВІДХИЛЕННЯ =================
async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = int(query.data.split("_")[1])

    await context.bot.send_message(
        user_id,
        "❌ Оплата отклонена\n\nНажми /start для возврата в меню"
    )

    pending.pop(user_id, None)
    payments.pop(user_id, None)

    await query.message.reply_text("❌ Отклонено")

# ================= МОИ ПОКУПКИ =================
async def my(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in purchased:
        await query.message.reply_text("📂 У тебя нет покупок", reply_markup=back_button())
        return

    text = "📂 Твои покупки:\n\n"
    for pid in purchased[user_id]:
        product = next((p for p in SHOP["products"] if p["id"] == pid), None)
        if product:
            text += f"{product['name']}\n{product['link']}\n\n"

    await query.message.reply_text(text, reply_markup=back_button())

# ================= ІНФО =================
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(SHOP["info_text"], reply_markup=back_button())

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(SHOP["about_text"], reply_markup=back_button())

# ================= НАЗАД =================
async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_photo(
        photo=SHOP["start_image"],
        caption=SHOP["start_text"],
        reply_markup=main_menu()
    )

# ================= ЗАПУСК =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(catalog, pattern="^catalog$"))
    app.add_handler(CallbackQueryHandler(product, pattern="^p[0-9]+$"))
    app.add_handler(CallbackQueryHandler(pay, pattern="^pay$"))
    app.add_handler(CallbackQueryHandler(confirm, pattern="^ok_"))
    app.add_handler(CallbackQueryHandler(reject, pattern="^no_"))
    app.add_handler(CallbackQueryHandler(my, pattern="^my$"))
    app.add_handler(CallbackQueryHandler(info, pattern="^info$"))
    app.add_handler(CallbackQueryHandler(about, pattern="^about$"))
    app.add_handler(CallbackQueryHandler(back, pattern="^back$"))

    app.add_handler(MessageHandler(filters.PHOTO, photo))

    print("🚀 Бот работает стабильно и без багов")
    app.run_polling()

if __name__ == "__main__":
    main()