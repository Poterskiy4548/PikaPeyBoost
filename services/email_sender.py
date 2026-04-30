# services/email_sender.py
# Отправка email через SendGrid API (пока заглушка)

import logging

logger = logging.getLogger("PikaPeyBoost.email")

async def send_email(to_email: str, subject: str, body: str):
    """Отправляет письмо. Пока выводит в лог."""
    logger.info(f"Отправка email на {to_email}: тема='{subject}'")
    # Здесь будет реальная отправка через SendGrid/SMTP
    return True