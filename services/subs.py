# services/subs.py
# Проверка подписки пользователя на канал

async def check_subscription(user_id: int, bot, channel_username: str) -> tuple[bool, str]:
    """Возвращает (подписан_ли, сообщение_об_ошибке)."""
    if not channel_username:
        return False, "❌ Канал не указан."
    try:
        chat = await bot.get_chat(channel_username)
        member = await bot.get_chat_member(chat.id, user_id)
        if member.status in ("member", "administrator", "creator"):
            return True, ""
        else:
            return False, "🔒 Ты не подписан на канал."
    except Exception as e:
        return False, f"⚠️ Не удалось проверить подписку."