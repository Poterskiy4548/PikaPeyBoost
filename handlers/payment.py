from telegram import Update
from telegram.ext import ContextTypes
from config import config
from handlers.tariff import activate_subscription

async def successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    payment = update.message.successful_payment
    _, tariff_id, uid_str, option = payment.invoice_payload.split("_")
    tariff = config["TARIFFS"][tariff_id]
    email = context.user_data.get("user_email", "")

    await activate_subscription(update, context, tariff_id, option, days=tariff["days"])

    receipt = (
        f"🧾 <b>Чек об оплате</b>\n\n"
        f"Тариф: {tariff['name']} ({option})\n"
        f"Сумма: {payment.total_amount // 100 if payment.currency == 'RUB' else payment.total_amount} {payment.currency}\n"
        f"ID: <code>{payment.telegram_payment_charge_id}</code>\n\n"
        f"<i>Спасибо, что выбрали PikaPey Boost!</i>"
    )
    await update.message.reply_text(receipt, parse_mode="HTML")

    if email:
        from services.email_sender import send_email
        await send_email(email, "Чек PikaPey Boost", receipt)