import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ContextTypes
from config import config

TARIFFS = config["TARIFFS"]
VPN_SURCHARGE = config["VPN_SURCHARGE"]
OWNER_ID = config["OWNER_ID"]

async def tariff_menu(update, context):
    query = update.callback_query
    await query.answer()
    keyboard = []
    for tid, t in TARIFFS.items():
        keyboard.append([InlineKeyboardButton(f"{t['name']} · {t['days']} дн. · от {t['price_proxy']} XTR", callback_data=f"tariff_select_{tid}")])
    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="glavnoe_menu")])
    await query.edit_message_text("⚡️ <b>Выберите тариф</b>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

async def select_tariff_handler(update, context):
    query = update.callback_query
    _, _, tariff_id = query.data.partition("tariff_select_")
    tariff = TARIFFS[tariff_id]
    context.user_data["selected_tariff_id"] = tariff_id

    keyboard = [
        [InlineKeyboardButton("📡 Только прокси", callback_data=f"option_{tariff_id}_proxy")],
        [InlineKeyboardButton("🔐 Только VPN", callback_data=f"option_{tariff_id}_vpn")],
        [InlineKeyboardButton("📡+🔐 Прокси + VPN", callback_data=f"option_{tariff_id}_both")],
        [InlineKeyboardButton("🔙 Назад к тарифам", callback_data="tariff_menu")]
    ]
    await query.edit_message_text(
        f"<b>{tariff['name']}</b> · {tariff['days']} дн.\n\nВыберите, что подключить:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def option_handler(update, context):
    query = update.callback_query
    _, tariff_id, option = query.data.split("_")
    tariff = TARIFFS[tariff_id]
    uid = query.from_user.id

    if option == "proxy":
        price = tariff["price_proxy"]
        vpn_included = False
    elif option == "vpn":
        price = tariff["price_vpn"] + VPN_SURCHARGE
        vpn_included = True
    else:
        price = tariff["price_proxy"] + tariff["price_vpn"] + VPN_SURCHARGE
        vpn_included = True

    context.user_data["tariff_option"] = option
    context.user_data["final_price"] = price
    context.user_data["vpn_included"] = vpn_included

    if uid == OWNER_ID:
        await activate_subscription(update, context, tariff_id, option, days=tariff["days"])
        return

    promo_code = context.user_data.get("promo_code")
    if promo_code:
        promo = config["PROMOCODES"].get(promo_code)
        if promo and promo["duration_days"]:
            price = 0
            days = promo["duration_days"]
            context.user_data["final_price"] = 0
            context.user_data["promo_duration"] = days

    currency = "XTR"
    await query.edit_message_text(
        f"💳 <b>Выбран тариф:</b> {tariff['name']} ({option})\n"
        f"💰 Стоимость: <b>{price} {currency}</b>\n\n"
        "Выберите способ оплаты:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🌟 Telegram Stars ({price} XTR)", callback_data=f"pay_stars_{tariff_id}")],
            [InlineKeyboardButton(f"💳 Карта (ЮKassa) ({price} ₽)", callback_data=f"pay_card_{tariff_id}")],
            [InlineKeyboardButton("🔙 Назад", callback_data="tariff_menu")]
        ])
    )

async def pay_stars_handler(update, context):
    query = update.callback_query
    await query.answer()
    _, _, tariff_id = query.data.partition("pay_stars_")
    await send_invoice(update, context, tariff_id, stars=True)

async def pay_card_handler(update, context):
    query = update.callback_query
    await query.answer()
    _, _, tariff_id = query.data.partition("pay_card_")
    await send_invoice(update, context, tariff_id, stars=False)

async def send_invoice(update, context, tariff_id, stars):
    tariff = TARIFFS[tariff_id]
    uid = update.effective_user.id
    option = context.user_data.get("tariff_option", "proxy")
    price = context.user_data.get("final_price", tariff["price_proxy"])
    currency = "XTR" if stars else "RUB"
    provider_token = "" if stars else config["YOOMONEY_PROVIDER_TOKEN"]

    title = f"PikaPey Boost · {tariff['name']}"
    description = f"{option} · {tariff['days']} дн."
    payload = f"boost_{tariff_id}_{uid}_{option}"
    prices = [LabeledPrice(title, price * 100 if not stars else price)]

    await context.bot.send_invoice(
        chat_id=uid,
        title=title,
        description=description,
        payload=payload,
        provider_token=provider_token,
        currency=currency,
        prices=prices,
        start_parameter="pay",
    )

async def activate_subscription(update, context, tariff_id, option, days):
    user = update.effective_user
    text = f"🎉 <b>Подписка активирована!</b>\n\nТариф: {TARIFFS[tariff_id]['name']}\nОпция: {option}\nСрок: {days} дн.\n"
    if option in ("proxy", "both"):
        text += f"\n📡 <b>Прокси:</b> <code>{config['PROXY_LINK']}</code>"
    if option in ("vpn", "both"):
        text += f"\n🔐 <b>VPN-конфиг:</b> (ссылка в следующем сообщении)"
    await context.bot.send_message(user.id, text, parse_mode="HTML")
    if option in ("vpn", "both"):
        await context.bot.send_message(user.id, f"<code>{config['VPN_LINK']}</code>\n<i>Скопируйте и вставьте в приложение</i>", parse_mode="HTML")