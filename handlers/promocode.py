from telegram import Update
from telegram.ext import ContextTypes
from config import config

PROMOCODES = config.get("PROMOCODES", {})

async def promocode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip().upper()

    if text in PROMOCODES:
        promo = PROMOCODES[text]
        if uid in promo["used_by"]:
            await update.message.reply_text("⚠️ Вы уже использовали этот промокод.")
            return
        if len(promo["used_by"]) >= promo["max_uses"]:
            await update.message.reply_text("⚠️ Промокод больше недействителен.")
            return

        context.user_data["promo_code"] = text
        context.user_data["promo_days"] = promo["duration_days"]
        await update.message.reply_text(
            f"🎉 Промокод активирован! Вы получите <b>{promo['duration_days']} дней</b> доступа к любому тарифу.\n"
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
        return