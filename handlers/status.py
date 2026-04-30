from telegram import Update
from telegram.ext import ContextTypes

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    days_left = 0
    active_tariff = "Нет активной подписки"
    if days_left > 0:
        text = f"📋 <b>Ваша подписка</b>\n\nТариф: {active_tariff}\nОсталось: {days_left} дн.\n"
    else:
        text = "📋 <b>У вас нет активной подписки.</b>\n\nВыберите тариф в меню: /start"
    await update.message.reply_text(text, parse_mode="HTML")