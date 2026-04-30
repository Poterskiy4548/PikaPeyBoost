from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.subs import check_subscription
from config import config

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id
    name = user.first_name or user.username or ""

    subbed, _ = await check_subscription(uid, context.bot, config["CHANNEL_USERNAME"])

    if uid == config["OWNER_ID"] or subbed:
        if not context.user_data.get("offer_accepted"):
            await show_offer(update, context)
            return
        await show_main(update, context, name, uid == config["OWNER_ID"])
    else:
        await show_subscribe(update, context, name)

async def show_offer(update, context):
    text = (
        "📄 <b>Пользовательское соглашение</b>\n\n"
        f"{config['OFFER_TEXT']}\n\n"
        "Нажмите «Согласен» для продолжения."
    )
    keyboard = [[InlineKeyboardButton("✅ Согласен", callback_data="agree_offer")]]
    await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_main(update, context, name, is_owner):
    text = (
        "⚡️ <b>PikaPey Boost</b> — ваш доступ без границ\n\n"
        f"Добро пожаловать, {name}!\n\n"
        "Выберите тариф и опции ниже 👇"
    )
    keyboard = [
        [InlineKeyboardButton("🚀 Выбрать тариф", callback_data="tariff_menu")],
        [InlineKeyboardButton("📋 Статус подписки", callback_data="status")],
        [InlineKeyboardButton("💬 Поддержка", url="https://t.me/PikaPey_support_bot")],
    ]
    if is_owner:
        keyboard.append([InlineKeyboardButton("👑 Админ-панель", callback_data="admin_panel")])
    await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_subscribe(update, context, name):
    channel = config["CHANNEL_USERNAME"]
    link = f"https://t.me/{channel.lstrip('@')}"
    text = (
        "🔒 <b>Доступ ограничен</b>\n\n"
        f"Привет, {name}! Чтобы пользоваться Boost, подпишитесь на наш канал.\n\n"
        "1. Подпишитесь\n"
        "2. Нажмите «Проверить подписку»"
    )
    keyboard = [
        [InlineKeyboardButton("📢 Подписаться", url=link)],
        [InlineKeyboardButton("✅ Проверить", callback_data="check_sub")],
        [InlineKeyboardButton("💬 Поддержка", url="https://t.me/PikaPey_support_bot")],
    ]
    await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

async def check_subscription_callback(update, context):
    query = update.callback_query
    uid = query.from_user.id
    name = query.from_user.first_name
    await query.answer()
    subbed, err = await check_subscription(uid, context.bot, config["CHANNEL_USERNAME"])
    if subbed or uid == config["OWNER_ID"]:
        await query.edit_message_text("✅ Подписка подтверждена! Теперь вы можете выбрать тариф.",
                                      parse_mode="HTML",
                                      reply_markup=InlineKeyboardMarkup([
                                          [InlineKeyboardButton("🚀 Перейти к тарифам", callback_data="tariff_menu")]
                                      ]))
    else:
        await query.edit_message_text(f"❌ {err}\nПопробуйте снова.",
                                      parse_mode="HTML",
                                      reply_markup=InlineKeyboardMarkup([
                                          [InlineKeyboardButton("🔄 Проверить", callback_data="check_sub")]
                                      ]))

async def glavnoe_menu(update, context):
    await start(update, context)