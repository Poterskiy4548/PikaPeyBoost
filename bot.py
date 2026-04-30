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

# Настройки из JSON (с возможностью переопределения через переменные окружения)
CONFIG_PATH = "config.json"

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    # Переопределяем BOT_TOKEN из переменной окружения, если она задана
    config["BOT_TOKEN"] = os.getenv("BOT_TOKEN", config.get("BOT_TOKEN"))
    config["OWNER_ID"] = int(os.getenv("OWNER_ID", config.get("OWNER_ID")))
    return config

config = load_config()

# Логирование в стиле PikaPey
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("PikaPeyBoost")

# Импортируем обработчики (будут созданы далее)
from handlers.start import start, check_subscription_callback, glavnoe_menu
from handlers.offer import offer_callback, agree_offer_callback
from handlers.email_input import get_email_handler
from handlers.tariff import tariff_menu, select_tariff_handler
from handlers.payment import successful_payment_handler
from handlers.admin import admin_panel, admin_callback_handler

# ==============================
# ТОЧКА ВХОДА
# ==============================
if __name__ == "__main__":
    logger.info("="*50)
    logger.info("🚀 PikaPey Boost ⚡️ запуск...")
    logger.info(f"👑 Владелец: {config['OWNER_ID']}")
    logger.info(f"📢 Канал: {config['CHANNEL_USERNAME']}")
    logger.info(f"💳 Stars: {config['USE_STARS']}, ЮKassa: {config['USE_YOOMONEY']}")
    logger.info("="*50)

    app = ApplicationBuilder().token(config["BOT_TOKEN"]).build()

    # Регистрируем обработчики команд
    app.add_handler(CommandHandler("start", start))

    # Обработчики callback-кнопок (общий диспетчер)
    app.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="^check_sub$"))
    app.add_handler(CallbackQueryHandler(glavnoe_menu, pattern="^glavnoe_menu$"))
    app.add_handler(CallbackQueryHandler(offer_callback, pattern="^offer$"))
    app.add_handler(CallbackQueryHandler(agree_offer_callback, pattern="^agree_offer$"))
    app.add_handler(CallbackQueryHandler(get_email_handler, pattern="^email_enter$"))
    app.add_handler(CallbackQueryHandler(tariff_menu, pattern="^tariff_menu$"))
    app.add_handler(CallbackQueryHandler(select_tariff_handler, pattern="^tariff_select_"))
    app.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
    app.add_handler(CallbackQueryHandler(admin_callback_handler, pattern="^adm_"))

    # Обработчик предпроверки платежа (обязателен для Stars)
    app.add_handler(PreCheckoutQueryHandler(lambda u, c: u.pre_checkout_query.answer(True)))

    # Обработчик успешного платежа
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_handler))

    # Обработчик текстовых сообщений (для ввода email)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_email_handler))

    # Запуск
    app.run_polling()