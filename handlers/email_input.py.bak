import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

async def get_email_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_email"):
        return

    uid = update.effective_user.id
    text = update.message.text.strip()

    if re.match(EMAIL_REGEX, text):
        context.user_data["user_email"] = text
        context.user_data["awaiting_email"] = False
        await update.message.reply_text(
            f"✅ Email <b>{text}</b> сохранён.\n\nТеперь вы можете выбрать тариф Boost.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Выбрать тариф", callback_data="tariff_menu")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="glavnoe_menu")],
            ])
        )
    else:
        await update.message.reply_text(
            "⚠️ Некорректный email. Пожалуйста, введите правильный адрес.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="glavnoe_menu")]
            ])
        )