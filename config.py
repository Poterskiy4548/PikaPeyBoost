# config.py
# Загрузка конфигурации из JSON и переменных окружения

import json
import os

CONFIG_PATH = "config.json"

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    config["BOT_TOKEN"] = os.getenv("BOT_TOKEN", config.get("BOT_TOKEN"))
    config["OWNER_ID"] = int(os.getenv("OWNER_ID", config.get("OWNER_ID")))
    return config

config = load_config()