# PikaPey Boost ⚡️ v1.0
# Главный модуль бота продажи подписок Boost

import json
import logging
import os

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
    ContextTypes,
    filters,
)

CONFIG_PATH = "config.json"

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    config["BOT_TOKEN"] = os.getenv("BOT_TOKEN", config.get("BOT_TOKEN"))
    config["OWNER_ID"] = int(os.getenv("OWNER_ID", config.get("OWNER_ID")))
    return config

config = load_config()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("PikaPeyBoost")

from handlers.start import start, check_subscription_callback, glavnoe_menu
from handlers.offer import offer_callback, agree_offer_callback
from handlers.email_input import get_email_handler
from handlers.tariff import (
    tariff_menu, select_tariff_handler,
    pay_stars_handler, pay_card_handler
)
from handlers.payment import successful_payment_handler
from handlers.admin import admin_panel, admin_callback_handler

if __name__ == "__main__":
    logger.info("="*50)
    logger.info("🚀 PikaPey Boost ⚡️ запуск...")
    logger.info(f"👑 Владелец: {config['OWNER_ID']}")
    logger.info(f"📢 Канал: {config['CHANNEL_USERNAME']}")
    logger.info(f"💳 Stars: {config['USE_STARS']}, ЮKassa: {config['USE_YOOMONEY']}")
    logger.info("="*50)

    proxy_config = config.get("BOT_PROXY", {})
    if proxy_config.get("enabled"):
        proxy_url = proxy_config["url"]
        logger.info(f"🔁 Бот использует прокси: {proxy_url}")
        app = ApplicationBuilder().token(config["BOT_TOKEN"]).proxy(proxy_url).build()
    else:
        app = ApplicationBuilder().token(config["BOT_TOKEN"]).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="^check_sub$"))
    app.add_handler(CallbackQueryHandler(glavnoe_menu, pattern="^glavnoe_menu$"))
    app.add_handler(CallbackQueryHandler(offer_callback, pattern="^offer$"))
    app.add_handler(CallbackQueryHandler(agree_offer_callback, pattern="^agree_offer$"))
    app.add_handler(CallbackQueryHandler(get_email_handler, pattern="^email_enter$"))
    app.add_handler(CallbackQueryHandler(tariff_menu, pattern="^tariff_menu$"))
    app.add_handler(CallbackQueryHandler(select_tariff_handler, pattern="^tariff_select_"))
    app.add_handler(CallbackQueryHandler(pay_stars_handler, pattern="^pay_stars_"))
    app.add_handler(CallbackQueryHandler(pay_card_handler, pattern="^pay_card_"))
    app.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
    app.add_handler(CallbackQueryHandler(admin_callback_handler, pattern="^adm_"))

    app.add_handler(PreCheckoutQueryHandler(lambda u, c: u.pre_checkout_query.answer(True)))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_email_handler))

    app.run_polling()