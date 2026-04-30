from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import config

async def offer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "📄 <b>Договор-оферта</b>\n\n" + config["OFFER_TEXT"]
    await query.edit_message_text(text, parse_mode="HTML",
                                reply_markup=InlineKeyboardMarkup([
                                    [InlineKeyboardButton("✅ Согласен", callback_data="agree_offer")],
                                    [InlineKeyboardButton("🔙 Назад", callback_data="glavnoe_menu")]
                                ]))

async def agree_offer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    context.user_data["offer_accepted"] = True
    await query.answer("✅ Принято")
    await query.edit_message_text("📧 Введите ваш email для чеков (или нажмите /skip):",
                                parse_mode="HTML",
                                reply_markup=InlineKeyboardMarkup([
                                    [InlineKeyboardButton("Пропустить", callback_data="skip_email")]
                                ]))
    context.user_data["awaiting_email"] = True