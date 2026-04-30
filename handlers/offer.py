# handlers/offer.py
# Показ оферты и фиксация согласия

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot import config

OFFER_TEXT = config.get("OFFER_TEXT", "Договор-оферта PikaPey Boost.\n\nУсловия предоставления услуг...\n\nПродолжая, вы соглашаетесь с условиями.")

async def offer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает текст оферты и кнопку 'Согласен'."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        f"📄 <b>Договор-оферта</b>\n\n{OFFER_TEXT}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Я прочитал и согласен", callback_data="agree_offer")],
            [InlineKeyboardButton("🔙 Назад", callback_data="glavnoe_menu")],
        ])
    )

async def agree_offer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Фиксирует согласие и запрашивает email."""
    query = update.callback_query
    uid = query.from_user.id
    # Здесь потом можно сохранить в БД
    context.user_data["offer_accepted"] = True
    await query.answer("✅ Согласие принято")
    await query.edit_message_text(
        "📧 <b>Введите ваш email для получения чека</b>\n\n"
        "На этот адрес будет отправлен чек после оплаты.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Назад", callback_data="glavnoe_menu")]
        ])
    )
    context.user_data["awaiting_email"] = True