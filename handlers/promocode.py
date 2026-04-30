from telegram import Update
from telegram.ext import ContextTypes
from config import config

PROMOCODES = config.get("PROMOCODES", {})

async def enter_promocode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["awaiting_promocode"] = True
    await query.edit_message_text(
        "🎟 <b>Введите ваш промокод</b>\n\n"
        "Просто отправьте код текстом.\n"
        "Если промокод верен, вы получите бесплатный доступ к выбранному тарифу.",
        parse_mode="HTML"
    )

async def promocode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Реагируем только если бот ждёт промокод
    if not context.user_data.get("awaiting_promocode"):
        return

    uid = update.effective_user.id
    text = update.message.text.strip().upper()
    context.user_data["awaiting_promocode"] = False

    if text in PROMOCODES:
        promo = PROMOCODES[text]
        if uid in promo.get("used_by", []):
            await update.message.reply_text("⚠️ Вы уже использовали этот промокод.")
            return
        if len(promo.get("used_by", [])) >= promo["max_uses"]:
            await update.message.reply_text("⚠️ Промокод больше недействителен.")
            return

        context.user_data["promo_code"] = text
        context.user_data["promo_days"] = promo["duration_days"]
        await update.message.reply_text(
            f"🎉 Промокод активирован! Вы получите <b>{promo['duration_days']} дней</b> доступа.\n"
            "Теперь выберите тариф в меню.",
            parse_mode="HTML"
        )
        promo["used_by"].append(uid)
        try:
            import json
            with open("config.json", "w") as f:
                json.dump(config, f, indent=2)
        except Exception:
            pass
    else:
        await update.message.reply_text("❌ Неверный промокод. Попробуйте ещё раз или нажмите /start.")