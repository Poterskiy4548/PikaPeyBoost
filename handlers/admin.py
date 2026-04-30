# handlers/admin.py
# Админ-панель для управления тарифами (пока заглушка)

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot import config

OWNER_ID = config["OWNER_ID"]

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != OWNER_ID:
        await query.answer("❌ Нет доступа", show_alert=True)
        return
    await query.edit_message_text(
        "👑 <b>Админ-панель PikaPey Boost</b>\n\nФункции будут добавлены позже.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Главное меню", callback_data="glavnoe_menu")]
        ])
    )

async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Функция в разработке")