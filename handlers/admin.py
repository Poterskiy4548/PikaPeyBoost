import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext
from config import config

OWNER_ID = config["OWNER_ID"]
SUBSCRIPTIONS_FILE = "subscriptions.json"

# ---------- вспомогательные функции ----------
def load_subscriptions():
    if not os.path.exists(SUBSCRIPTIONS_FILE):
        return []
    with open(SUBSCRIPTIONS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def save_subscriptions(subs):
    with open(SUBSCRIPTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(subs, f, ensure_ascii=False, indent=2)

def save_config():
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# ---------- главное меню админа ----------
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != OWNER_ID:
        await query.answer("❌ Нет доступа", show_alert=True)
        return

    keyboard = [
        [InlineKeyboardButton("📊 Тарифы", callback_data="adm_tariffs")],
        [InlineKeyboardButton("🎟 Промокоды", callback_data="adm_promos")],
        [InlineKeyboardButton("👥 Подписки", callback_data="adm_subscriptions")],
        [InlineKeyboardButton("🔗 Ссылки", callback_data="adm_links")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="glavnoe_menu")],
    ]
    await query.edit_message_text(
        "👑 <b>Админ-панель PikaPey Boost</b>\n\nВыберите раздел:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------- TARIFFS ----------
async def adm_tariffs_menu(update, context):
    query = update.callback_query
    await query.answer()
    keyboard = []
    for t_id, t in config["TARIFFS"].items():
        keyboard.append([InlineKeyboardButton(f"✏️ {t['name']} ({t['price_proxy']} XTR)", callback_data=f"adm_edittariff_{t_id}")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")])
    await query.edit_message_text("📊 <b>Редактирование тарифов</b>\nВыберите тариф:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

async def adm_edit_tariff(update, context):
    query = update.callback_query
    await query.answer()
    _, _, t_id = query.data.partition("adm_edittariff_")
    tariff = config["TARIFFS"][t_id]
    context.user_data["admin_edit_tariff"] = t_id
    await query.edit_message_text(
        f"✏️ <b>{tariff['name']}</b>\n\n"
        f"1. Цена прокси: {tariff['price_proxy']} XTR\n"
        f"2. Цена VPN: {tariff['price_vpn']} XTR\n"
        f"3. Дней: {tariff['days']}\n"
        f"4. Описание: {tariff.get('description','')}\n\n"
        "Что меняем? Отправьте цифру или новое значение.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="adm_tariffs")]])
    )
    context.user_data["admin_await"] = "tariff_field"

# Обработчик текстовых команд админа
async def admin_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid != OWNER_ID:
        return
    if not context.user_data.get("admin_await"):
        return

    action = context.user_data["admin_await"]
    text = update.message.text.strip()
    t_id = context.user_data.get("admin_edit_tariff")
    tariff = config["TARIFFS"][t_id]

    if action == "tariff_field":
        if text == "1":
            context.user_data["admin_await"] = "tariff_price_proxy"
            await update.message.reply_text("Введите новую цену прокси (только число):")
        elif text == "2":
            context.user_data["admin_await"] = "tariff_price_vpn"
            await update.message.reply_text("Введите новую цену VPN:")
        elif text == "3":
            context.user_data["admin_await"] = "tariff_days"
            await update.message.reply_text("Введите количество дней:")
        elif text == "4":
            context.user_data["admin_await"] = "tariff_desc"
            await update.message.reply_text("Введите новое описание:")
        else:
            await update.message.reply_text("Неверный выбор. Нажмите /admin.")
    elif action.startswith("tariff_"):
        field = action[7:]  # price_proxy, price_vpn, days, desc
        if field in ["price_proxy", "price_vpn", "days"]:
            try:
                value = int(text)
                tariff[field] = value
                save_config()
                await update.message.reply_text(f"✅ Поле {field} обновлено.")
            except:
                await update.message.reply_text("❌ Нужно число.")
        elif field == "desc":
            tariff["description"] = text
            save_config()
            await update.message.reply_text("✅ Описание обновлено.")
        context.user_data["admin_await"] = None
        # Вернёмся к меню тарифов
        await admin_panel(update, context)

# ---------- PROMOCODES ----------
async def adm_promos_menu(update, context):
    query = update.callback_query
    await query.answer()
    promos = config.get("PROMOCODES", {})
    keyboard = []
    for code, data in promos.items():
        used = len(data.get("used_by", []))
        max_u = data["max_uses"]
        keyboard.append([InlineKeyboardButton(f"{code} ({used}/{max_u})", callback_data=f"adm_promodel_{code}")])
    keyboard.append([InlineKeyboardButton("➕ Добавить промокод", callback_data="adm_addpromo")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")])
    await query.edit_message_text("🎟 <b>Промокоды</b>\nВыберите для удаления или добавьте новый:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

async def adm_add_promo(update, context):
    query = update.callback_query
    await query.answer()
    context.user_data["admin_await"] = "promo_add"
    await query.edit_message_text("Введите новый промокод в формате:\n<code>КОД ДНИ МАКС_ИСПОЛЬЗОВАНИЙ</code>\nПример: <code>SUPER 7 50</code>", parse_mode="HTML")

async def adm_delete_promo(update, context):
    query = update.callback_query
    await query.answer()
    _, _, code = query.data.partition("adm_promodel_")
    if code in config.get("PROMOCODES", {}):
        del config["PROMOCODES"][code]
        save_config()
        await query.answer("Промокод удалён", show_alert=True)
    await adm_promos_menu(update, context)

# Обработчик текста для добавления промокода
async def admin_promo_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid != OWNER_ID or context.user_data.get("admin_await") != "promo_add":
        return
    parts = update.message.text.strip().split()
    if len(parts) < 2:
        await update.message.reply_text("Неверный формат. Пример: <code>SUPER 7 50</code>", parse_mode="HTML")
        return
    code = parts[0].upper()
    days = int(parts[1])
    max_uses = int(parts[2]) if len(parts) > 2 else 100
    config.setdefault("PROMOCODES", {})[code] = {
        "duration_days": days,
        "max_uses": max_uses,
        "used_by": []
    }
    save_config()
    context.user_data["admin_await"] = None
    await update.message.reply_text(f"✅ Промокод {code} добавлен.")
    # Вернёмся в админку
    await admin_panel_from_text(update, context)

async def admin_panel_from_text(update, context):
    await context.bot.send_message(update.effective_user.id, "Возвращаемся в админ-панель:", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 Админ-панель", callback_data="admin_panel")]
    ]))

# ---------- SUBSCRIPTIONS ----------
async def adm_subscriptions(update, context):
    query = update.callback_query
    await query.answer()
    subs = load_subscriptions()
    if not subs:
        text = "👥 <b>Активных подписок нет.</b>"
    else:
        text = "👥 <b>Активные подписки:</b>\n\n"
        for s in subs[-10:]:  # последние 10
            text += f"• <code>{s['user_id']}</code> — {s['tariff']} ({s['option']}) до {s['expiry']}\n"
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]]
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

# ---------- LINKS ----------
async def adm_links_menu(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        f"🔗 <b>Текущие ссылки</b>\n\n"
        f"Прокси: <code>{config['PROXY_LINK']}</code>\n"
        f"VPN: <code>{config['VPN_LINK']}</code>\n\n"
        "Что меняем?",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📡 Прокси", callback_data="adm_link_proxy")],
            [InlineKeyboardButton("🔐 VPN", callback_data="adm_link_vpn")],
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")],
        ])
    )

async def adm_edit_link(update, context):
    query = update.callback_query
    await query.answer()
    _, _, link_type = query.data.partition("adm_link_")
    context.user_data["admin_await"] = f"link_{link_type}"
    await query.edit_message_text(f"Введите новую ссылку для {link_type}:")

async def admin_link_text(update, context):
    uid = update.effective_user.id
    if uid != OWNER_ID:
        return
    action = context.user_data.get("admin_await")
    if not action or not action.startswith("link_"):
        return
    link_type = action[5:]
    config[f"{link_type.upper()}_LINK"] = update.message.text.strip()
    save_config()
    context.user_data["admin_await"] = None
    await update.message.reply_text(f"✅ Ссылка {link_type} обновлена.")
    await admin_panel_from_text(update, context)

# ---------- диспетчер callback админа ----------
async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "adm_tariffs":
        await adm_tariffs_menu(update, context)
    elif data.startswith("adm_edittariff_"):
        await adm_edit_tariff(update, context)
    elif data == "adm_promos":
        await adm_promos_menu(update, context)
    elif data.startswith("adm_promodel_"):
        await adm_delete_promo(update, context)
    elif data == "adm_addpromo":
        await adm_add_promo(update, context)
    elif data == "adm_subscriptions":
        await adm_subscriptions(update, context)
    elif data == "adm_links":
        await adm_links_menu(update, context)
    elif data.startswith("adm_link_"):
        await adm_edit_link(update, context)
    else:
        await query.answer("Неизвестная команда")