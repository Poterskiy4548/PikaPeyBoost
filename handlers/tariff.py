# handlers/tariff.py
# Выбор тарифа и формирование счёта

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ContextTypes
from bot import config

TARIFFS = config["TARIFFS"]
USE_STARS = config["USE_STARS"]
USE_YOOMONEY = config["USE_YOOMONEY"]
YOOMONEY_PROVIDER_TOKEN = config.get("YOOMONEY_PROVIDER_TOKEN", "")

async def tariff_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список тарифов."""
    query = update.callback_query
    await query.answer()

    keyboard = []
    for tariff_id, tariff in TARIFFS.items():
        name = tariff["name"]
        price = tariff["price_stars"] if USE_STARS else tariff["price_rub"]
        currency = "XTR" if USE_STARS else "₽"
        days = tariff["days"]
        desc = tariff.get("description", "")
        keyboard.append([
            InlineKeyboardButton(
                f"{name} — {price} {currency} / {days} дн.",
                callback_data=f"tariff_select_{tariff_id}"
            )
        ])

    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="glavnoe_menu")])

    await query.edit_message_text(
        "⚡️ <b>Выберите тариф Boost</b>\n\n"
        "После выбора вам будет предложен способ оплаты.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def select_tariff_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор конкретного тарифа и предлагает способ оплаты."""
    query = update.callback_query
    await query.answer()
    _, _, tariff_id = query.data.partition("tariff_select_")
    tariff = TARIFFS.get(tariff_id)
    if not tariff:
        await query.answer("Тариф не найден.", show_alert=True)
        return

    context.user_data["selected_tariff"] = tariff_id

    # Предлагаем способ оплаты, если оба включены; иначе сразу счёт
    if USE_STARS and USE_YOOMONEY:
        await query.edit_message_text(
            f"💳 <b>Способ оплаты</b>\n\nТариф: <b>{tariff['name']}</b>\nСумма: {tariff['price_stars']} XTR или {tariff['price_rub']} ₽\n\nВыберите удобный способ:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🌟 Telegram Stars", callback_data=f"pay_stars_{tariff_id}")],
                [InlineKeyboardButton("💳 Банковская карта (ЮKassa)", callback_data=f"pay_card_{tariff_id}")],
                [InlineKeyboardButton("🔙 Назад к тарифам", callback_data="tariff_menu")],
            ])
        )
    elif USE_STARS:
        await send_invoice(update, context, tariff_id, stars=True)
    elif USE_YOOMONEY:
        await send_invoice(update, context, tariff_id, stars=False)

async def pay_stars_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выставление счёта в Stars."""
    query = update.callback_query
    await query.answer()
    _, _, tariff_id = query.data.partition("pay_stars_")
    await send_invoice(update, context, tariff_id, stars=True)

async def pay_card_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выставление счёта через ЮKassa."""
    query = update.callback_query
    await query.answer()
    _, _, tariff_id = query.data.partition("pay_card_")
    await send_invoice(update, context, tariff_id, stars=False)

async def send_invoice(update, context, tariff_id, stars):
    """Общая функция отправки счёта."""
    tariff = TARIFFS[tariff_id]
    uid = update.effective_user.id
    name = tariff["name"]
    desc = tariff.get("description", "Доступ Boost")
    price = tariff["price_stars"] if stars else tariff["price_rub"]
    currency = "XTR" if stars else "RUB"
    payload = f"boost_{tariff_id}_{uid}"
    provider_token = "" if stars else YOOMONEY_PROVIDER_TOKEN

    prices = [LabeledPrice(name, price * 100 if not stars else price)]  # в копейках для RUB

    await context.bot.send_invoice(
        chat_id=uid,
        title="PikaPey Boost",
        description=desc,
        payload=payload,
        provider_token=provider_token,
        currency=currency,
        prices=prices
    )