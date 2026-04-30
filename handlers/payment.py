# handlers/payment.py
# Обработка успешного платежа, чек в чат и на email

from telegram import Update
from telegram.ext import ContextTypes
from config import config
from services.email_sender import send_email

TARIFFS = config["TARIFFS"]

async def successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    payment = update.message.successful_payment
    tariff_id = context.user_data.get("selected_tariff")
    email = context.user_data.get("user_email")

    tariff = TARIFFS.get(tariff_id)
    if not tariff:
        await update.message.reply_text("⚠️ Ошибка: тариф не найден. Обратитесь в поддержку.")
        return

    receipt = (
        f"🧾 <b>Чек об оплате</b>\n\n"
        f"Тариф: <b>{tariff['name']}</b>\n"
        f"Сумма: {payment.total_amount // 100 if payment.currency == 'RUB' else payment.total_amount} {payment.currency}\n"
        f"Дата: {update.message.date.strftime('%d.%m.%Y %H:%M')}\n"
        f"ID транзакции: <code>{payment.telegram_payment_charge_id}</code>\n\n"
        f"<i>Доступ активен на {tariff['days']} дней.</i>"
    )
    await update.message.reply_text(receipt, parse_mode="HTML")

    if email:
        subject = f"Чек PikaPey Boost: {tariff['name']}"
        body = (
            f"Тариф: {tariff['name']}\n"
            f"Сумма: {payment.total_amount // 100 if payment.currency == 'RUB' else payment.total_amount} {payment.currency}\n"
            f"Дата: {update.message.date.strftime('%d.%m.%Y %H:%M')}\n"
            f"ID транзакции: {payment.telegram_payment_charge_id}\n"
        )
        await send_email(email, subject, body)