# handlers/start.py
# Обработчик команды /start и проверка подписки на канал

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.subs import check_subscription
from config import config

CHANNEL_USERNAME = config["CHANNEL_USERNAME"]
OWNER_ID = config["OWNER_ID"]
SUPPORT_LINK = "https://t.me/PikaPey_support_bot"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id
    name = user.first_name
    username = user.username

    subbed, _ = await check_subscription(uid, context.bot, CHANNEL_USERNAME)

    if uid == OWNER_ID or subbed:
        text = (
            f"⚡️ <b>PikaPey Boost</b>\n\n"
            f"Привет, {username or name}!\n\n"
            f"✅ Ты подписан на канал и можешь выбрать тариф Boost.\n\n"
            f"<i>Быстрый и безопасный доступ к любимым сервисам.</i>"
        )
        keyboard = [
            [InlineKeyboardButton("🚀 Выбрать тариф", callback_data="tariff_menu")],
            [InlineKeyboardButton("💬 Поддержка", url=SUPPORT_LINK)],
        ]
        if uid == OWNER_ID:
            keyboard.append([InlineKeyboardButton("👑 Админ-панель", callback_data="admin_panel")])
    else:
        channel_link = f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}"
        text = (
            f"⚡️ <b>PikaPey Boost</b>\n\n"
            f"👋 Привет, {username or name}!\n\n"
            f"🔒 Для доступа к Boost необходимо подписаться на наш канал.\n\n"
            f"1️⃣ Подпишись 👇\n"
            f"2️⃣ Нажми «✅ Проверить подписку»"
        )
        keyboard = [
            [InlineKeyboardButton("📢 Подписаться на канал", url=channel_link)],
            [InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub")],
            [InlineKeyboardButton("💬 Поддержка", url=SUPPORT_LINK)],
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)

async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    name = query.from_user.first_name

    await query.answer("⏳ Проверяем подписку...")
    subbed, error_msg = await check_subscription(uid, context.bot, CHANNEL_USERNAME)

    if subbed or uid == OWNER_ID:
        await query.edit_message_text(
            f"🎉 <b>Отлично, {name}!</b>\n\nПодписка подтверждена ✅\nТеперь ты можешь выбрать тариф Boost.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Выбрать тариф", callback_data="tariff_menu")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="glavnoe_menu")],
            ])
        )
    else:
        channel_link = f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}"
        await query.edit_message_text(
            f"❌ {error_msg}\n\nУбедись, что ты подписался на канал, и попробуй снова.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Подписаться на канал", url=channel_link)],
                [InlineKeyboardButton("🔄 Проверить снова", callback_data="check_sub")],
            ])
        )

async def glavnoe_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)